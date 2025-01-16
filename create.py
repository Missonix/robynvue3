import asyncio
from core.database import Base, engine
# 必须导入所有模型
from apps.users.models import User
from apps.products.models import Product

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




# robynproject/
# ├── main.py
# ├── apps/
# │   ├── users/
# │   │   ├── __init__.py
# │   │   ├── api.py
# │   │   ├── api_routes.py
# │   │   ├── models.py
# │   │   ├── crud.py
# │   │   ├── queries.py
# │   │   ├── services.py
# │   │   ├── schemas.py
# │   │   └── views/
# │   │       ├── __init__.py
# │   │       ├── view_routes.py
# │   │       └── views.py
# │   │
# │   └── market/
# │       ├── __init__.py
# │       ├── api.py
# │       ├── api_routes.py
# │       ├── models.py
# │       ├── crud.py
# │       ├── queries.py
# │       ├── services.py
# │       ├── schemas.py
# │       └── views/
# │           ├── __init__.py
# │           ├── view_routes.py
# │           └── views.py
# │
# └── templates/
# │   └── station/
# │   │   ├── base.html
# │   │   ├── index.html
# │   │   ├── about.html
# │   │   ├── service.html
# │   │   ├── market.html
# │   │   ├── users.html
# │   │   └── ...
# │   └── common/
# │   │   ├── not_found.html
# │   │   └── ...
# │   │
# │   └── admin/...
# │
# └── static/
# │   └── station/...
# │   └── common/...
# │   └── admin/...
# │
# └── core/
# │   └── database.py
# │   └── __init__.py
# │
# └── common/
# │   └── __init__.py
# │   └── utils/
# │       └── dynamic_import.py
# │
# └── robyn_data.db
# └──robyn.env