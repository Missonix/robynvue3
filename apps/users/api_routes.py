from robyn import Request
from apps.users.api import (
    create_user_api,
    get_all_users_api,
    get_user_by_email_api,
    get_user_by_phone_api,
    get_user_by_username_api,
    get_users_api,
    get_user_api,
    update_user_api,
    delete_user_api,
    fuzzy_search_user_api,
    update_user_field_api,
    get_user_ip_history_api
)
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit


def users_api_routes(app):
    """
    注册用户路由
    API 路由 - 用于后端接口
    路由层 应该专注于 处理请求 并 返回响应
    """
    @app.get("/api/users")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)  # 限制每分钟最多100次请求
    async def users_get(request):
        """
        获取所有用户
        """
        return await get_all_users_api(request)
    
    @app.get("/api/users/:user_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_get(request):
        """
        通过用户ID获取单个用户
        """
        return await get_user_api(request)
    
    @app.get("/api/users/username/:username")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_get_by_username(request):
        """
        通过用户名获取单个用户
        """
        return await get_user_by_username_api(request)
    
    @app.get("/api/users/email/:email")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_get_by_email(request):
        """
        通过邮箱获取单个用户
        """
        return await get_user_by_email_api(request)
    
    @app.get("/api/users/phone/:phone")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_get_by_phone(request):
        """
        通过手机号获取单个用户
        """
        return await get_user_by_phone_api(request)
    
    @app.get("/api/users/ip_history/:user_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_ip_history(request):
        """
        获取用户IP地址历史
        """
        return await get_user_ip_history_api(request)


    @app.post("/api/users")
    @error_handler
    @request_logger
    @rate_limit(max_requests=20, time_window=60)  # 限制每分钟最多20次创建请求
    async def users_create(request):
        """
        创建用户
        """
        return await create_user_api(request)
    
    @app.put("/api/users/:user_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_update(request):
        """
        更新用户
        """
        return await update_user_api(request)
    
    @app.patch("/api/users/:user_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_update_field(request):
        """
        更新用户指定字段
        """
        return await update_user_field_api(request)
    
    @app.delete("/api/users/:user_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def user_delete(request):
        """
        删除用户
        """
        return await delete_user_api(request)