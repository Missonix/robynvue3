from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.response import ApiResponse
from core.logger import setup_logger
from apps.users import crud
from core.database import AsyncSessionLocal
from core.token_blacklist import token_blacklist
from robyn import Request

# 设置日志记录器
logger = setup_logger('auth')

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token相关配置
SECRET_KEY = "your-secret-key-keep-it-secret"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
AUTO_REFRESH_BEFORE_EXPIRY_MINUTES = 5  # 在过期前5分钟自动续期

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    :param password: 明文密码
    :return: 哈希密码
    """
    return pwd_context.hash(password)

class TokenService:
    """Token服务类"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        :param data: 要编码的数据
        :param expires_delta: 过期时间增量
        :return: 编码后的JWT令牌
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        :param data: 要编码的数据
        :return: 编码后的JWT令牌
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        解码并验证令牌
        :param token: JWT令牌
        :return: 解码后的数据或None（如果验证失败）
        """
        try:
            # 首先检查令牌是否在黑名单中
            if token_blacklist.is_blacklisted(token):
                logger.warning("Token is blacklisted")
                return None
                
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"Token decode error: {str(e)}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        验证令牌是否有效
        :param token: JWT令牌
        :return: 是否有效
        """
        payload = TokenService.decode_token(token)
        if not payload:
            return False
            
        # 检查令牌是否过期
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
            return False
            
        return True
    
    @staticmethod
    def check_token_needs_refresh(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        检查令牌是否需要续期
        :param token: JWT令牌
        :return: (是否需要续期, 令牌数据)
        """
        payload = TokenService.decode_token(token)
        print("payload是",payload)
        if not payload:
            return False, None
            
        exp = payload.get("exp")
        if not exp:
            return False, None
            
        # 计算距离过期还有多少分钟
        exp_time = datetime.fromtimestamp(exp)
        remaining_time = exp_time - datetime.utcnow()
        
        # 如果剩余时间小于设定的阈值，需要续期
        needs_refresh = remaining_time <= timedelta(minutes=AUTO_REFRESH_BEFORE_EXPIRY_MINUTES)
        return needs_refresh, payload
    
    @staticmethod
    def revoke_token(token: str) -> None:
        """
        吊销令牌（加入黑名单）
        :param token: JWT令牌
        """
        try:
            payload = TokenService.decode_token(token)
            if payload and "exp" in payload:
                expire_time = datetime.fromtimestamp(payload["exp"])
                token_blacklist.add_to_blacklist(token, expire_time)
                logger.info("Token revoked and added to blacklist")
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
    
    @staticmethod
    async def verify_admin(token: str) -> bool:
        """
        验证用户是否是管理员
        :param token: JWT令牌
        :return: 是否是管理员
        """
        payload = TokenService.decode_token(token)
        if not payload:
            return False
            
        username = payload.get("sub")
        if not username:
            return False
            
        try:
            async with AsyncSessionLocal() as db:
                user = await crud.get_user_by_filter(db, {"username": username})
                return user and user.is_admin
        except Exception as e:
            logger.error(f"Admin verification error: {str(e)}")
            return False

def get_token_from_request(request: Request) -> Optional[str]:
    """
    从请求中获取Token
    优先从Authorization头获取，其次从cookie获取
    :param request: 请求对象
    :return: Token字符串或None
    """
    # 从Authorization头获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    return None

async def get_current_user(request) -> Optional[Dict[str, Any]]:
    """
    获取当前登录用户信息
    :param request: 请求对象
    :return: 用户信息或None
    """
    token = get_token_from_request(request)
    if not token:
        return None
        
    payload = TokenService.decode_token(token)
    if not payload:
        return None
        
    username = payload.get("sub")
    if not username:
        return None
        
    try:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_filter(db, {"username": username})
            return user.to_dict() if user else None
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return None 