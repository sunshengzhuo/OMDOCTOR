"""药材 ORM 模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer, Numeric, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Herb(Base):
    """中药材字典"""
    __tablename__ = "herbs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="正名")
    aliases: Mapped[dict | None] = mapped_column(JSON, comment="异名列表")
    category: Mapped[str | None] = mapped_column(String(30), comment="分类: 解表药/清热药/...")
    nature: Mapped[str | None] = mapped_column(String(20), comment="药性: 寒/热/温/凉/平")
    flavor: Mapped[str | None] = mapped_column(String(50), comment="药味: 甘/苦/辛/...")
    meridian_tropism: Mapped[str | None] = mapped_column(String(100), comment="归经")
    efficacy: Mapped[str | None] = mapped_column(Text, comment="功效")
    dosage_min: Mapped[float | None] = mapped_column(Numeric(6, 2), comment="最小剂量(g)")
    dosage_max: Mapped[float | None] = mapped_column(Numeric(6, 2), comment="最大剂量(g)")
    toxicity: Mapped[str] = mapped_column(String(10), default="无毒", comment="毒性")
    pregnancy_contraindicated: Mapped[bool] = mapped_column(Boolean, default=False, comment="孕妇禁忌")
    storage_condition: Mapped[str | None] = mapped_column(String(100), comment="储存条件")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")

    # 关系
    inventory_items: Mapped[list["HerbInventory"]] = relationship(back_populates="herb", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Herb(id={self.id}, name='{self.name}')>"


class IncompatibilityRule(Base):
    """配伍禁忌规则 (十八反/十九畏)"""
    __tablename__ = "incompatibility_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="十八反/十九畏")
    herb_a_id: Mapped[int] = mapped_column(Integer, ForeignKey("herbs.id"), nullable=False)
    herb_b_id: Mapped[int] = mapped_column(Integer, ForeignKey("herbs.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, comment="禁忌说明")
    source: Mapped[str | None] = mapped_column(String(100), comment="出处")

    def __repr__(self):
        return f"<IncompatibilityRule(type='{self.rule_type}', a={self.herb_a_id}, b={self.herb_b_id})>"


class HerbInventory(Base):
    """中药饮片库存"""
    __tablename__ = "herb_inventory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    herb_id: Mapped[int] = mapped_column(Integer, ForeignKey("herbs.id"), nullable=False)
    batch_number: Mapped[str | None] = mapped_column(String(50), comment="批号")
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="库存量(g)")
    unit_price: Mapped[float | None] = mapped_column(Numeric(8, 2), comment="单价(元/g)")
    purchase_date: Mapped[str | None] = mapped_column(String(10), comment="购入日期")
    expiry_date: Mapped[str | None] = mapped_column(String(10), comment="有效期")
    supplier: Mapped[str | None] = mapped_column(String(100), comment="供应商")
    min_stock: Mapped[float | None] = mapped_column(Numeric(10, 2), comment="最低库存预警")
    location: Mapped[str | None] = mapped_column(String(50), comment="存放位置")
    status: Mapped[str] = mapped_column(String(20), default="正常", comment="状态")

    herb: Mapped["Herb"] = relationship(back_populates="inventory_items")

    def __repr__(self):
        return f"<HerbInventory(herb_id={self.herb_id}, qty={self.quantity})>"


class InventoryTransaction(Base):
    """库存出入库记录"""
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    herb_id: Mapped[int] = mapped_column(Integer, ForeignKey("herbs.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False, comment="入库/出库/损耗")
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    before_quantity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    after_quantity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    reference_id: Mapped[int | None] = mapped_column(Integer, comment="关联处方ID")
    note: Mapped[str | None] = mapped_column(Text, comment="备注")
    operator: Mapped[str | None] = mapped_column(String(50), comment="操作人")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<InventoryTransaction(herb_id={self.herb_id}, type='{self.transaction_type}', qty={self.quantity})>"
