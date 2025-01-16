from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from pathlib import Path

"""
异步数据库配置
"""

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, "robyn_data.db")

# 创建异步数据库引擎
engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_PATH}",
    echo=True,  # 设置为 True 可以看到 SQL 语句
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 创建异步基类
class Base(DeclarativeBase):
    pass

# 获取异步数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()