from robyn import Request, Robyn
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit
from .api import (
    create_chat_session,
    get_session,
    get_sessions,
    delete_session,
    update_session_title,
    create_chat_message,
    get_message,
    get_messages,
    delete_message,
    update_message_content
)


def chat_api_routes(app: Robyn):
    """注册聊天接口路由"""
    
    @app.post("/api/chat/session")
    @error_handler
    @request_logger
    @rate_limit(max_requests=20, time_window=60)
    async def create_session_api(request):
        """
        创建会话
        """
        return await create_chat_session(request)
    
    @app.get("/api/chat/sessions/:session_id")
    @error_handler
    @request_logger
    # @auth_required
    async def get_session_api(request):
        """
        获取单个会话
        """
        return await get_session(request)
    
    @app.post("/api/chat/sessions")
    @error_handler
    @request_logger
    # @auth_required
    async def get_sessions_api(request):
        """
        批量获取会话
        """
        return await get_sessions(request)
    
    @app.delete("/api/chat/sessions/:session_id")
    @error_handler
    @request_logger
    # @auth_required
    async def delete_session_api(request):
        """
        删除单个会话
        """
        return await delete_session(request)
    
    @app.patch("/api/chat/sessions/:session_id")
    @error_handler
    @request_logger
    # @auth_required
    async def update_session_title_api(request):
        """
        更新会话标题
        """
        return await update_session_title(request)

    @app.post("/api/chat/message")
    @error_handler
    @request_logger
    # @auth_required
    @rate_limit(max_requests=60, time_window=60)
    async def create_message_api(request):
        """
        创建新消息
        """
        return await create_chat_message(request)
    

    @app.get("/api/chat/sessions/:session_id/messages/:message_id")
    @error_handler
    @request_logger
    # @auth_required
    async def get_message_api(request):
        """
        获取单个消息
        """
        return await get_message(request)
    
    @app.get("/api/chat/sessions/:session_id/messages")
    @error_handler
    @request_logger
    # @auth_required
    async def get_messages_api(request):
        """
        批量获取会话历史消息
        """
        return await get_messages(request)
    
    @app.delete("/api/chat/messages/:message_id")
    @error_handler
    @request_logger
    # @auth_required
    async def delete_message_api(request):
        """
        删除单个消息
        """
        return await delete_message(request)
    
    @app.patch("/api/chat/messages/:message_id")
    @error_handler
    @request_logger
    # @auth_required
    async def update_message_content_api(request):
        """
        修改单个消息内容
        """
        return await update_message_content(request)