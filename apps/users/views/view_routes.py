from robyn import Robyn, Request
from apps.users.views.views import (
    login,
    logout,
    register_precheck,
    verify_and_register_user
)

def users_view_routes(app):
    """
    用户视图 路由 
    路由层 应该专注于 处理请求 并 返回响应
    """
    
    app.add_route(route_type="POST", endpoint="/users/login", handler=login) # 登录路由
    app.add_route(route_type="GET", endpoint="/users/logout", handler=logout) # 登出路由
    app.add_route(route_type="POST", endpoint="/users/register/precheck", handler=register_precheck) # 注册预检查路由
    app.add_route(route_type="POST", endpoint="/users/register/verify", handler=verify_and_register_user) # 注册验证路由
