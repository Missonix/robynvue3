from robyn import Request, Response, jsonify, status_codes
from apps.products import crud
from apps.products.models import Product
from core.database import AsyncSessionLocal
from core.response import ApiResponse

"""
    crud -> services -> api
    服务层:根据业务逻辑整合crud数据操作 封装业务方法 可以由上层函数直接调用
    服务层 应该完成 业务逻辑（如判断数据是否存在、响应失败的处理逻辑）
"""

async def get_product_by_id(request):
    """
    通过产品ID获取单个产品
    """
    try:
        async with AsyncSessionLocal() as db:
            product_id = request.path_params.get("product_id")
            product_obj = await crud.get_product(db, product_id)
            if not product_obj:
                return ApiResponse.not_found("产品不存在")
            return ApiResponse.success(data=product_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_product_by_name(request):
    """
    通过产品名称获取单个产品
    """
    try:
        async with AsyncSessionLocal() as db:
            product_name = request.path_params.get("product_name")
            product_obj = await crud.get_product_by_filter(db, {"name": product_name})
            if not product_obj:
                return ApiResponse.not_found("产品不存在")
            return ApiResponse.success(data=product_obj.to_dict())
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_products_service(request):
    """
    获取所有产品
    """
    try:
        async with AsyncSessionLocal() as db:
            products = await crud.get_products_by_filters(db)
            products_data = [product.to_dict() for product in products]
            return ApiResponse.success(data=products_data)
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="获取产品列表失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def create_product_service(request):
    """
    创建产品
    """
    try:
        product_data = request.json()
        product_name = product_data.get("name")

        if not product_name:
            return ApiResponse.validation_error("产品名称不能为空")
        
        async with AsyncSessionLocal() as db:
            product_exists = await crud.get_product_by_filter(db, {"name": product_name})
            if product_exists:
                return ApiResponse.error(
                    message="产品已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )
            
            try:
                inserted_product_obj = await crud.create_product(db, product_data)
                if not inserted_product_obj:
                    raise Exception("Product creation failed")
                return ApiResponse.success(
                    data=inserted_product_obj.to_dict(),
                    message="产品创建成功"
                )
            except Exception as e:
                raise Exception(f"Database integrity error: {str(e)}")
            
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="创建产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_product_service(request):
    """
    更新产品
    """
    try:
        async with AsyncSessionLocal() as db:
            product_id = request.path_params.get("product_id")
            product_obj = await crud.get_product(db, product_id)
            if not product_obj:
                return ApiResponse.not_found("产品不存在")
            
            updated_product_obj = await crud.update_product(db, product_id, request.json())
            return ApiResponse.success(
                data=updated_product_obj.to_dict(),
                message="产品更新成功"
            )
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="更新产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_product_service(request):
    """
    删除产品
    """
    try:
        async with AsyncSessionLocal() as db:
            product_id = request.path_params.get("product_id")
            product_obj = await crud.get_product(db, product_id)
            if not product_obj:
                return ApiResponse.not_found("产品不存在")
            
            await crud.delete_product(db, product_id)
            return ApiResponse.success(message="产品删除成功")
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="删除产品失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

