import asyncio
from core.database import Base, engine
# 必须导入所有模型
from apps.users.models import User
from apps.products.models import Product
from apps.chat.models import ChatSession, ChatMessage
"""
创建 初始化asyncio数据库
"""


async def init_db():
    print("开始创建数据库...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # 可选：删除所有表
        await conn.run_sync(Base.metadata.create_all)
    print("数据库创建完成！")

if __name__ == "__main__":
    asyncio.run(init_db())



