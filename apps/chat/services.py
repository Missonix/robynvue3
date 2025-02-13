import json
import re
import random
from datetime import datetime, timedelta
from robyn import Headers, Request, Response, jsonify, status_codes
from apps.users import crud as user_crud
from apps.chat import crud as chat_crud
from apps.chat.models import ChatSession
from apps.chat.models import ChatMessage
from core.auth import TokenService, get_token_from_request
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from core.logger import setup_logger
from core.cache import Cache
from .utils import generate_session_id

# 设置日志记录器
logger = setup_logger('chat_services')

"""
接收用户发来的消息->保存在数据库(异步)->
"""

async def create_session_service(request: Request) -> Response:
    """
    创建新会话
    """
    try:
        data = request.json()
        user_id = data.get("user_id")
        # access_token = data["access_token"]
        # if not TokenService.verify_token(access_token):
        #     return ApiResponse.error(message="token验证失败，请重新登录！")
        
        async with AsyncSessionLocal() as db:
            # 判断用户存在
            user = await user_crud.get_user(db, user_id)
            if not user:
                return ApiResponse.error(message="用户不存在无法创建会话")

            session = await chat_crud.create_session(
                db, 
                session_id=generate_session_id(),
                user_id=user_id,
                title=data.get("title", "新会话")
            )
            return ApiResponse.success(data=session.to_dict())
    except Exception as e:
        return ApiResponse.error(message=str(e))
    

async def get_sessionlist_service(request: Request) -> Response:
    """批量获取会话"""
    try:
        user_id = request.path_params.get("user_id")
        print("####################批量获取会话##########################")
        print('user_id:',user_id)
        page = int(request.path_params.get("page", 1))
        page_size = int(request.path_params.get("page_size", 20))
        
        async with AsyncSessionLocal() as db:
            # 获取分页数据
            sessions = await chat_crud.list_sessions(db, user_id, page, page_size)
            print("###############################################################")
            print(sessions)
            # 获取总条数
            total = await chat_crud.get_user_session_count(db, user_id)
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size
            
            return ApiResponse.success(data={
                "list": [s.to_dict() for s in sessions],
                "pagination": {
                    "total": total,
                    "pageSize": page_size,
                    "pageNum": page,
                    "totalPages": total_pages
                }
            })
    except Exception as e:
        return ApiResponse.error(message=str(e))
    

async def get_sessionlist_service_pro(request: Request) -> Response:
    """批量获取会话（优化版）"""
    try:
        user_id = request.path_params.get("user_id")
        
        # 强制分页参数为最近20条
        page = 1
        page_size = 20
        
        async with AsyncSessionLocal() as db:
            # 获取最近更新的20条会话（强制按更新时间降序）
            sessions = await chat_crud.list_sessions(db, user_id, page, page_size)
            
            # 获取总条数
            total = await chat_crud.get_user_session_count(db, user_id)
            total_pages = (total + page_size - 1) // page_size

            # 处理消息数据
            session_list = []
            if sessions:
                # 获取第一条会话的50条消息（最新会话）
                latest_session = sessions[0]
                messages = await chat_crud.list_messages(
                    db,
                    session_id=latest_session.session_id,
                    page=1,
                    page_size=50
                )
                
                # 构造最新会话数据
                latest_data = latest_session.to_dict()
                latest_data["messages"] = [msg.to_dict() for msg in messages]
                session_list.append(latest_data)

                # 处理其他会话（不包含消息）
                for session in sessions[1:]:
                    session_data = session.to_dict()
                    session_data["messages"] = []
                    session_list.append(session_data)
            else:
                session_list = []

            return ApiResponse.success(data={
                "list": session_list,
                "pagination": {
                    "total": total,
                    "pageSize": page_size,
                    "pageNum": page,
                    "totalPages": total_pages
                }
            })
            
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        return ApiResponse.error(message="获取会话列表失败")
    
# async def get_session(request: Request) -> Response:
#     """获取单个会话"""
#     try:
#         session_id = request.path_params.get("session_id")
#         async with AsyncSessionLocal() as db:
#             session = await chat_crud.get_session(db, session_id)
#             return ApiResponse.success(data=session.to_dict())
#     except Exception as e:
#         return ApiResponse.error(message=str(e))
    
async def get_session(request: Request) -> Response:
    """获取单个会话(包含最新50条消息)"""
    try:
        session_id = request.path_params.get("session_id")
        
        async with AsyncSessionLocal() as db:
            # 获取会话基本信息
            session = await chat_crud.get_session(db, session_id)
            if not session:
                return ApiResponse.error(message="会话不存在", code=404)
            
            # 获取最近50条消息
            messages = await chat_crud.list_messages(
                db,
                session_id=session_id,
                page=1,
                page_size=50
            )
            
            # 构建响应数据
            session_data = session.to_dict()
            session_data["messages"] = [msg.to_dict() for msg in messages]
            
            return ApiResponse.success(data=session_data)
            
    except Exception as e:
        logger.error(f"获取会话详情失败: {str(e)}")
        return ApiResponse.error(message="获取会话详情失败")
    
async def update_session_title(request: Request) -> Response:
    """更新会话标题"""
    try:
        session_id = request.path_params.get("session_id")
        new_title = request.json().get("new_title")
        async with AsyncSessionLocal() as db:
            session = await chat_crud.update_session_title(db, session_id, new_title)
            return ApiResponse.success(data="会话标题更新成功")
    except Exception as e:
        return ApiResponse.error(message=str(e))

async def delete_session_service(request: Request) -> Response:
    """删除会话"""
    try:
        session_id = request.path_params.get("session_id")
        async with AsyncSessionLocal() as db:
            session = await chat_crud.soft_delete_session(db, session_id)
            return ApiResponse.success(data=True)
    except Exception as e:
        return ApiResponse.error(message=str(e))
    

async def get_messages(request: Request) -> Response:
    """批量获取会话历史消息"""
    try:
        session_id = request.path_params.get("session_id")
        page = int(request.query_params.get("page", "1"))
        page_size = int(request.query_params.get("pageSize", "50"))
        
        async with AsyncSessionLocal() as db:
            messages = await chat_crud.list_messages(db, session_id, page, page_size)
            return ApiResponse.success(data=[m.to_dict() for m in messages])
    except ValueError as e:
        return ApiResponse.error(message=f"无效的分页参数: {str(e)}")
    except Exception as e:
        return ApiResponse.error(message=str(e))
