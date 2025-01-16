from robyn import Request
from apps.products.services import (
    get_product_by_id,
    get_product_by_name,
    get_products_service,
    create_product_service,
    update_product_service,
    delete_product_service
)

"""
    定义商城API接口
    接口层 应该专注于 处理基础的数据库操作 并 返回成功的状态码及数据内容
    接口层避免直接暴露在外,应该由服务层调用
"""

async def get_products_api(request: Request):
    """
    获取产品列表 接口
    """
    return await get_products_service(request)

async def create_product_api(request: Request):
    """
    创建产品 接口
    """
    return await create_product_service(request)

async def get_product_by_id_api(request: Request):
    """
    通过产品ID获取单个产品 接口
    """
    return await get_product_by_id(request)

async def get_product_by_name_api(request: Request):
    """
    通过产品名称获取单个产品 接口
    """
    return await get_product_by_name(request)

async def update_product_api(request: Request):
    """
    更新产品 接口
    """
    return await update_product_service(request)

async def delete_product_api(request: Request):
    """
    删除产品 接口
    """
    return await delete_product_service(request)