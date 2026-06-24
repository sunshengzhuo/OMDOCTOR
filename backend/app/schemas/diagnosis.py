"""智能问诊相关 Pydantic 模型"""
from datetime import datetime
from pydantic import BaseModel, Field


class DiagnosisChatRequest(BaseModel):
    """对话式问诊请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    images: list[str] | None = Field(None, description="图片base64 data URL列表")
    conversation_id: str | None = Field(None, description="会话ID(延续对话)")
    patient_id: int | None = Field(None, description="关联患者ID")
    visit_id: int | None = Field(None, description="关联就诊ID")


class DiagnosisAnalyzeRequest(BaseModel):
    """四诊信息辨证分析请求"""
    observation: str | None = Field(None, description="望诊")
    auscultation: str | None = Field(None, description="闻诊")
    inquiry: str | None = Field(None, description="问诊")
    palpation: str | None = Field(None, description="切诊")
    tongue_body: str | None = Field(None, description="舌质")
    tongue_coat: str | None = Field(None, description="舌苔")
    pulse: str | None = Field(None, description="脉象")
    chief_complaint: str | None = Field(None, description="主诉")
    patient_gender: str | None = Field(None, description="患者性别")
    is_pregnant: bool | None = Field(None, description="是否孕妇")
    tongue_image: str | None = Field(None, description="舌象图片base64 data URL")
    face_image: str | None = Field(None, description="面色图片base64 data URL")
    lab_report_images: list[str] | None = Field(None, description="化验单/影像报告图片列表")


class DiagnosisChatResponse(BaseModel):
    """问诊对话响应"""
    conversation_id: str
    reply: str
    suggested_syndrome: str | None = Field(None, description="建议证型")
    suggested_formula: str | None = Field(None, description="建议方剂")
    safety_warnings: list[str] = Field(default_factory=list, description="安全警告")


class DiagnosisAnalyzeResponse(BaseModel):
    """辨证分析响应"""
    syndrome_analysis: str = Field(..., description="辨证分析")
    tcm_disease: str | None = Field(None, description="中医病名")
    tcm_syndrome: str | None = Field(None, description="证型")
    treatment_method: str | None = Field(None, description="治法")
    recommended_formulas: list[dict] = Field(default_factory=list, description="推荐方剂")
    safety_warnings: list[str] = Field(default_factory=list, description="安全警告")
    references: list[str] = Field(default_factory=list, description="参考出处")


# ── 会话管理 ──

class ConversationCreate(BaseModel):
    title: str | None = Field(None, description="对话标题")
    patient_id: int | None = Field(None, description="关联患者ID")


class ConversationUpdate(BaseModel):
    title: str | None = Field(None, description="新标题")


class ConversationSummary(BaseModel):
    """侧边栏对话摘要"""
    uuid: str
    title: str | None
    message_count: int
    last_message_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """对话详情"""
    uuid: str
    title: str | None
    patient_id: int | None
    message_count: int
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    total: int
    items: list[ConversationSummary]
    page: int
    page_size: int


class MessageResponse(BaseModel):
    """消息"""
    id: int
    seq: int
    role: str
    content: str
    images: list | None = None
    warnings: list | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    total: int
    items: list[MessageResponse]
