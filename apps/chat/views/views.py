from robyn import Request, Response
from core.response import ApiResponse
from apps.chat.services import (
    create_session_service,
    get_sessionlist_service,
    get_sessionlist_service_pro,
    delete_session_service,
    get_session,
    update_session_title,
    get_messages
)
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit
from core.logger import setup_logger

# 设置日志记录器
logger = setup_logger('chat_views')

@error_handler
@request_logger
@rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def create_session_view(request: Request) -> Response:
    """创建会话"""
    return await create_session_service(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def get_session_view(request: Request) -> Response:
    """获取会话列表"""
    return await get_session(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def get_session_list_view(request: Request) -> Response:
    """获取会话列表"""
    return await get_sessionlist_service(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def get_session_list_view_pro(request: Request) -> Response:
    """获取会话列表并获取最近一次更新会话的50条消息"""
    return await get_sessionlist_service_pro(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def update_session_title_view(request: Request) -> Response:
        """修改会话标题"""
        return await update_session_title(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def delete_session_view(request: Request) -> Response:
    """删除会话"""
    return await delete_session_service(request)



@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def get_messages_view(request: Request) -> Response:
    """批量获取历史消息"""
    return await get_messages(request)





