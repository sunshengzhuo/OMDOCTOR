"""患者 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    """患者基本信息"""
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    gender: Mapped[str | None] = mapped_column(String(4), comment="性别: 男/女")
    birth_date: Mapped[str | None] = mapped_column(String(10), comment="出生日期")
    phone: Mapped[str | None] = mapped_column(String(20), comment="电话")
    id_card: Mapped[str | None] = mapped_column(String(18), comment="身份证号")
    address: Mapped[str | None] = mapped_column(Text, comment="地址")
    allergy_history: Mapped[str | None] = mapped_column(Text, comment="过敏史")
    medical_history: Mapped[str | None] = mapped_column(Text, comment="既往史")
    constitution_type: Mapped[str | None] = mapped_column(String(20), comment="体质类型")
    constitution_score: Mapped[dict | None] = mapped_column(JSON, comment="体质评分明细")
    notes: Mapped[str | None] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    visits: Mapped[list["Visit"]] = relationship(back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"
