from datetime import datetime
from typing import Dict, Set
import threading
from core.logger import setup_logger

# 设置日志记录器
logger = setup_logger('token_blacklist')

class TokenBlacklist:
    """令牌黑名单管理类"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # 初始化黑名单集合和过期时间映射
                cls._instance.blacklist = set()  
                cls._instance.expire_times = {}   
            return cls._instance
    
    def add_to_blacklist(self, token: str, expire_time: datetime) -> None:
        """
        将令牌添加到黑名单
        :param token: 要加入黑名单的令牌
        :param expire_time: 令牌的过期时间
        """
        with self._lock:
            self.blacklist.add(token)
            self.expire_times[token] = expire_time
            logger.info(f"Token added to blacklist, expires at {expire_time}")
    
    def is_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        :param token: 要检查的令牌
        :return: 是否在黑名单中
        """
        with self._lock:
            # 如果令牌在黑名单中且未过期，返回True
            if token in self.blacklist:
                expire_time = self.expire_times.get(token)
                if expire_time and expire_time > datetime.utcnow():
                    return True
                # 如果令牌已过期，从黑名单中移除
                self.remove_from_blacklist(token)
            return False
    
    def remove_from_blacklist(self, token: str) -> None:
        """
        从黑名单中移除令牌
        :param token: 要移除的令牌
        """
        with self._lock:
            self.blacklist.discard(token)
            self.expire_times.pop(token, None)
            logger.info(f"Token removed from blacklist")
    
    def cleanup_expired_tokens(self) -> None:
        """
        清理已过期的令牌
        """
        with self._lock:
            current_time = datetime.utcnow()
            expired_tokens = [
                token for token, expire_time in self.expire_times.items()
                if expire_time <= current_time
            ]
            
            for token in expired_tokens:
                self.remove_from_blacklist(token)
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

# 创建全局实例
token_blacklist = TokenBlacklist() 