from robyn import Request, Response
from core.response import ApiResponse
from apps.chat.services import (
    create_session_service,
    get_sessionlist_service,
    delete_session_service,
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
async def get_session_list_view(request: Request) -> Response:
    """获取会话列表"""
    return await get_sessionlist_service(request)

@error_handler
@request_logger
# @rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次创建会话请求
async def delete_session_view(request: Request) -> Response:
    """获取会话列表"""
    return await delete_session_service(request)







