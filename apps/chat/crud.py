from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from core.database import AsyncSessionLocal
from core.logger import setup_logger
from common.utils.dynamic_query import dynamic_query
from .models import ChatSession, ChatMessage
from typing import List, Optional, Dict

# 设置日志记录器
logger = setup_logger('user_crud')

"""
    定义聊天应用(会话、消息)的CRUD操作, 解耦API和数据库操作
    只定义 单表的基础操作 和 动态查询功能
    CRUD层函数 返回值一律为 ORM实例对象
"""

class ChatCRUD:
    """聊天系统数据库操作"""

    # ------------------ 会话操作 ------------------
    @staticmethod
    async def create_session(db: AsyncSession, session_id: str, user_id: str, title: str = "新会话") -> ChatSession:
        """创建新会话"""
        new_session = ChatSession(session_id=session_id, user_id=user_id, title=title)
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session

    @staticmethod
    async def get_session(db: AsyncSession, session_id: str) -> Optional[ChatSession]:
        """获取单个会话详情"""
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.session_id == session_id)
            .where(ChatSession.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sessions(
        db: AsyncSession, 
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[ChatSession]:
        """
        获取用户所有会话列表(分页，一页20条)
        接收 user_id
        返回 查询的session对象
        """
        page = max(1, page)
        page_size = min(max(1, page_size), 20)  # 限制每页最多20条
        offset = (page - 1) * page_size
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.is_deleted == False)
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        return result.scalars().all()

    @staticmethod
    async def soft_delete_session(db: AsyncSession, session_id: str) -> bool:
        """软删除会话"""
        result = await db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(is_deleted=True)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_session_title(db: AsyncSession, session_id: str, new_title: str) -> bool:
        """更新会话标题"""
        result = await db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(title=new_title)
        )
        await db.commit()
        return result.rowcount > 0

    # ------------------ 消息操作 ------------------
    @staticmethod
    async def create_message(
        db: AsyncSession,
        session_id: str,
        content: str,
        role: str
    ) -> ChatMessage:
        """创建新消息并更新会话计数"""
        # 需要添加消息ID自增逻辑
        last_message = await db.execute(
            select(func.max(ChatMessage.message_id))
            .where(ChatMessage.session_id == session_id)
        )
        new_message_id = (last_message.scalar() or 0) + 1

        # 创建消息
        new_message = ChatMessage(
            session_id=session_id,
            content=content,
            role=role
        )
        db.add(new_message)
        
        # 更新会话消息计数
        await db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(message_count=ChatSession.message_count + 1)
        )
        
        await db.commit()
        await db.refresh(new_message)
        return new_message

    @staticmethod
    async def get_message(db: AsyncSession, session_id: str, message_id: int) -> Optional[ChatMessage]:
        """获取单条消息"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .where(ChatMessage.message_id == message_id)
            .where(ChatMessage.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_messages(
        db: AsyncSession,
        session_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> List[ChatMessage]:
        """批量获取会话消息历史"""
        # 确保分页参数有效性
        page = max(1, page)
        page_size = min(max(1, page_size), 50)  # 限制每页最多50条
        offset = (page - 1) * page_size
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .where(ChatMessage.is_deleted == False)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()


    @staticmethod
    async def soft_delete_message(db: AsyncSession, message_id: int) -> bool:
        """软删除消息"""
        result = await db.execute(
            update(ChatMessage)
            .where(ChatMessage.message_id == message_id)
            .values(is_deleted=True)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_message_content(db: AsyncSession, message_id: int, new_content: str) -> bool:
        """修改消息内容(仅限role:user的消息)"""
        result = await db.execute(
            update(ChatMessage)
            .where(ChatMessage.message_id == message_id)
            .where(ChatMessage.role == "user")
            .values(content=new_content)
        )
        await db.commit()
        return result.rowcount > 0

    # ------------------ 统计操作 ------------------
    @staticmethod
    async def get_session_message_count(db: AsyncSession, session_id: str) -> int:
        """获取会话实际消息数量"""
        result = await db.execute(
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .where(ChatMessage.is_deleted == False)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_user_session_count(db: AsyncSession, user_id: str) -> int:
        """获取用户有效会话总数"""
        result = await db.execute(
            select(func.count())
            .select_from(ChatSession)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.is_deleted == False)
        )
        return result.scalar() or 0

    # ------------------ 批量操作 ------------------
    @staticmethod
    async def batch_create_messages(db: AsyncSession, messages: List[Dict]) -> bool:
        """批量创建消息（用于导入）"""
        try:
            db.add_all([ChatMessage(**msg) for msg in messages])
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"批量创建消息失败: {str(e)}")
            await db.rollback()
            return False



