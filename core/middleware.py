import traceback
from functools import wraps
from typing import Callable, Any
from robyn import Request, Response, status_codes
from core.response import ApiResponse
from sqlalchemy.exc import SQLAlchemyError
from core.logger import setup_logger
from core.auth import TokenService, get_token_from_request, get_current_user
from apps.users.services import check_and_refresh_token


# 设置日志记录器
logger = setup_logger('middleware')


def error_handler(func: Callable) -> Callable:
    """
    全局错误处理装饰器
    用于捕获和处理路由处理函数中的异常
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Response:
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            # 数据库相关错误
            logger.error(f"Database error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return ApiResponse.error(
                message="数据库操作失败",
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ValueError as e:
            # 参数验证错误
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return ApiResponse.validation_error(str(e))
        except PermissionError as e:
            # 权限相关错误
            logger.warning(f"Permission error in {func.__name__}: {str(e)}")
            return ApiResponse.forbidden(str(e))
        except Exception as e:
            # 其他未预期的错误
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return ApiResponse.error(
                message="服务器内部错误",
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def request_logger(func: Callable) -> Callable:
    """
    请求日志记录装饰器
    用于记录请求的详细信息
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Response:
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url}")
        logger.debug(f"Headers: {request.headers}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            logger.debug(f"Body: {request.body}")
            
        # 执行处理函数
        response = await func(request, *args, **kwargs)
        
        # 记录响应信息
        logger.info(f"Response: {response.status_code}")
        logger.debug(f"Response Body: {response.description}")
        
        return response
    return wrapper

def auth_required(func: Callable) -> Callable:
    """
    身份认证装饰器
    用于验证用户是否已登录
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Response:
        token = get_token_from_request(request)
        if not token:
            return ApiResponse.unauthorized("请先登录")
        
        # 验证令牌有效性
        if not TokenService.verify_token(token):
            return ApiResponse.unauthorized("登录已过期，请重新登录")
        
        # 检查是否需要续期
        refresh_response = await check_and_refresh_token(request)
        if refresh_response:
            # 如果需要续期，使用新的响应头
            response = await func(request, *args, **kwargs)
            response.headers.update(refresh_response.headers)
            return response
        
        return await func(request, *args, **kwargs)
    return wrapper

def auth_userinfo(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Response:
        token = get_token_from_request(request)
        if not token:
            return ApiResponse.unauthorized("请先登录")
        
        # 验证令牌有效性
        if not TokenService.verify_token(token):
            return ApiResponse.unauthorized("登录已过期，请重新登录")
        
        # 获取用户信息并设置到 request 中
        current_user = await get_current_user(request)
        if not current_user:
            return ApiResponse.unauthorized("未找到用户信息")
        
        # 将用户信息添加到 request 中
        request.user_info = current_user
    
        # 检查是否需要续期
        refresh_response = await check_and_refresh_token(request)
        if refresh_response:
            # 如果需要续期，使用新的响应头
            response = await func(request, *args, **kwargs)
            response.headers.update(refresh_response.headers)
            return response
    
        return await func(request, *args, **kwargs)
    return wrapper

def admin_required(func: Callable) -> Callable:
    """
    管理员权限装饰器
    用于验证用户是否具有管理员权限
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Response:
        token = get_token_from_request(request)
        if not token:
            return ApiResponse.unauthorized("请先登录")
        
        # 验证令牌有效性
        if not TokenService.verify_token(token):
            return ApiResponse.unauthorized("登录已过期，请重新登录")
        
        # 验证管理员权限
        is_admin = await TokenService.verify_admin(token)
        if not is_admin:
            return ApiResponse.forbidden("需要管理员权限")
        
        # 检查是否需要续期
        refresh_response = await check_and_refresh_token(request)
        if refresh_response:
            # 如果需要续期，使用新的响应头
            response = await func(request, *args, **kwargs)
            response.headers.update(refresh_response.headers)
            return response
        
        return await func(request, *args, **kwargs)
    return wrapper

def rate_limit(max_requests: int, time_window: int) -> Callable:
    """
    速率限制装饰器
    用于限制API的访问频率
    :param max_requests: 在时间窗口内允许的最大请求数
    :param time_window: 时间窗口（秒）
    """
    from collections import defaultdict
    import time
    
    # 用于存储请求记录
    request_records = defaultdict(list)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Response:
            # 获取客户端IP
            client_ip = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            
            # 获取当前时间
            current_time = time.time()
            
            # 清理过期的请求记录
            request_records[client_ip] = [
                timestamp for timestamp in request_records[client_ip]
                if current_time - timestamp < time_window
            ]
            
            # 检查是否超过限制
            if len(request_records[client_ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return ApiResponse.error(
                    message="请求过于频繁，请稍后再试",
                    status_code=status_codes.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # 记录新的请求
            request_records[client_ip].append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 