"""知识库 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class KnowledgeEntry(Base):
    """知识条目"""
    __tablename__ = "knowledge_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    category: Mapped[str] = mapped_column(String(30), nullable=False, comment="分类: 条文/方剂/药材/医案/诊疗规范")
    source: Mapped[str | None] = mapped_column(String(100), comment="出处")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    structured_data: Mapped[dict | None] = mapped_column(JSON, comment="结构化扩展数据")
    vector_id: Mapped[str | None] = mapped_column(String(100), comment="ChromaDB向量ID")
    tags: Mapped[dict | None] = mapped_column(JSON, comment="标签")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (
        Index('ix_knowledge_category', 'category'),
        Index('ix_knowledge_source', 'source'),
        Index('ix_knowledge_cat_source', 'category', 'source'),
    )

    def __repr__(self):
        return f"<KnowledgeEntry(id={self.id}, title='{self.title}', category='{self.category}')>"
