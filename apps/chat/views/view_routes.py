from robyn import Robyn, Request
from apps.chat.views.views import (
    create_session_view,
    get_session_list_view,
    get_session_list_view_pro,
    delete_session_view,
    get_session_view,
    update_session_title_view,
    get_messages_view
    
)
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit


def chat_view_routes(app: Robyn):
    """
    AI对话视图 路由 
    路由层 应该专注于 处理请求 并 返回响应
    """

    @app.get("/aichat/getsessionlist/:user_id")
    async def get_session_list(request):
        """
        获取会话列表
        """
        return await get_session_list_view(request)
    
    @app.get("/aichat/getsessionlistshow/:user_id")
    async def get_session_list_pro(request):
        """
        获取会话列表并获取最近一次更新会话的50条消息
        """
        return await get_session_list_view_pro(request)
    
    @app.get("/aichat/sessions/:session_id")
    # @error_handler
    # @request_logger
    # @auth_required
    async def get_session(request):
        """
        获取单个会话
        """
        return await get_session_view(request)
    
    @app.post("/aichat/createsession")
    # @error_handler
    # @request_logger
    # @rate_limit(max_requests=20, time_window=60)
    async def create_session_api(request):
        """
        创建会话
        """
        return await create_session_view(request)
    
    @app.patch("/aichat/sessions/:session_id")
    # @error_handler
    # @request_logger
    # @auth_required
    async def update_session_title(request):
        """
        更新会话标题
        """
        return await update_session_title_view(request)
    
    @app.delete("/aichat/deletesession/:session_id")
    async def delete_session(request):
        """
        删除会话
        """
        return await delete_session_view(request)
    
    @app.get("/aichat/sessions/:session_id/messages")
    # @error_handler
    # @request_logger
    # @auth_required
    async def get_messages(request):
        """
        批量获取会话历史消息
        """
        return await get_messages_view(request)
    

