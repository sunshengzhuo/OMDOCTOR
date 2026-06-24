"""处方管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.prescription import ClassicFormula, Prescription, PrescriptionItem
from app.models.herb import IncompatibilityRule, Herb
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionResponse, PrescriptionItemResponse,
    ClassicFormulaResponse,
)

router = APIRouter(prefix="/prescriptions", tags=["处方管理"])


# ── 经典方剂库（必须在 /{prescription_id} 之前，否则会被动态路由捕获） ──

@router.get("/classic-formulas", response_model=list[ClassicFormulaResponse], summary="经典方列表")
def list_classic_formulas(
    source: str | None = Query(None, description="出处筛选"),
    search: str | None = Query(None, description="搜索方名"),
    db: Session = Depends(get_db),
):
    query = db.query(ClassicFormula)
    if source:
        query = query.filter(ClassicFormula.source == source)
    if search:
        query = query.filter(ClassicFormula.name.contains(search))
    return query.order_by(ClassicFormula.source, ClassicFormula.name).all()


@router.get("/classic-formulas/{formula_id}", response_model=ClassicFormulaResponse, summary="经典方详情")
def get_classic_formula(formula_id: int, db: Session = Depends(get_db)):
    formula = db.query(ClassicFormula).filter(ClassicFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="方剂不存在")
    return formula


# ── 处方 CRUD ──

@router.get("", response_model=list[PrescriptionResponse], summary="处方列表")
def list_prescriptions(
    patient_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Prescription).options(joinedload(Prescription.items))
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if status:
        query = query.filter(Prescription.status == status)
    return query.order_by(Prescription.created_at.desc()).limit(limit).all()


@router.post("", response_model=PrescriptionResponse, summary="开具处方")
def create_prescription(data: PrescriptionCreate, db: Session = Depends(get_db)):
    """开具处方 — 自动校验配伍禁忌和剂量"""
    herb_ids = [item.herb_id for item in data.items]

    # 配伍禁忌检查
    conflicts = db.query(IncompatibilityRule).filter(
        (IncompatibilityRule.herb_a_id.in_(herb_ids)) & (IncompatibilityRule.herb_b_id.in_(herb_ids))
    ).all()

    if conflicts:
        herbs = db.query(Herb).filter(Herb.id.in_(herb_ids)).all()
        herb_map = {h.id: h.name for h in herbs}
        conflict_names = [
            f"{herb_map.get(c.herb_a_id, '?')} + {herb_map.get(c.herb_b_id, '?')} ({c.rule_type})"
            for c in conflicts
        ]
        raise HTTPException(
            status_code=400,
            detail=f"配伍禁忌冲突: {', '.join(conflict_names)}",
        )

    # 剂量检查
    herbs = db.query(Herb).filter(Herb.id.in_(herb_ids)).all()
    herb_map = {h.id: h for h in herbs}
    for item in data.items:
        herb = herb_map.get(item.herb_id)
        if herb and herb.dosage_max and item.dose > float(herb.dosage_max):
            raise HTTPException(
                status_code=400,
                detail=f"剂量超限: {herb.name} 最大剂量{herb.dosage_max}g，实际{item.dose}g",
            )

    # 创建处方
    prescription = Prescription(
        visit_id=data.visit_id,
        patient_id=data.patient_id,
        formula_name=data.formula_name,
        is_classic=data.is_classic,
        classic_formula_id=data.classic_formula_id,
        preparation_method=data.preparation_method,
        administration=data.administration,
        doses=data.doses,
        doctor_notes=data.doctor_notes,
    )
    db.add(prescription)
    db.flush()

    # 创建药味明细
    for item_data in data.items:
        item = PrescriptionItem(
            prescription_id=prescription.id,
            herb_id=item_data.herb_id,
            herb_name=item_data.herb_name,
            dose=item_data.dose,
            special_method=item_data.special_method,
            is_king_herb=item_data.is_king_herb,
            note=item_data.note,
        )
        db.add(item)

    db.commit()
    db.refresh(prescription)
    return prescription


@router.get("/{prescription_id}", response_model=PrescriptionResponse, summary="处方详情")
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).options(joinedload(Prescription.items)).filter(
        Prescription.id == prescription_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")
    return prescription


@router.put("/{prescription_id}/review", response_model=PrescriptionResponse, summary="审核处方")
def review_prescription(prescription_id: int, reviewer_id: int = 1, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")
    if prescription.status != "已开":
        raise HTTPException(status_code=400, detail=f"处方状态为'{prescription.status}'，不可审核")
    prescription.status = "已审核"
    prescription.reviewed_by = reviewer_id
    db.commit()
    db.refresh(prescription)
    return prescription


@router.put("/{prescription_id}/dispense", response_model=PrescriptionResponse, summary="发药(扣减库存)")
def dispense_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """发药：扣减库存，更新处方状态"""
    from app.models.herb import HerbInventory, InventoryTransaction

    prescription = db.query(Prescription).options(joinedload(Prescription.items)).filter(
        Prescription.id == prescription_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")
    if prescription.status != "已审核":
        raise HTTPException(status_code=400, detail="处方未审核，不可发药")

    # 扣减库存
    for item in prescription.items:
        total_qty = float(item.dose) * prescription.doses
        available = db.query(HerbInventory).filter(
            HerbInventory.herb_id == item.herb_id,
            HerbInventory.status == "正常",
        ).all()
        avail_total = sum(float(inv.quantity) for inv in available)

        if avail_total < total_qty:
            raise HTTPException(
                status_code=400,
                detail=f"库存不足: {item.herb_name} 需{total_qty}g，可用{avail_total}g",
            )

        remaining = total_qty
        for inv in available:
            if remaining <= 0:
                break
            deduct = min(float(inv.quantity), remaining)
            inv.quantity = float(inv.quantity) - deduct
            remaining -= deduct

        # 记录出库
        txn = InventoryTransaction(
            herb_id=item.herb_id,
            transaction_type="出库",
            quantity=total_qty,
            before_quantity=avail_total,
            after_quantity=avail_total - total_qty,
            reference_id=prescription.id,
            note=f"处方#{prescription.id}发药",
        )
        db.add(txn)

    prescription.status = "已发药"
    db.commit()
    db.refresh(prescription)
    return prescription
