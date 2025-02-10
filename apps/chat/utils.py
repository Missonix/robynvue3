import uuid
from robyn import Request, Robyn, WebSocket
import random
import asyncio
from model.base import AiChat
import json
import time
from core.database import AsyncSessionLocal
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit
from apps.chat import crud
from core.auth import TokenService
from core.cache import Cache

def generate_session_id():
    '''
    生成会话id
    '''
    return str(uuid.uuid4())


# @error_handler
# @request_logger
# @auth_required
def ai_websocket(app: Robyn):
    websocket = WebSocket(app, "/ws")

    active_ws = {}  # 保存 WebSocket 实例和对应的状态
    HEARTBEAT_INTERVAL = 30  # 心跳间隔30秒
    HEARTBEAT_TIMEOUT = 60   # 超时时间60秒

    async def heartbeat_checker():
        """心跳检测后台任务"""
        while True:
            now = time.time()
            to_remove = []
            
            for ws_id, data in active_ws.items():
                # 检查心跳超时
                if now - data["last_activity"] > HEARTBEAT_TIMEOUT:
                    print(f"连接 {ws_id} 心跳超时，关闭连接")
                    to_remove.append(ws_id)
                    await data["ws"].async_close()
                    
                # 发送心跳ping
                elif now - data["last_ping"] > HEARTBEAT_INTERVAL:
                    try:
                        # 确保心跳包包含所有必要字段
                        await data["ws"].async_send_to(ws_id, json.dumps({
                            "type": "heartbeat_ping",
                            "timestamp": now,
                            "message": "ping"  # 添加验证字段
                        }))
                        data["last_ping"] = now
                        data["waiting_pong"] = True
                    except Exception as e:
                        print(f"发送心跳失败: {str(e)}")
                        to_remove.append(ws_id)
            
            # 清理失效连接
            for ws_id in to_remove:
                del active_ws[ws_id]
            
            await asyncio.sleep(5)  # 每5秒检查一次

    @websocket.on("connect")
    async def handle_connect(ws):
        token = ws.query_params.get("token") 
        if not TokenService.verify_token(token):
            await ws.async_send_to(ws.id, json.dumps({
                "type": "error",
                "content": f"token验证失败，请重新登录！"
            }))
            await ws.async_close()
            return ""
        
        user_data = TokenService.decode_token(token)
        user_id = user_data.get("user_id")
        session_id = ws.query_params.get("session_id")  # 获取客户端提供的会话ID
        
        print(f"客户端 {ws.id} 已连接")

        # 检查会话ID是否存在
        async with AsyncSessionLocal() as db:
            existing_session = await crud.get_session(db, session_id=session_id)
        
        if existing_session:
            # 如果会话存在，加载历史消息
            # 从 Redis 中获取消息队列
            messages = await Cache.get_messages(session_id)
            ai_chat = AiChat()
            try:
                await ai_chat.load_chat_history(messages)
            except Exception as e:
                print(f"缓存加载数据失败改为数据库加载: {str(e)}")
                messagelistobj = await crud.list_messages(db, session_id)
                messagelist = messagelistobj["data"]
                cur_messagelist = []
                cur_message = { }

                for message in messagelist:
                    cur_message = {
                        "role": message.role,
                        "content": message.content
                    }
                    cur_messagelist.append(cur_message)
                await ai_chat.load_chat_history(cur_messagelist)

            
                
        else:
            # 如果会话不存在，返回错误
            error_msg = f"会话不存在：{str(e)}"
            await ws.async_send_to(ws.id, json.dumps({
                    "type": "error",
                    "content": error_msg
                }))
            return ""
            


        
        active_ws[ws.id] = {
            "ai_chat": ai_chat,
            "session_id": session_id,  # 添加 session_id 到 active_ws 状态中
            "current_stream_id": None,
            "last_activity": time.time(),  # 最后活动时间
            "last_ping": time.time(),       # 最后发送ping时间
            "waiting_pong": False,          # 是否在等待pong响应
            "ws": ws                        # 保存ws实例
        }
        await ws.async_send_to(ws.id, json.dumps({
            "type": "system",
            "content": f"欢迎{session_id}来到AI聊天室！"
        }))
        return ""

    @websocket.on("close")
    async def handle_close(ws):
        if ws.id in active_ws:
            try:
                await active_ws[ws.id]["ws"].async_close()
            except Exception as e:
                print(f"关闭连接时出错: {str(e)}")
            finally:
                del active_ws[ws.id]
        return ""

    @websocket.on("message")
    async def handle_message(ws, msg):
        try:
            # 增加空消息检查
            if not msg or msg.strip() == "":
                return ""

            data = active_ws.get(ws.id)
            if not data:
                return ""

            # 获取session_id
            session_id = data["session_id"]

            # 更新最后活动时间
            data["last_activity"] = time.time()
            
            # 解析JSON消息
            try:
                msg_data = json.loads(msg)
            except json.JSONDecodeError:
                await ws.async_send_to(ws.id, json.dumps({
                    "type": "error",
                    "content": "消息格式错误，请使用JSON格式"
                }))
                return ""

            # 优先处理心跳响应
            if msg_data.get("type") == "heartbeat_pong":
                data["waiting_pong"] = False
                return ""

            # 过滤非用户消息
            if msg_data.get("type") != "user":
                print(f"收到非用户消息类型: {msg_data.get('type')}")
                return ""

            # 处理用户消息
            if msg_data.get("type") == "user":
                content = msg_data.get("content", "").strip()
            if not content:
                await ws.async_send_to(ws.id, json.dumps({
                    "type": "error",
                    "content": "消息内容不能为空"
                }))
                return ""
            
            # 存储消息到 Redis
            await Cache.set_message(session_id, {"role": "user", "content": content})

            # 处理普通消息（保持原有逻辑）
            print(f"[会话{session_id}] {msg_data.get('content', '')}")

            try:
                # 创建用户消息记录（用户提问）
                async with AsyncSessionLocal() as db:
                    await crud.create_message(
                        db=db,
                        session_id=session_id,
                        stream_id=None,  # 用户消息不关联stream_id
                        content=content,
                        role="user"      # 角色标记为用户
                    )
            except Exception as e:
                print(f"用户消息存储失败: {str(e)}")
            
            stream_id = str(uuid.uuid4())
            active_ws[ws.id]["current_stream_id"] = stream_id

            await ws.async_send_to(ws.id, json.dumps({
                "type": "stream_start",
                "stream_id": stream_id
            }))
            
            # 初始化累积变量
            full_ai_response = ""

            async for ai_response in data["ai_chat"].chat(content=content):
                # 增加响应内容检查
                if ai_response is None:
                    continue
                full_ai_response += ai_response  # 累积完整响应
                await ws.async_send_to(ws.id, json.dumps({
                    "type": "stream_chunk",
                    "stream_id": stream_id,
                    "content": ai_response or ""  # 确保不为None
                }))

            # 流式传输结束
            await ws.async_send_to(ws.id, json.dumps({
                "type": "stream_end",
                "stream_id": stream_id
            }))

            # 存储 AI 回复到 Redis
            await Cache.set_message(session_id, {"role": "assistant", "content": full_ai_response})
            
            try:    
                # 将完整AI回复写入数据库（角色标记为AI）
                async with AsyncSessionLocal() as db:
                    await crud.create_message(
                        db=db,
                        session_id=session_id,
                        stream_id=stream_id,  # 关联本次stream_id
                        content=full_ai_response,
                        role="assistant"      # 角色标记为AI助手
                    )
            except Exception as e:
                print(f"AI回复存储失败: {str(e)}")
                await ws.async_send_to(ws.id, json.dumps({
                    "type": "error",
                    "content": "消息保存失败，请联系管理员"
                }))

        except Exception as e:
            error_msg = f"系统错误：{str(e)}"
            await ws.async_send_to(ws.id, json.dumps({
                "type": "error",
                "content": error_msg
            }))
        return ""

    # 添加启动事件
    @app.startup_handler
    async def startup_handler():
        asyncio.create_task(heartbeat_checker())
        print("WebSocket服务已启动，心跳检测已启用")
