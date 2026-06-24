"""对话 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    """AI 问诊对话"""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, comment="对外 UUID")
    title: Mapped[str | None] = mapped_column(String(200), comment="对话标题")
    patient_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("patients.id"), comment="关联患者")
    message_count: Mapped[int] = mapped_column(Integer, default=0, comment="消息数")
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime, comment="最后消息时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.seq"
    )


class Message(Base):
    """对话消息"""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False, comment="序号")
    role: Mapped[str] = mapped_column(String(10), nullable=False, comment="user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息文本")
    images: Mapped[list | None] = mapped_column(JSON, comment="图片列表")
    warnings: Mapped[list | None] = mapped_column(JSON, comment="安全警告")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
