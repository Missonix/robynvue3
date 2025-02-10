from robyn.robyn import Request
from robyn import Response
from core.response import ApiResponse
from apps.chat import crud as chat_crud
from core.database import AsyncSessionLocal
from apps.users import crud as user_crud
from .utils import generate_session_id

"""
    定义用户API接口
    接口层 应该专注于 处理基础的数据库操作 并 返回成功的状态码及数据内容
    接口层避免直接暴露在外,应该由服务层调用
"""

async def create_chat_session(request: Request) -> Response:
    """
    创建新会话
    """
    try:
        data = request.json()
        user_id = data.get("user_id")
        # token = data["token"]
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

async def get_session(request: Request) -> Response:
    """获取单个会话"""
    try:
        session_id = request.path_params.get("session_id")
        async with AsyncSessionLocal() as db:
            session = await chat_crud.get_session(db, session_id)
            return ApiResponse.success(data=session.to_dict())
    except Exception as e:
        return ApiResponse.error(message=str(e))
    
async def get_sessions(request: Request) -> Response:
    """批量获取会话"""
    try:
        session_data = request.json()
        user_id = session_data.get("user_id")
        page = int(session_data.get("page", 1))
        page_size = int(session_data.get("page_size", 20))
        async with AsyncSessionLocal() as db:
            sessions = await chat_crud.list_sessions(db, user_id, page, page_size)
            return ApiResponse.success(data=[s.to_dict() for s in sessions])
    except Exception as e:
        return ApiResponse.error(message=str(e))
    
async def delete_session(request: Request) -> Response:
    """删除单个会话"""
    try:
        session_id = request.path_params.get("session_id")
        async with AsyncSessionLocal() as db:
            session = await chat_crud.soft_delete_session(db, session_id)
            return ApiResponse.success(data="会话删除成功")
    except Exception as e:
        return ApiResponse.error(message=str(e))
    
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

async def create_chat_message(request: Request) -> Response:
    """创建新消息"""
    try:
        data = request.json()
        async with AsyncSessionLocal() as db:
            message = await chat_crud.create_message(
                db,
                session_id=data.get("session_id"),
                content=data.get("content"),
                role=data.get("role")
            )
            return ApiResponse.success(data=message.to_dict())
    except Exception as e:
        return ApiResponse.error(message=str(e))

async def get_message(request: Request) -> Response:
    """获取会话单个消息"""
    try:
        message_id = request.path_params.get("message_id")
        session_id = request.path_params.get("session_id")
        
        async with AsyncSessionLocal() as db:
            message = await chat_crud.get_message(db, session_id, message_id)
            return ApiResponse.success(data=message.to_dict())
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

async def delete_message(request: Request) -> Response:
    """删除会话单个消息"""
    try:
        message_id = request.path_params.get("message_id")
        
        async with AsyncSessionLocal() as db:
            message = await chat_crud.soft_delete_message(db, message_id)
            return ApiResponse.success(data="消息删除成功")
    except Exception as e:
        return ApiResponse.error(message=str(e))
    
async def update_message_content(request: Request) -> Response:
    """修改会话单个消息内容(仅限role:user的消息)"""
    try:
        message_id = request.path_params.get("message_id")
        new_content = request.json().get("new_content") 
        
        async with AsyncSessionLocal() as db:
            message = await chat_crud.update_message_content(db, message_id, new_content)
            return ApiResponse.success(data="消息编辑成功")
    except Exception as e:
        return ApiResponse.error(message=str(e))
