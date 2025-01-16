"""
    定义复杂查询
    处理复杂的数据库查询逻辑，例如多表关联查询、聚合查询、排序、分页等。
    职责：解耦复杂逻辑，方便复用。
"""

from sqlalchemy import select
from apps.products.models import Product
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from robyn import status_codes

async def get_products_by_category(category: str):
    """
    根据分类查询产品
    """
    try:
        async with AsyncSessionLocal() as db:
            query = select(Product).where(Product.category == category)
            result = await db.execute(query)
            products = result.scalars().all()
            
            if not products:
                return ApiResponse.not_found("该分类下没有产品")
            
            products_data = [product.to_dict() for product in products]
            return ApiResponse.success(data=products_data)
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取分类产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_products_by_price_range(min_price: float, max_price: float):
    """
    根据价格范围查询产品
    """
    try:
        async with AsyncSessionLocal() as db:
            query = select(Product).where(Product.price >= min_price, Product.price <= max_price)
            result = await db.execute(query)
            products = result.scalars().all()
            
            if not products:
                return ApiResponse.not_found("该价格范围内没有产品")
            
            products_data = [product.to_dict() for product in products]
            return ApiResponse.success(data=products_data)
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取价格范围产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def search_products(keyword: str):
    """
    搜索产品（名称和描述）
    """
    try:
        async with AsyncSessionLocal() as db:
            query = select(Product).where(
                (Product.name.ilike(f"%{keyword}%")) |
                (Product.description.ilike(f"%{keyword}%"))
            )
            result = await db.execute(query)
            products = result.scalars().all()
            
            if not products:
                return ApiResponse.not_found("未找到相关产品")
            
            products_data = [product.to_dict() for product in products]
            return ApiResponse.success(data=products_data)
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="搜索产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
