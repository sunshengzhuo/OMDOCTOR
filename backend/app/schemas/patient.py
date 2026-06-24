"""患者相关 Pydantic 模型"""
from datetime import datetime
from pydantic import BaseModel, Field


# === 患者 ===

class PatientCreate(BaseModel):
    """创建患者"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: str | None = Field(None, description="性别")
    birth_date: str | None = Field(None, description="出生日期")
    phone: str | None = Field(None, description="电话")
    id_card: str | None = Field(None, description="身份证号")
    address: str | None = Field(None, description="地址")
    allergy_history: str | None = Field(None, description="过敏史")
    medical_history: str | None = Field(None, description="既往史")
    notes: str | None = Field(None, description="备注")


class PatientUpdate(BaseModel):
    """更新患者"""
    name: str | None = Field(None, min_length=1, max_length=50)
    gender: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    id_card: str | None = None
    address: str | None = None
    allergy_history: str | None = None
    medical_history: str | None = None
    constitution_type: str | None = None
    constitution_score: dict | None = None
    notes: str | None = None


class PatientResponse(BaseModel):
    """患者响应"""
    id: int
    name: str
    gender: str | None
    birth_date: str | None
    phone: str | None
    id_card: str | None
    address: str | None
    allergy_history: str | None
    medical_history: str | None
    constitution_type: str | None
    constitution_score: dict | None
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    """患者列表响应(分页)"""
    total: int
    items: list[PatientResponse]
    page: int
    page_size: int


# === 就诊记录 ===

class VisitCreate(BaseModel):
    """创建就诊记录"""
    visit_date: str = Field(..., description="就诊日期")
    chief_complaint: str = Field(..., min_length=1, description="主诉")
    present_illness: str | None = Field(None, description="现病史")
    # 四诊信息
    observation: str | None = Field(None, description="望诊")
    auscultation: str | None = Field(None, description="闻诊")
    inquiry: str | None = Field(None, description="问诊")
    palpation: str | None = Field(None, description="切诊")
    tongue_body: str | None = Field(None, description="舌质")
    tongue_coat: str | None = Field(None, description="舌苔")
    pulse: str | None = Field(None, description="脉象")
    # 中医诊断
    tcm_disease: str | None = Field(None, description="中医病名")
    tcm_syndrome: str | None = Field(None, description="证型")
    treatment_method: str | None = Field(None, description="治法")
    # 医嘱
    doctor_notes: str | None = Field(None, description="医嘱")
    doctor_id: int | None = Field(None, description="接诊医师ID")


class VisitResponse(BaseModel):
    """就诊记录响应"""
    id: int
    patient_id: int
    visit_date: str
    chief_complaint: str
    present_illness: str | None
    observation: str | None
    auscultation: str | None
    inquiry: str | None
    palpation: str | None
    tongue_body: str | None
    tongue_coat: str | None
    pulse: str | None
    tcm_disease: str | None
    tcm_syndrome: str | None
    treatment_method: str | None
    doctor_notes: str | None
    doctor_id: int | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


# === 体质辨识 ===

class ConstitutionSubmit(BaseModel):
    """提交体质辨识量表"""
    answers: dict[str, int] = Field(..., description="量表答案: {题目ID: 分值(1-5)}")


class ConstitutionResult(BaseModel):
    """体质辨识结果"""
    primary_type: str = Field(..., description="主要体质类型")
    scores: dict[str, float] = Field(..., description="各体质得分(转化分)")
    secondary_types: list[str] = Field(default_factory=list, description="倾向体质")
