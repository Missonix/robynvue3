from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.products.models import Product
from common.utils.dynamic_query import dynamic_query
# from sqlalchemy.future import select

"""
    定义商城CRUD操作, 解耦API和数据库操作
    只定义 单表的基础操作 和 动态查询功能
    CRUD层函数 返回值一律为 ORM实例对象
"""

# 单表的基础操作
async def get_product(db: AsyncSession, product_id: int):
    """
    根据产品ID获取单个产品
    """
    return await db.get(Product, product_id)

async def create_product(db: AsyncSession, product: dict):
    """
    创建产品
    """
    new_product = Product(**product)
    db.add(new_product)  # 直接添加 Product 实例
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def update_product(db: AsyncSession, product_id: int, product_data: dict):
    """
    更新产品
    """
    target_product = await db.get(Product, product_id)
    if target_product is None:
        raise Exception("Product not found")
    
    for key, value in product_data.items(): # 更新目标产品
        setattr(target_product, key, value) # 设置目标产品的属性
    await db.commit() # 提交事务
    await db.refresh(target_product) # 刷新目标产品
    return target_product

async def delete_product(db: AsyncSession, product_id: int):
    """
    删除产品
    """
    target_product = await db.get(Product, product_id)
    if target_product is None:
        raise Exception("Product not found")
    
    await db.delete(target_product)
    await db.commit()
    return target_product



# 动态查询
async def get_product_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询产品
    """
    query = await dynamic_query(db, Product, filters)
    result = await db.execute(query)
    return result.first()


async def get_products_by_filters(db: AsyncSession, filters=None, order_by=None, limit=None, offset=None):
    """
    批量查询产品
    """
    query = await dynamic_query(db, Product, filters, order_by, limit, offset)
    result = await db.execute(query)
    return result.scalars().all()

