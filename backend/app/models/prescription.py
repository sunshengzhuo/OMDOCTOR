"""处方 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer, Numeric, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClassicFormula(Base):
    """经典方剂库"""
    __tablename__ = "classic_formulas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="方名")
    aliases: Mapped[dict | None] = mapped_column(JSON, comment="别名")
    source: Mapped[str | None] = mapped_column(String(100), comment="出处: 伤寒论/金匮要略/...")
    composition: Mapped[dict] = mapped_column(JSON, nullable=False, comment="组成")
    efficacy: Mapped[str | None] = mapped_column(Text, comment="功效")
    indications: Mapped[str | None] = mapped_column(Text, comment="主治")
    usage: Mapped[str | None] = mapped_column(Text, comment="用法")
    modifications: Mapped[dict | None] = mapped_column(JSON, comment="加减变化")

    def __repr__(self):
        return f"<ClassicFormula(id={self.id}, name='{self.name}')>"


class Prescription(Base):
    """处方记录"""
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visit_id: Mapped[int] = mapped_column(Integer, ForeignKey("visits.id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id"), nullable=False)
    formula_name: Mapped[str | None] = mapped_column(String(100), comment="方名")
    is_classic: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否经典方")
    classic_formula_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("classic_formulas.id"))
    preparation_method: Mapped[str] = mapped_column(String(50), default="水煎服", comment="煎法")
    administration: Mapped[str | None] = mapped_column(String(100), comment="服法")
    doses: Mapped[int] = mapped_column(Integer, default=7, comment="剂数")
    doctor_notes: Mapped[str | None] = mapped_column(Text, comment="医嘱")
    total_price: Mapped[float | None] = mapped_column(Numeric(8, 2), comment="总价")
    status: Mapped[str] = mapped_column(String(20), default="已开", comment="状态")
    reviewed_by: Mapped[int | None] = mapped_column(Integer, comment="审核人")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    visit: Mapped["Visit"] = relationship(back_populates="prescriptions")
    items: Mapped[list["PrescriptionItem"]] = relationship(back_populates="prescription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription(id={self.id}, formula='{self.formula_name}', status='{self.status}')>"


class PrescriptionItem(Base):
    """处方药味明细"""
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    herb_id: Mapped[int] = mapped_column(Integer, ForeignKey("herbs.id"), nullable=False)
    herb_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="药材名(冗余)")
    dose: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, comment="剂量(g)")
    special_method: Mapped[str | None] = mapped_column(String(20), comment="特殊煎法")
    is_king_herb: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否君药")
    note: Mapped[str | None] = mapped_column(String(100), comment="备注")

    prescription: Mapped["Prescription"] = relationship(back_populates="items")

    def __repr__(self):
        return f"<PrescriptionItem(herb='{self.herb_name}', dose={self.dose}g)>"
