from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.users.models import User
from common.utils.dynamic_query import dynamic_query

"""
    定义用户CRUD操作, 解耦API和数据库操作
    只定义 单表的基础操作 和 动态查询功能
    CRUD层函数 返回值一律为 ORM实例对象
"""

# 单表基础操作
async def get_user(db: AsyncSession, user_id: int):
    """
    根据用户ID获取单个用户
    """
    return await db.get(User, user_id)

async def create_user(db: AsyncSession, user: dict):
    """
    创建用户
    """
    new_user = User(**user)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(db: AsyncSession, user_id: int, user_data: dict):
    """
    更新用户
    """
    user = await db.get(User, user_id)
    if user is None:
        raise Exception("User not found")
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    """
    删除用户
    """
    target_user = await db.get(User, user_id)
    if target_user is None:
        raise Exception("User not found")
    
    await db.delete(target_user)
    await db.commit()
    return target_user

# 动态查询
async def get_user_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询用户
    """
    query = await dynamic_query(db, User, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    user = result.scalar_one_or_none()
    return user


async def get_users_by_filters(db: AsyncSession, filters=None, order_by=None, limit=None, offset=None):
    """
    批量查询用户
    """
    query = await dynamic_query(db, User, filters, order_by, limit, offset)
    result = await db.execute(query)
    # 返回所有完整记录（ORM 对象列表）
    return result.scalars().all()



