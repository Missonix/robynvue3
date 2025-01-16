import json
from robyn import Headers, Request, Response, jsonify, status_codes
from apps.users import crud
from apps.users.models import User
from core.auth import TokenService, verify_password, get_password_hash, get_token_from_request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.queries import get_user_by_email, get_user_by_phone
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from core.logger import setup_logger
from datetime import datetime

# 设置日志记录器
logger = setup_logger('user_services')

"""
    crud -> services -> api
    服务层:根据业务逻辑整合crud数据操作 封装业务方法 可以由上层函数直接调用
    服务层 应该完成 业务逻辑（如判断数据是否存在、响应失败的处理逻辑）
"""

async def create_user_service(request):
    """
    创建用户接口 管理员权限
    """
    try:
        user_data = request.json()
        username = user_data.get("username")
        email = user_data.get("email")
        phone = user_data.get("phone")
        password = user_data.get("password")
        
        # 确保必填字段都存在
        if not all([username, email, phone, password]):
            return ApiResponse.validation_error("缺少必填字段")

        # 检查用户是否已存在
        async with AsyncSessionLocal() as db:
            user_exists = (await crud.get_user_by_filter(db, {"username": username}) or 
                         await crud.get_user_by_filter(db, {"email": email}) or 
                         await crud.get_user_by_filter(db, {"phone": phone}))
            
            if user_exists:
                return ApiResponse.error(
                    message="用户已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )

            user_data["password"] = get_password_hash(user_data["password"])

            try:
                inserted_user = await crud.create_user(db, user_data)
                if not inserted_user:
                    raise Exception("User creation failed")
                return ApiResponse.success(
                    data=inserted_user.to_dict(),
                    message="用户创建成功"
                )
            except Exception as e:
                raise Exception(f"Database integrity error: {str(e)}")

    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="创建用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_user_service(request):
    """
    更新用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_data = request.json()
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")

            user_data["password"] = get_password_hash(user_data["password"])
    
            user = await crud.update_user(db, user_id, user_data)
            if not user:
                raise Exception("User update failed")
            
            return ApiResponse.success(
                data=user.to_dict(),
                message="用户更新成功"
            )
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
        return ApiResponse.error(message="更新用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
    
async def update_user_field_service(request):
    """
    更新用户指定字段
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            
            user_data = request.json()

            # 处理布尔值字段
            bool_fields = ['is_admin', 'is_active', 'is_deleted']
            for field in bool_fields:
                if field in user_data:
                    if isinstance(user_data[field], str):
                        user_data[field] = user_data[field].lower() == 'true'
                    else:
                        user_data[field] = bool(user_data[field])

            if "password" in user_data:
                user_data["password"] = get_password_hash(user_data["password"])
                
            user = await crud.update_user(db, user_id, user_data)
            if not user:
                raise Exception("User update failed")
            
            return ApiResponse.success(
                data=user.to_dict(),
                message="用户字段更新成功"
            )
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
        return ApiResponse.error(message="更新用户字段失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_user_service(request):
    """
    删除用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            
            user = await crud.delete_user(db, user_id) 
            if not user:
                raise Exception("User delete failed")
            
            return ApiResponse.success(message="用户删除成功")
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="删除用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def login_user(request):
    """
    登录用户
    """
    try:
        request_data = request.json()
        account = request_data.get("account")
        password = request_data.get("password")

        if not account or not password:
            logger.warning("Missing account or password")
            return ApiResponse.validation_error("账号和密码不能为空")

        # 获取用户响应
        user_response = await get_user_by_email(account) or await get_user_by_phone(account)
        logger.debug(f"User response status: {user_response.status_code}")
        
        if user_response.status_code != status_codes.HTTP_200_OK:
            return ApiResponse.not_found("用户不存在")

        try:
            response_data = json.loads(user_response.description)
            logger.debug(f"Response data: {response_data}")

            if not isinstance(response_data, dict):
                logger.error("Response data is not a dictionary")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if "data" not in response_data:
                logger.error("No 'data' field in response")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            user_data = response_data["data"]
            logger.debug(f"User data: {user_data}")

            if not isinstance(user_data, dict):
                logger.error("User data is not a dictionary")
                return ApiResponse.error(message="用户数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if "password" not in user_data:
                logger.error("No password field in user data")
                return ApiResponse.error(message="用户数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if not verify_password(password, user_data["password"]):
                logger.warning(f"Invalid password attempt for account: {account}")
                return ApiResponse.error(
                    message="密码错误",
                    status_code=status_codes.HTTP_401_UNAUTHORIZED
                )

            # 获取用户IP地址
            ip_address = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            
            # 更新用户IP地址
            async with AsyncSessionLocal() as db:
                user = await crud.get_user_by_filter(db, {"email": user_data["email"]})
                if user:
                    await crud.update_user(db, user.id, {"ip_address": ip_address, "last_login": datetime.utcnow()})
                    logger.info(f"Updated user {user.username} IP address to {ip_address}")
            
            # 生成Token
            token_data = {
                "sub": user_data["username"],
                "email": user_data["email"],
                "is_admin": user_data.get("is_admin", False)
            }
            
            # 创建访问令牌和刷新令牌
            access_token = TokenService.create_access_token(token_data)
            refresh_token = TokenService.create_refresh_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "refresh_token": refresh_token,
                    "ip_address": ip_address
                }
            )
            
            # 设置访问令牌到HttpOnly Cookie
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )

            return response

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding user data: {str(e)}")
            return ApiResponse.error(message="用户数据解析失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error processing user login: {str(e)}")
        return ApiResponse.error(message="登录处理失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def refresh_token(request):
    """
    刷新访问令牌
    """
    try:
        refresh_token = request.json().get("refresh_token")
        if not refresh_token:
            return ApiResponse.validation_error("缺少刷新令牌")
        
        # 验证刷新令牌
        payload = TokenService.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return ApiResponse.unauthorized("无效的刷新令牌")
        
        # 创建新的访问令牌
        token_data = {
            "sub": payload["sub"],
            "email": payload["email"],
            "is_admin": payload.get("is_admin", False)
        }
        new_access_token = TokenService.create_access_token(token_data)
        
        # 创建响应
        response = ApiResponse.success(
            message="令牌刷新成功",
            data={"username": payload["sub"]}
        )
        
        # 设置新的访问令牌
        response.headers["Set-Cookie"] = (
            f"access_token=Bearer {new_access_token}; "
            f"HttpOnly; Secure; Path=/; SameSite=Strict; "
            f"Max-Age={30*60}"  # 30分钟
        )
        
        return response
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return ApiResponse.error(message="令牌刷新失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def check_and_refresh_token(request):
    """
    检查并自动续期令牌
    """
    try:
        token = get_token_from_request(request)
        if not token:
            return None
            
        # 检查令牌是否需要续期
        needs_refresh, payload = TokenService.check_token_needs_refresh(token)
        if needs_refresh and payload:
            # 创建新的访问令牌
            token_data = {
                "sub": payload["sub"],
                "email": payload["email"],
                "is_admin": payload.get("is_admin", False)
            }
            new_access_token = TokenService.create_access_token(token_data)
            
            # 创建响应
            response = ApiResponse.success(
                message="令牌已自动续期",
                data={"username": payload["sub"]}
            )
            
            # 设置新的访问令牌
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {new_access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )
            
            return response
            
        return None
    except Exception as e:
        logger.error(f"Error checking token refresh: {str(e)}")
        return None

async def logout_user(request):
    """
    退出登录
    """
    try:
        # 获取当前令牌
        token = get_token_from_request(request)
        if token:
            # 将令牌加入黑名单
            TokenService.revoke_token(token)
        
        # 创建响应
        response = ApiResponse.success(message="退出登录成功")
        
        # 清除Cookie中的访问令牌
        response.headers["Set-Cookie"] = (
            "access_token=; HttpOnly; Secure; Path=/; SameSite=Strict; Max-Age=0"
        )
        
        return response
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="退出登录失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def register_precheck_and_send_verification(request):
    """
    注册预校验并发送验证码
    """
    try:
        user_data = request.json()
        username = user_data.get("username")
        email = user_data.get("email")
        phone = user_data.get("phone")
        password = user_data.get("password")
        
        if not all([username, email, phone, password]):
            return ApiResponse.validation_error("缺少必填字段")

        async with AsyncSessionLocal() as db:
            user_exists = (await crud.get_user_by_filter(db, {"username": username}) or 
                         await crud.get_user_by_filter(db, {"email": email}) or 
                         await crud.get_user_by_filter(db, {"phone": phone}))
            
            if user_exists:
                return ApiResponse.error(
                    message="用户已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )

            # TODO: 实现发送验证码逻辑
            return ApiResponse.success(message="验证码已发送")
            
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="注册预检失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_user_ip_history(request):
    """
    获取用户IP地址历史
    """
    try:
        user_id = request.path_params.get("user_id")
        
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, user_id)
            if not user:
                return ApiResponse.not_found("用户不存在")
            
            # 构建IP地址历史信息
            ip_history = {
                "current_ip": user.ip_address,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "user_info": {
                    "username": user.username,
                    "email": user.email
                }
            }
            
            logger.info(f"Retrieved IP history for user {user.username}")
            return ApiResponse.success(
                data=ip_history,
                message="获取用户IP历史成功"
            )
            
    except Exception as e:
        logger.error(f"Error getting user IP history: {str(e)}")
        return ApiResponse.error(
            message="获取用户IP历史失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
