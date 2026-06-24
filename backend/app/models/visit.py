"""就诊记录 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Visit(Base):
    """就诊记录 — 中医特色: 含四诊信息 + 辨证论治"""
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date: Mapped[str] = mapped_column(String(20), nullable=False, comment="就诊日期")

    # 主诉与病史
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False, comment="主诉")
    present_illness: Mapped[str | None] = mapped_column(Text, comment="现病史")

    # 四诊信息 (核心中医特色字段)
    observation: Mapped[str | None] = mapped_column(Text, comment="望诊: 面色、神态、形体")
    auscultation: Mapped[str | None] = mapped_column(Text, comment="闻诊: 语声、呼吸、气味")
    inquiry: Mapped[str | None] = mapped_column(Text, comment="问诊: 寒热汗出饮食睡眠二便等")
    palpation: Mapped[str | None] = mapped_column(Text, comment="切诊: 脉象描述")
    tongue_body: Mapped[str | None] = mapped_column(String(50), comment="舌质: 如'舌红'")
    tongue_coat: Mapped[str | None] = mapped_column(String(50), comment="舌苔: 如'苔黄腻'")
    pulse: Mapped[str | None] = mapped_column(String(100), comment="脉象: 如'弦滑数'")

    # 中医诊断 (理法方药)
    tcm_disease: Mapped[str | None] = mapped_column(String(100), comment="中医病名: 如'胃脘痛'")
    tcm_syndrome: Mapped[str | None] = mapped_column(String(100), comment="证型: 如'肝气犯胃证'")
    treatment_method: Mapped[str | None] = mapped_column(String(100), comment="治法: 如'疏肝理气'")

    # 医嘱
    doctor_notes: Mapped[str | None] = mapped_column(Text, comment="医嘱/调护")
    doctor_id: Mapped[int | None] = mapped_column(Integer, comment="接诊医师ID")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    patient: Mapped["Patient"] = relationship(back_populates="visits")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="visit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Visit(id={self.id}, patient_id={self.patient_id}, date='{self.visit_date}')>"
