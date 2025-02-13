from robyn.robyn import Request
from apps.users.queries import fuzzy_search_user, get_user, get_user_by_id, get_user_by_username, get_users_service
from apps.users.services import create_user_service, delete_user_service, get_user_by_email, get_user_by_phone, update_user_field_service, update_user_service, get_user_ip_history, get_token, check_token

"""
    定义用户API接口
    接口层 应该专注于 处理基础的数据库操作 并 返回成功的状态码及数据内容
    接口层避免直接暴露在外,应该由服务层调用
"""

# 查询
async def get_all_users_api(request: Request):
    """
    获取所有用户 接口
    """
    return await get_users_service(request)

async def get_user_api(request: Request):
    """
    通过用户ID获取单个用户 接口
    """
    return await get_user_by_id(request)

async def get_user_by_username_api(request: Request):
    """
    通过用户名获取单个用户 接口
    """
    username = request.path_params.get("username")  # 从路径参数获取username
    return await get_user_by_username(username)

async def get_user_by_email_api(request: Request):
    """
    通过邮箱获取单个用户 接口
    """
    email = request.path_params.get("email")  # 从路径参数获取email
    return await get_user_by_email(email)

async def get_user_by_phone_api(request: Request):
    """
    通过手机号获取单个用户 接口
    """
    phone = request.path_params.get("phone")  # 从路径参数获取phone
    return await get_user_by_phone(phone)
    
async def fuzzy_search_user_api(request: Request):
    """
    账号匹配用户 接口
    """
    account = request.path_params.get("account")  # 从路径参数获取account
    return await fuzzy_search_user(account)

async def get_users_api(request: Request):
    """
    通过用户ID、邮箱、用户名、手机号 通用查询用户 接口
    """
    userdata = request.path_params.get("userdata")  # 从路径参数获取userdata
    return await get_user(userdata)

async def get_user_ip_history_api(request: Request):
    """
    获取用户IP地址历史
    """
    return await get_user_ip_history(request)


async def create_user_api(request: Request):
    """
    创建用户
    """
    return await create_user_service(request) 

async def update_user_api(request: Request):
    """
    更新用户
    """
    return await update_user_service(request)


# @app.patch("/user/:user_id")
async def update_user_field_api(request: Request):
    """
    更新用户指定字段
    """
    return await update_user_field_service(request)

# @app.delete("/user/:user_id")
async def delete_user_api(request: Request):
    """
    删除用户
    """
    return await delete_user_service(request)

async def get_token_api(request: Request):
    """
    获取token
    """
    return await get_token(request)

async def check_token_api(request: Request):
    """
    检查token状态
    """
    return await check_token(request)