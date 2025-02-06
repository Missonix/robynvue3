from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from core.database import Base
import logging

logger = logging.getLogger(__name__)


class ChatSession(Base):
    """
    聊天会话模型
    """
    __tablename__ = 'chat_sessions'
    
    session_id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(20), ForeignKey('users.user_id'), index=True, nullable=False)  # 关联用户表
    title = Column(String(100), default="新会话")                  # 会话标题
    message_count = Column(Integer, default=0)                   # 消息条数
    created_at = Column(DateTime, default=datetime.utcnow)        # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最后活动时间
    is_deleted = Column(Boolean, default=False)                   # 软删除标记
    
    # 定义与消息的一对多关系
    messages = relationship("ChatMessage", back_populates="session")
    
    # 添加复合索引
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),  # 按用户和时间查询的复合索引
    )

    def __repr__(self):
        return f"ChatSession(session_id={self.session_id}, user_id={self.user_id}, title={self.title}, message_count={self.message_count}, created_at={self.created_at}, updated_at={self.updated_at}, is_deleted={self.is_deleted})"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted
        }

class ChatMessage(Base):
    """
    聊天消息模型
    """
    __tablename__ = 'chat_messages'
    
    message_id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)                        # 消息内容（使用Text类型支持长文本）
    role = Column(String(20), nullable=False)                     # 消息角色：user/assistant/system
    session_id = Column(String(20), ForeignKey('chat_sessions.session_id'), index=True)  # 关联会话表
    created_at = Column(DateTime, default=datetime.utcnow)      # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    is_deleted = Column(Boolean, default=False)                   # 软删除标记
    
    # 定义与会话的多对一关系
    session = relationship("ChatSession", back_populates="messages")
    
    # 添加索引
    __table_args__ = (
        Index('ix_session_created', 'session_id', 'created_at'),  # 按会话和时间查询的复合索引
    )

    def __repr__(self):
        return f"ChatMessage(message_id={self.message_id}, content={self.content}, role={self.role}, session_id={self.session_id}, created_at={self.created_at}, updated_at={self.updated_at}, is_deleted={self.is_deleted})"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "role": self.role,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted
        }
