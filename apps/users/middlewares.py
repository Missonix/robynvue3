import json
from robyn import Request
from robyn.authentication import AuthenticationHandler, Identity

from core.auth import TokenService
from core.database import AsyncSessionLocal
from apps.users import services

"""
中间件
"""

class BasicAuthHandler(AuthenticationHandler):
    def authenticate(self, request: Request):
        """
        通过cookie内的access_token认证
        """

        # 从 headers 中提取 Cookie
        cookie_header = request.headers.get("Cookie") if hasattr(request.headers, "get") else None

        if not cookie_header:
            return None

        # 手动解析 Cookie 获取 access_token
        cookies = {cookie.split("=")[0].strip(): cookie.split("=")[1].strip() for cookie in cookie_header.split(";") if "=" in cookie}
        token = cookies.get("access_token")

        if not token:
            return None

        try:
            # 移除Bearer前缀
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            # 解码token
            payload = TokenService.decode_token(token)
            username = payload["sub"]

            # 使用同步方式运行异步代码
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 验证用户是否存在于数据库中
                user_response = loop.run_until_complete(services.get_user_by_username(username))
                
                if user_response.status_code != 200:
                    return None
                    
                user_json = user_response.description
                user_dict = json.loads(user_json)
                
                # 可以在这里添加额外的验证
                if user_dict.get('is_deleted') or not user_dict.get('is_active'):
                    return None
                
                return Identity(claims={
                    "user": str(user_dict['username']),
                    "user_id": str(user_dict['user_id']),  # 转换为字符串
                    "is_admin": str(user_dict['is_admin']).lower()  # 转换为字符串
                })
            finally:
                loop.close()
            
        except Exception as e:
            return None






