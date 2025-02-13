from robyn import Request, Response
from core.response import ApiResponse
from apps.users.services import (
    create_user_service,
    update_user_service,
    update_user_field_service,
    delete_user_service,
    login_user,
    refresh_token,
    logout_user,
    register_precheck_and_send_verification,
    verify_and_register,
    send_verification_code_by_email,
    login_user_by_email,
    forgot_password_by_email,
    get_userinfo
)
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit, auth_userinfo
from core.logger import setup_logger

# 设置日志记录器
logger = setup_logger('user_views')

@error_handler
@request_logger
@rate_limit(max_requests=5, time_window=60)  # 每分钟最多5次注册请求
async def register_precheck(request: Request) -> Response:
    """注册预检查并发送验证码"""
    return await register_precheck_and_send_verification(request)


@error_handler
@request_logger
@rate_limit(max_requests=20, time_window=60)  # 1分钟最多20次请求
async def verify_and_register_user(request: Request) -> Response:
    """
    验证码验证并注册用户
    """
    return await verify_and_register(request)


@error_handler
@request_logger
@rate_limit(max_requests=10, time_window=60)  # 每分钟最多10次登录尝试
async def login(request: Request) -> Response:
    """用户密码登录"""

    return await login_user(request)

@error_handler
@request_logger
@rate_limit(max_requests=1, time_window=60)  # 每分钟最多1次登录尝试
async def send_verification_code_email(request: Request) -> Response:
    """发送验证码"""
    return await send_verification_code_by_email(request)

@error_handler
@request_logger
@rate_limit(max_requests=10, time_window=60)  # 每分钟最多1次登录尝试
async def login_by_email(request: Request) -> Response:
    """邮箱登录"""
    return await login_user_by_email(request)


@error_handler
@request_logger
@rate_limit(max_requests=20, time_window=60)  # 每分钟最多20次刷新令牌请求
async def refresh(request: Request) -> Response:
    """刷新访问令牌"""
    return await refresh_token(request)

@error_handler
@request_logger
@auth_required
async def logout(request: Request) -> Response:
    """用户登出"""
    return await logout_user(request)


@error_handler
@request_logger
@rate_limit(max_requests=5, time_window=60)  # 每分钟最多5次忘记密码请求
async def forgot_password(request: Request) -> Response:
    """忘记密码"""
    return await forgot_password_by_email(request)

@error_handler
@request_logger
@admin_required
@rate_limit(max_requests=30, time_window=60)  # 每分钟最多30次用户创建请求
async def create_user(request: Request) -> Response:
    """创建用户（管理员权限）"""
    return await create_user_service(request)

@error_handler
@request_logger
@admin_required
async def update_user(request: Request) -> Response:
    """更新用户信息（管理员权限）"""
    return await update_user_service(request)

@error_handler
@request_logger
@admin_required
async def update_user_field(request: Request) -> Response:
    """更新用户指定字段（管理员权限）"""
    return await update_user_field_service(request)

@error_handler
@request_logger
@admin_required
async def delete_user(request: Request) -> Response:
    """删除用户（管理员权限）"""
    return await delete_user_service(request)

@error_handler
@request_logger
# @auth_userinfo
async def get_current_user(request: Request) -> Response:
    """获取当前登录用户信息"""
    return await get_userinfo(request)

@error_handler
@request_logger
@admin_required
@rate_limit(max_requests=100, time_window=60)  # 每分钟最多100次用户查询请求
async def get_users(request: Request) -> Response:
    """获取用户列表（管理员权限）"""
    try:
        # TODO: 实现分页和筛选功能
        from apps.users.queries import get_all_users
        return await get_all_users()
    except Exception as e:
        logger.error(f"Error getting users list: {str(e)}")
        return ApiResponse.error("获取用户列表失败")







