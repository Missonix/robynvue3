import os
from robyn import Request, Response, Robyn, status_codes, HttpMethod
from apps.products.api_routes import products_api_routes # 导入商品服务接口路由
from apps.users.api_routes import users_api_routes # 导入用户接口路由
from apps.users.views.view_routes import users_view_routes # 导入用户视图路由
from apps.chat.api_routes import chat_api_routes # 导入聊天接口路由
from apps.chat.utils import ai_websocket # 导入AI聊天websocket服务
from apps.chat.views.view_routes import chat_view_routes # 导入AI聊天视图路由
from pathlib import Path
from settings import configure_cors
from core.cache import Cache
from core.logger import setup_logger
import asyncio

# 设置日志记录器
logger = setup_logger('main')

# 创建 Robyn 实例
app = Robyn(__file__)

# 配置CORS
configure_cors(app)

# # 配置静态资源
# serve_static_files(app)

# 注册商品服务接口路由
products_api_routes(app)

# 注册用户服务接口路由
users_api_routes(app)

# 注册聊天服务接口路由
chat_api_routes(app)

# 注册用户服务视图路由
users_view_routes(app)

# 注册AI聊天websocket服务
ai_websocket(app)

# 注册AI聊天视图路由
chat_view_routes(app)

# 初始化Redis连接的路由
@app.get("/initialize")
async def initialize(request: Request) -> Response:
    """初始化应用的路由"""
    try:
        await Cache.init()
        logger.info("Application initialized successfully")
        return Response(status_code=status_codes.HTTP_200_OK, description="Initialization successful")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        return Response(
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
            description="Failed to initialize"
        )

# 关闭Redis连接的路由
@app.get("/shutdown")
async def shutdown(request: Request) -> Response:
    """关闭应用的路由"""
    try:
        await Cache.close()
        logger.info("Application shutdown completed")
        return Response(status_code=status_codes.HTTP_200_OK, description="Shutdown successful")
    except Exception as e:
        logger.error(f"Error during application shutdown: {str(e)}")
        return Response(
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
            description="Failed to shutdown"
        )

# 在应用启动时自动初始化Redis
async def init_redis():
    try:
        # 确保Redis连接关闭
        await Cache.close()
        # 重新初始化Redis连接
        await Cache.init()
        # 测试Redis连接
        test_key = "test:connection"
        await Cache.set(test_key, {"test": "value"}, expire=60)
        test_value = await Cache.get(test_key)
        if test_value and test_value.get("test") == "value":
            logger.info("Redis connection test successful")
        else:
            raise Exception("Redis connection test failed")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # 在新的事件循环中初始化Redis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(init_redis())
        logger.info("Redis initialized successfully")
        
        # 启动应用
        app.start(port=8080, host="0.0.0.0")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
