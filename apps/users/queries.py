from robyn import Response, jsonify, status_codes
from sqlalchemy import select
from apps.users import crud
from apps.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from core.logger import setup_logger

# 设置日志记录器
logger = setup_logger('user_queries')

"""
    定义复杂查询
    处理复杂的数据库查询逻辑，例如多表关联查询、聚合查询、排序、分页等。
    职责：解耦复杂逻辑，方便复用。
"""

async def get_user_by_id(request):
    """
    通过用户ID获取单个用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            return ApiResponse.success(data=user_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
    
async def get_user_by_username(username):
    """
    通过用户名获取单个用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_obj = await crud.get_user_by_filter(db, {"username": username})
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            return ApiResponse.success(data=user_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_user_by_email(email: str) -> Response:
    """通过邮箱获取用户"""
    try:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_filter(db, {"email": email})
            if not user:
                logger.warning(f"User not found with email: {email}")
                return ApiResponse.not_found("用户不存在")
            
            user_dict = user.to_dict()
            logger.debug(f"User data retrieved: {user_dict}")
            return ApiResponse.success(data=user_dict)
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        return ApiResponse.error("获取用户信息失败")

async def get_user_by_phone(phone: str) -> Response:
    """通过手机号获取用户"""
    try:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_filter(db, {"phone": phone})
            if not user:
                logger.warning(f"User not found with phone: {phone}")
                return ApiResponse.not_found("用户不存在")
            
            user_dict = user.to_dict()
            logger.debug(f"User data retrieved: {user_dict}")
            return ApiResponse.success(data=user_dict)
    except Exception as e:
        logger.error(f"Error getting user by phone: {str(e)}")
        return ApiResponse.error("获取用户信息失败")

async def get_user(userdata):
    """
    通用动态查询
    通过用户ID、邮箱、用户名、手机号查询用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_obj = (await crud.get_user(db, userdata) or 
                       await crud.get_user_by_filter(db, {"username": userdata}) or 
                       await crud.get_user_by_filter(db, {"email": userdata}) or 
                       await crud.get_user_by_filter(db, {"phone": userdata}))
            
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            return ApiResponse.success(data=user_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def fuzzy_search_user(account):
    """
    账号匹配用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_obj = (await crud.get_user_by_filter(db, {"username": account}) or 
                       await crud.get_user_by_filter(db, {"email": account}) or 
                       await crud.get_user_by_filter(db, {"phone": account}))
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            return ApiResponse.success(data=user_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="模糊搜索用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_users_service(request):
    """
    获取所有用户列表
    """
    try:
        async with AsyncSessionLocal() as db:
            users_obj = await crud.get_users_by_filters(db)
            users_data = [user.to_dict() for user in users_obj]
            return ApiResponse.success(data=users_data)
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取用户列表失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

