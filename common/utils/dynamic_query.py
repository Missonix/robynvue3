from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

"""
通用动态查询
返回构造的查询对象：而不是直接执行查询
调用方可以根据具体需求选择 scalars().all() 或 first() 或其他形式的处理方式。
"""

async def dynamic_query(db: AsyncSession, model, filters: dict = None, order_by: list = None, limit: int = None, offset: int = None):
    """
    通用动态查询方法
    :param db: 数据库会话
    :param model: 查询的数据库模型
    :param filters: 查询条件的字典 如 {"name": "John"}
    :param order_by: 排序规则列表 如 [Model.name.asc(), Model.age.desc()]
    :param limit: 查询结果数量限制
    :param offset: 查询起始偏移量
    :return: 查询结果
    """
    query = select(model)

    # 应用过滤条件
    if filters:
        for column, value in filters.items():
            query = query.where(getattr(model, column) == value)

    # 应用排序规则
    if order_by:
        query = query.order_by(*order_by)

    # 应用分页规则
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    return query
