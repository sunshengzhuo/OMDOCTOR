"""处方相关 Pydantic 模型"""
from datetime import datetime
from pydantic import BaseModel, Field


class PrescriptionItemCreate(BaseModel):
    """处方药味"""
    herb_id: int
    herb_name: str
    dose: float = Field(..., gt=0, description="剂量(g)")
    special_method: str | None = Field(None, description="特殊煎法")
    is_king_herb: bool = False
    note: str | None = None


class PrescriptionCreate(BaseModel):
    """创建处方"""
    visit_id: int
    patient_id: int
    formula_name: str | None = Field(None, description="方名")
    is_classic: bool = False
    classic_formula_id: int | None = None
    preparation_method: str = "水煎服"
    administration: str | None = None
    doses: int = Field(7, ge=1, description="剂数")
    doctor_notes: str | None = None
    items: list[PrescriptionItemCreate] = Field(..., min_length=1, description="药味列表")


class PrescriptionItemResponse(BaseModel):
    """处方药味响应"""
    id: int
    herb_id: int
    herb_name: str
    dose: float
    special_method: str | None
    is_king_herb: bool
    note: str | None

    model_config = {"from_attributes": True}


class PrescriptionResponse(BaseModel):
    """处方响应"""
    id: int
    visit_id: int
    patient_id: int
    formula_name: str | None
    is_classic: bool
    classic_formula_id: int | None
    preparation_method: str
    administration: str | None
    doses: int
    doctor_notes: str | None
    total_price: float | None
    status: str
    reviewed_by: int | None
    created_at: datetime | None
    items: list[PrescriptionItemResponse] = []

    model_config = {"from_attributes": True}


class ClassicFormulaResponse(BaseModel):
    """经典方剂响应"""
    id: int
    name: str
    aliases: list[str] | None
    source: str | None
    composition: list[dict] | None
    efficacy: str | None
    indications: str | None
    usage: str | None
    modifications: list[dict] | None

    model_config = {"from_attributes": True}
