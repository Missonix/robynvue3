import json
import os
import asyncio
from redis.asyncio import Redis
from core.logger import setup_logger
from dotenv import load_dotenv
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载环境变量
load_dotenv(os.path.join(BASE_DIR, "robyn.env"))

# Redis配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_MAX_RETRIES = 3
REDIS_RETRY_DELAY = 1  # 秒

logger = setup_logger('cache')

class Cache:
    _redis = None
    _initialized = False
    
    @classmethod
    async def init(cls):
        """初始化Redis连接"""
        if cls._initialized:
            return
            
        retries = 0
        while retries < REDIS_MAX_RETRIES:
            try:
                logger.info(f"Attempting to connect to Redis at {REDIS_HOST}:{REDIS_PORT} (attempt {retries + 1}/{REDIS_MAX_RETRIES})")
                
                # 使用环境变量配置Redis连接
                cls._redis = Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    encoding='utf-8',
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                
                # 测试连接
                await cls._redis.ping()
                cls._initialized = True
                logger.info("Redis connection established successfully")
                return
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis (attempt {retries + 1}): {str(e)}")
                logger.error(f"Redis configuration: host={REDIS_HOST}, port={REDIS_PORT}, db={REDIS_DB}")
                
                if cls._redis:
                    await cls._redis.close()
                    cls._redis = None
                
                retries += 1
                if retries < REDIS_MAX_RETRIES:
                    logger.info(f"Retrying in {REDIS_RETRY_DELAY} seconds...")
                    await asyncio.sleep(REDIS_RETRY_DELAY)
                else:
                    logger.error("Max retries reached, giving up")
                    raise

    @classmethod
    async def ensure_connection(cls):
        """确保Redis连接可用"""
        if not cls._initialized or not cls._redis:
            await cls.init()
        try:
            await cls._redis.ping()
        except Exception as e:
            logger.error(f"Redis connection lost: {str(e)}")
            cls._initialized = False
            await cls.init()

    @classmethod
    async def set(cls, key: str, value: dict, expire: int = None):
        """
        设置缓存
        :param key: 键
        :param value: 值（字典类型）
        :param expire: 过期时间（秒）
        """
        try:
            await cls.ensure_connection()
            
            # 将字典转换为JSON字符串
            value_str = json.dumps(value)
            logger.debug(f"Setting cache for key: {key}, value: {value_str}")
            
            # 设置值
            await cls._redis.set(key, value_str)
            
            # 如果设置了过期时间
            if expire:
                await cls._redis.expire(key, expire)
                logger.debug(f"Set expiration for key {key}: {expire} seconds")
            
            logger.info(f"Successfully set cache for key: {key}")
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {str(e)}")
            logger.error(f"Value type: {type(value)}, Value: {value}")
            raise

    @classmethod
    async def get(cls, key: str) -> dict:
        """
        获取缓存
        :param key: 键
        :return: 值（字典类型）
        """
        try:
            await cls.ensure_connection()
            
            logger.debug(f"Getting cache for key: {key}")
            value = await cls._redis.get(key)
            
            if value:
                result = json.loads(value)
                logger.debug(f"Cache hit for key {key}: {result}")
                return result
            
            logger.debug(f"Cache miss for key {key}")
            return None
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {str(e)}")
            return None

    @classmethod
    async def close(cls):
        """关闭Redis连接"""
        if cls._redis:
            try:
                await cls._redis.close()
                cls._redis = None
                cls._initialized = False
                logger.info("Redis connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {str(e)}")

    @classmethod
    async def exists(cls, key: str) -> bool:
        """
        检查键是否存在
        :param key: 键
        :return: 是否存在
        """
        try:
            await cls.ensure_connection()
            exists = await cls._redis.exists(key)
            logger.debug(f"Checking existence of key {key}: {exists}")
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check existence for key {key}: {str(e)}")
            return False 

    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        删除缓存
        :param key: 缓存键
        :return: 是否删除成功
        """
        try:
            if not cls._redis:
                logger.error("Redis connection not initialized")
                return False
            
            await cls.ensure_connection()
            await cls._redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return False 