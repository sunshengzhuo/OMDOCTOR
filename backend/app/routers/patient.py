"""患者管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.visit import Visit
from app.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientListResponse,
    VisitCreate, VisitResponse, ConstitutionSubmit, ConstitutionResult,
)

router = APIRouter(prefix="/patients", tags=["患者管理"])


# ── 患者 CRUD ──

@router.get("", response_model=PatientListResponse, summary="患者列表")
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="搜索(姓名/电话)"),
    db: Session = Depends(get_db),
):
    query = db.query(Patient)
    if search:
        query = query.filter(
            (Patient.name.contains(search)) | (Patient.phone.contains(search))
        )
    total = query.count()
    items = query.order_by(Patient.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PatientListResponse(total=total, items=items, page=page, page_size=page_size)


@router.post("", response_model=PatientResponse, summary="新增患者")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientResponse, summary="患者详情")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse, summary="更新患者")
def update_patient(patient_id: int, data: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", summary="删除患者")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    db.delete(patient)
    db.commit()
    return {"message": "删除成功"}


# ── 就诊记录 ──

@router.get("/{patient_id}/visits", response_model=list[VisitResponse], summary="就诊记录列表")
def list_visits(patient_id: int, db: Session = Depends(get_db)):
    visits = db.query(Visit).filter(Visit.patient_id == patient_id).order_by(Visit.visit_date.desc()).all()
    return visits


@router.post("/{patient_id}/visits", response_model=VisitResponse, summary="新增就诊记录")
def create_visit(patient_id: int, data: VisitCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    visit = Visit(patient_id=patient_id, **data.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/{patient_id}/visits/{visit_id}", response_model=VisitResponse, summary="就诊详情")
def get_visit(patient_id: int, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == visit_id, Visit.patient_id == patient_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="就诊记录不存在")
    return visit


# ── 体质辨识 ──

@router.post("/{patient_id}/constitution", response_model=ConstitutionResult, summary="提交体质辨识")
def submit_constitution(patient_id: int, data: ConstitutionSubmit, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    from app.services.constitution_evaluator import evaluate_constitution
    result_dict = evaluate_constitution(data.answers)

    patient.constitution_type = result_dict["primary_type"]
    patient.constitution_score = result_dict["scores"]
    db.commit()

    return ConstitutionResult(**result_dict)


@router.get("/{patient_id}/constitution", response_model=ConstitutionResult | None, summary="获取体质报告")
def get_constitution(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    if not patient.constitution_type:
        return None
    return ConstitutionResult(
        primary_type=patient.constitution_type,
        scores=patient.constitution_score or {},
        secondary_types=[],
    )
