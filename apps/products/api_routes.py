from robyn import Request
from apps.products.api import (
    get_products_api,
    create_product_api,
    get_product_by_id_api,
    get_product_by_name_api,
    update_product_api,
    delete_product_api
)
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit

def products_api_routes(app):
    """
    注册商城路由
    API 路由 - 用于后端接口
    路由层 应该专注于 处理请求 并 返回响应
    """
    @app.get("/api/products")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)  # 限制每分钟最多100次请求
    async def products_get(request: Request):
        """
        获取所有产品
        """
        return await get_products_api(request)
    
    @app.post("/api/products")
    @error_handler
    @request_logger
    @admin_required  # 只有管理员可以创建产品
    @rate_limit(max_requests=20, time_window=60)  # 限制每分钟最多20次创建请求
    async def products_create(request: Request):
        """
        创建产品
        """
        return await create_product_api(request)
    
    @app.get("/api/products/:product_id")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def product_get_by_id(request: Request):
        """
        通过ID获取单个产品
        """
        return await get_product_by_id_api(request)
    
    @app.get("/api/products/name/:product_name")
    @error_handler
    @request_logger
    @rate_limit(max_requests=100, time_window=60)
    async def product_get_by_name(request: Request):
        """
        通过名称获取单个产品
        """
        return await get_product_by_name_api(request)
    
    @app.put("/api/products/:product_id")
    @error_handler
    @request_logger
    @admin_required  # 只有管理员可以更新产品
    @rate_limit(max_requests=20, time_window=60)
    async def product_update(request: Request):
        """
        更新产品
        """
        return await update_product_api(request)
    
    @app.delete("/api/products/:product_id")
    @error_handler
    @request_logger
    @admin_required  # 只有管理员可以删除产品
    @rate_limit(max_requests=20, time_window=60)
    async def product_delete(request: Request):
        """
        删除产品
        """
        return await delete_product_api(request)