"""ORM 模型导出 — 确保所有模型被导入以便 Alembic 检测"""
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.herb import Herb, IncompatibilityRule, HerbInventory, InventoryTransaction
from app.models.prescription import ClassicFormula, Prescription, PrescriptionItem
from app.models.knowledge import KnowledgeEntry
from app.models.conversation import Conversation, Message

__all__ = [
    "Patient",
    "Visit",
    "Herb",
    "IncompatibilityRule",
    "HerbInventory",
    "InventoryTransaction",
    "ClassicFormula",
    "Prescription",
    "PrescriptionItem",
    "KnowledgeEntry",
    "Conversation",
    "Message",
]
