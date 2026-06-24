"""智能问诊路由"""
import base64
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.diagnosis import (
    DiagnosisChatRequest, DiagnosisChatResponse,
    DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse,
)
from app.config import settings

router = APIRouter(prefix="/diagnosis", tags=["智能问诊"])


@router.post("/chat", response_model=DiagnosisChatResponse, summary="对话式问诊")
async def diagnosis_chat(data: DiagnosisChatRequest, db: Session = Depends(get_db)):
    """对话式智能问诊 — DeepSeek + RAG"""
    if not settings.deepseek_api_key:
        return DiagnosisChatResponse(
            conversation_id=data.conversation_id or "demo",
            reply="⚠️ DeepSeek API Key 未配置，请在系统设置中配置后使用智能问诊功能。",
            safety_warnings=[],
        )

    from app.services.ai_diagnosis_service import diagnosis_service
    result = await diagnosis_service.chat(
        message=data.message,
        images=data.images,
        conversation_id=data.conversation_id,
        patient_id=data.patient_id,
        visit_id=data.visit_id,
        db=db,
    )
    return DiagnosisChatResponse(**result)


@router.post("/analyze", response_model=DiagnosisAnalyzeResponse, summary="四诊辨证分析")
async def diagnosis_analyze(data: DiagnosisAnalyzeRequest, db: Session = Depends(get_db)):
    """四诊信息 → 辨证分析 — DeepSeek + RAG"""
    if not settings.deepseek_api_key:
        return DiagnosisAnalyzeResponse(
            syndrome_analysis="⚠️ DeepSeek API Key 未配置",
            safety_warnings=["请在系统设置中配置 DeepSeek API Key"],
        )

    from app.services.ai_diagnosis_service import diagnosis_service
    result = await diagnosis_service.analyze(
        observation=data.observation,
        auscultation=data.auscultation,
        inquiry=data.inquiry,
        palpation=data.palpation,
        tongue_body=data.tongue_body,
        tongue_coat=data.tongue_coat,
        pulse=data.pulse,
        chief_complaint=data.chief_complaint,
        patient_gender=data.patient_gender,
        is_pregnant=data.is_pregnant,
        tongue_image=data.tongue_image,
        face_image=data.face_image,
        lab_report_images=data.lab_report_images,
        db=db,
    )
    return DiagnosisAnalyzeResponse(**result)


@router.post("/upload-image", summary="上传诊断图片")
async def upload_diagnosis_image(file: UploadFile = File(...)):
    """上传舌苔/面色/化验单图片，返回 base64 data URL"""
    # 限制文件大小 5MB
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过5MB")
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    # 编码为 base64 data URL
    b64 = base64.b64encode(content).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{b64}"
    return {"data_url": data_url, "filename": file.filename}


@router.get("/history", summary="问诊历史")
def diagnosis_history(limit: int = 20, db: Session = Depends(get_db)):
    """获取问诊历史记录"""
    return []


@router.get("/status", summary="AI 服务状态")
def diagnosis_status():
    """获取 AI 服务状态"""
    from app.services.vector_store import vector_store
    stats = vector_store.get_stats()
    return {
        "deepseek_configured": bool(settings.deepseek_api_key),
        "deepseek_model": settings.deepseek_model,
        "vector_store_available": stats.get("available", False),
        "vector_store_count": stats.get("count", 0),
    }
