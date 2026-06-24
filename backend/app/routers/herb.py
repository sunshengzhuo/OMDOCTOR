"""药品管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.herb import Herb, IncompatibilityRule, HerbInventory, InventoryTransaction
from app.schemas.herb import (
    HerbCreate, HerbUpdate, HerbResponse,
    IncompatibilityCheckRequest, IncompatibilityCheckResponse, IncompatibilityWarning,
    InventoryIn, InventoryOut, InventoryResponse, InventoryAlert, InventoryUpdate, InventorySummary,
)

router = APIRouter(prefix="/herbs", tags=["药品管理"])


# ── 药材字典 CRUD ──

@router.get("", response_model=list[HerbResponse], summary="药材列表")
def list_herbs(
    category: str | None = Query(None, description="分类筛选"),
    search: str | None = Query(None, description="搜索(正名/异名)"),
    is_active: bool | None = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
):
    query = db.query(Herb)
    if category:
        query = query.filter(Herb.category == category)
    if is_active is not None:
        query = query.filter(Herb.is_active == is_active)
    if search:
        # 搜索正名和异名(JSON字段)
        query = query.filter(Herb.name.contains(search))
        # TODO: 异名搜索需要 SQLite JSON 查询或应用层过滤
    return query.order_by(Herb.category, Herb.name).all()


@router.post("", response_model=HerbResponse, summary="新增药材")
def create_herb(data: HerbCreate, db: Session = Depends(get_db)):
    existing = db.query(Herb).filter(Herb.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"药材'{data.name}'已存在")
    herb = Herb(**data.model_dump())
    db.add(herb)
    db.commit()
    db.refresh(herb)
    return herb


# ── 配伍禁忌检查 ──

@router.post("/incompatibility-check", response_model=IncompatibilityCheckResponse, summary="配伍禁忌检查")
def check_incompatibility(data: IncompatibilityCheckRequest, db: Session = Depends(get_db)):
    """检查一组药材是否存在十八反/十九畏配伍禁忌"""
    herb_ids = data.herb_ids

    # 查询涉及的禁忌规则
    rules = db.query(IncompatibilityRule).filter(
        (IncompatibilityRule.herb_a_id.in_(herb_ids)) & (IncompatibilityRule.herb_b_id.in_(herb_ids))
    ).all()

    # 构建药材ID→名称映射
    herbs = db.query(Herb).filter(Herb.id.in_(herb_ids)).all()
    herb_map = {h.id: h.name for h in herbs}

    warnings = []
    for rule in rules:
        if rule.herb_a_id in herb_ids and rule.herb_b_id in herb_ids:
            warnings.append(IncompatibilityWarning(
                herb_a=herb_map.get(rule.herb_a_id, f"ID:{rule.herb_a_id}"),
                herb_b=herb_map.get(rule.herb_b_id, f"ID:{rule.herb_b_id}"),
                rule_type=rule.rule_type,
                description=rule.description,
            ))

    return IncompatibilityCheckResponse(is_safe=len(warnings) == 0, warnings=warnings)


# ── 库存管理（必须在 /{herb_id} 之前定义，否则 inventory 会被当作 herb_id 匹配）──

@router.get("/inventory", response_model=list[InventoryResponse], summary="库存列表")
def list_inventory(
    search: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(HerbInventory).options(joinedload(HerbInventory.herb))
    if status:
        query = query.filter(HerbInventory.status == status)
    items = query.all()
    result = []
    for item in items:
        resp = InventoryResponse.model_validate(item)
        resp.herb_name = item.herb.name if item.herb else None
        result.append(resp)
    return result


@router.post("/inventory/in", response_model=InventoryResponse, summary="入库")
def inventory_in(data: InventoryIn, db: Session = Depends(get_db)):
    herb = db.query(Herb).filter(Herb.id == data.herb_id).first()
    if not herb:
        raise HTTPException(status_code=404, detail="药材不存在")

    # 查找或创建库存记录
    inv = HerbInventory(
        herb_id=data.herb_id,
        batch_number=data.batch_number,
        quantity=data.quantity,
        unit_price=data.unit_price,
        purchase_date=data.purchase_date,
        expiry_date=data.expiry_date,
        supplier=data.supplier,
        min_stock=0,
    )
    db.add(inv)
    db.flush()

    # 记录出入库
    txn = InventoryTransaction(
        herb_id=data.herb_id,
        transaction_type="入库",
        quantity=data.quantity,
        before_quantity=0,
        after_quantity=data.quantity,
        note=data.note,
    )
    db.add(txn)
    db.commit()
    db.refresh(inv)

    resp = InventoryResponse.model_validate(inv)
    resp.herb_name = herb.name
    return resp


@router.post("/inventory/out", summary="出库")
def inventory_out(data: InventoryOut, db: Session = Depends(get_db)):
    """出库：从库存中扣减指定数量"""
    # 获取该药材总库存
    total = db.query(HerbInventory).filter(
        HerbInventory.herb_id == data.herb_id,
        HerbInventory.status == "正常",
    ).all()
    available = sum(float(item.quantity) for item in total)

    if available < data.quantity:
        raise HTTPException(status_code=400, detail=f"库存不足: 可用{available}g，需{data.quantity}g")

    # 按批次先进先出扣减
    remaining = data.quantity
    for item in total:
        if remaining <= 0:
            break
        deduct = min(float(item.quantity), remaining)
        item.quantity = float(item.quantity) - deduct
        remaining -= deduct

    # 记录出入库
    txn = InventoryTransaction(
        herb_id=data.herb_id,
        transaction_type="出库",
        quantity=data.quantity,
        before_quantity=available,
        after_quantity=available - data.quantity,
        reference_id=data.reference_id,
        note=data.note,
    )
    db.add(txn)
    db.commit()
    return {"message": "出库成功", "quantity": data.quantity, "remaining": available - data.quantity}


@router.get("/inventory/alerts", response_model=list[InventoryAlert], summary="库存预警")
def inventory_alerts(db: Session = Depends(get_db)):
    """低于最低库存的药材预警"""
    items = db.query(HerbInventory).options(joinedload(HerbInventory.herb)).filter(
        HerbInventory.min_stock > 0,
    ).all()

    alerts = []
    for item in items:
        if float(item.quantity) < float(item.min_stock or 0):
            alerts.append(InventoryAlert(
                herb_id=item.herb_id,
                herb_name=item.herb.name if item.herb else "未知",
                current_quantity=float(item.quantity),
                min_stock=float(item.min_stock or 0),
                alert_type="低于最低库存",
            ))
    return alerts


@router.get("/inventory/summary", response_model=list[InventorySummary], summary="库存汇总")
def inventory_summary(db: Session = Depends(get_db)):
    """按药材汇总库存"""
    from sqlalchemy import func as sqlfunc
    results = db.query(
        HerbInventory.herb_id,
        sqlfunc.sum(HerbInventory.quantity).label("total_quantity"),
        sqlfunc.count(HerbInventory.id).label("batch_count"),
        sqlfunc.max(HerbInventory.min_stock).label("min_stock"),
    ).filter(
        HerbInventory.status == "正常",
    ).group_by(HerbInventory.herb_id).all()

    herb_ids = [r.herb_id for r in results]
    herbs_map = {}
    if herb_ids:
        herbs_list = db.query(Herb).filter(Herb.id.in_(herb_ids)).all()
        herbs_map = {h.id: h.name for h in herbs_list}

    return [
        InventorySummary(
            herb_id=r.herb_id,
            herb_name=herbs_map.get(r.herb_id, "未知"),
            total_quantity=float(r.total_quantity or 0),
            batch_count=r.batch_count,
            min_stock=float(r.min_stock) if r.min_stock else None,
            has_alert=float(r.min_stock or 0) > 0 and float(r.total_quantity or 0) < float(r.min_stock or 0),
        )
        for r in results
    ]


@router.put("/inventory/{inventory_id}", response_model=InventoryResponse, summary="更新库存记录")
def update_inventory(inventory_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    """更新库存记录的预警值、仓位、状态等"""
    inv = db.query(HerbInventory).filter(HerbInventory.id == inventory_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)
    db.commit()
    db.refresh(inv)
    resp = InventoryResponse.model_validate(inv)
    resp.herb_name = inv.herb.name if inv.herb else None
    return resp


# ── 药材详情/更新（路径参数路由，必须放在所有固定路径路由之后）──

@router.get("/{herb_id}", response_model=HerbResponse, summary="药材详情")
def get_herb(herb_id: int, db: Session = Depends(get_db)):
    herb = db.query(Herb).filter(Herb.id == herb_id).first()
    if not herb:
        raise HTTPException(status_code=404, detail="药材不存在")
    return herb


@router.put("/{herb_id}", response_model=HerbResponse, summary="更新药材")
def update_herb(herb_id: int, data: HerbUpdate, db: Session = Depends(get_db)):
    herb = db.query(Herb).filter(Herb.id == herb_id).first()
    if not herb:
        raise HTTPException(status_code=404, detail="药材不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(herb, key, value)
    db.commit()
    db.refresh(herb)
    return herb
