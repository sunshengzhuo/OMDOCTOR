"""智能问诊路由"""
import base64
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.diagnosis import (
    DiagnosisChatRequest, DiagnosisChatResponse,
    DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse,
    ConversationCreate, ConversationUpdate,
    ConversationResponse, ConversationSummary, ConversationListResponse,
    MessageResponse, MessageListResponse,
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


@router.post("/chat/stream", summary="流式对话问诊")
async def diagnosis_chat_stream(data: DiagnosisChatRequest, db: Session = Depends(get_db)):
    """流式对话式智能问诊 — SSE 逐块返回"""
    if not settings.deepseek_api_key:
        async def error_stream():
            yield f"data: {__import__('json').dumps({'type': 'error', 'content': '⚠️ DeepSeek API Key 未配置'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    from app.services.ai_diagnosis_service import diagnosis_service

    async def event_stream():
        async for chunk in diagnosis_service.chat_stream(
            message=data.message,
            images=data.images,
            conversation_id=data.conversation_id,
            patient_id=data.patient_id,
            visit_id=data.visit_id,
            db=db,
        ):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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


@router.post("/analyze/stream", summary="流式四诊辨证分析")
async def diagnosis_analyze_stream(data: DiagnosisAnalyzeRequest, db: Session = Depends(get_db)):
    """流式四诊辨证分析 — SSE 逐块返回"""
    if not settings.deepseek_api_key:
        async def error_stream():
            yield f"data: {__import__('json').dumps({'type': 'error', 'content': '⚠️ DeepSeek API Key 未配置'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    from app.services.ai_diagnosis_service import diagnosis_service

    async def event_stream():
        async for chunk in diagnosis_service.analyze_stream(
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
        ):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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


@router.get("/conversations", response_model=ConversationListResponse, summary="会话列表")
def list_conversations(page: int = 1, page_size: int = 20, search: str | None = None, db: Session = Depends(get_db)):
    """获取会话列表（侧边栏）"""
    from app.models.conversation import Conversation
    q = db.query(Conversation).order_by(Conversation.last_message_at.desc().nulls_last(), Conversation.created_at.desc())
    if search:
        q = q.filter(Conversation.title.contains(search))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return ConversationListResponse(total=total, items=items, page=page, page_size=page_size)


@router.post("/conversations", response_model=ConversationResponse, summary="新建会话")
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):
    """新建对话"""
    import uuid as _uuid
    from app.models.conversation import Conversation
    conv = Conversation(uuid=str(_uuid.uuid4()), title=data.title, patient_id=data.patient_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/conversations/{conv_uuid}", response_model=ConversationResponse, summary="会话详情")
def get_conversation(conv_uuid: str, db: Session = Depends(get_db)):
    from app.models.conversation import Conversation
    conv = db.query(Conversation).filter(Conversation.uuid == conv_uuid).first()
    if not conv:
        raise HTTPException(404, "会话不存在")
    return conv


@router.put("/conversations/{conv_uuid}", response_model=ConversationResponse, summary="更新会话")
def update_conversation(conv_uuid: str, data: ConversationUpdate, db: Session = Depends(get_db)):
    from app.models.conversation import Conversation
    conv = db.query(Conversation).filter(Conversation.uuid == conv_uuid).first()
    if not conv:
        raise HTTPException(404, "会话不存在")
    if data.title is not None:
        conv.title = data.title
    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/conversations/{conv_uuid}", summary="删除会话")
def delete_conversation(conv_uuid: str, db: Session = Depends(get_db)):
    from app.models.conversation import Conversation
    conv = db.query(Conversation).filter(Conversation.uuid == conv_uuid).first()
    if not conv:
        raise HTTPException(404, "会话不存在")
    db.delete(conv)
    db.commit()
    return {"message": "删除成功"}


@router.get("/conversations/{conv_uuid}/messages", response_model=MessageListResponse, summary="会话消息")
def list_messages(conv_uuid: str, db: Session = Depends(get_db)):
    """加载会话的所有消息"""
    from app.models.conversation import Conversation, Message
    conv = db.query(Conversation).filter(Conversation.uuid == conv_uuid).first()
    if not conv:
        raise HTTPException(404, "会话不存在")
    msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.seq).all()
    return MessageListResponse(total=len(msgs), items=msgs)


@router.get("/history", response_model=ConversationListResponse, summary="问诊历史")
def diagnosis_history(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """获取问诊历史记录"""
    from app.models.conversation import Conversation
    q = db.query(Conversation).order_by(Conversation.last_message_at.desc().nulls_last(), Conversation.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return ConversationListResponse(total=total, items=items, page=page, page_size=page_size)


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
