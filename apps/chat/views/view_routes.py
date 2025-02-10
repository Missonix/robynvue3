from robyn import Robyn, Request
from apps.chat.views.views import (
    create_session_view,
    get_session_list_view,
    delete_session_view,
    
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
    
    @app.delete("/aichat/deletesession/:session_id")
    async def delete_session(request):
        """
        删除会话
        """
        return await delete_session_view(request)
    
    app.add_route(route_type="POST", endpoint="/aichat/createsession", handler=create_session_view) # 创建会话路由
    

