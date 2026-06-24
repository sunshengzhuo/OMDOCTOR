"""统计报表路由"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.prescription import Prescription, PrescriptionItem
from app.models.herb import Herb, HerbInventory

router = APIRouter(prefix="/stats", tags=["统计报表"])


@router.get("/dashboard", summary="工作台概览数据")
def dashboard_stats(db: Session = Depends(get_db)):
    """工作台首页统计数据"""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # 今日就诊数
    today_visits = db.query(Visit).filter(
        Visit.visit_date.between(today_start, today_end)
    ).count()

    # 患者总数
    total_patients = db.query(Patient).count()

    # 药品总数
    total_herbs = db.query(Herb).filter(Herb.is_active == True).count()

    # 今日处方数
    today_prescriptions = db.query(Prescription).filter(
        Prescription.created_at.between(today_start, today_end)
    ).count()

    # 待审核处方数
    pending_prescriptions = db.query(Prescription).filter(
        Prescription.status == "已开"
    ).count()

    # 库存预警数
    low_stock_count = 0
    inventory_items = db.query(HerbInventory).filter(HerbInventory.min_stock > 0).all()
    for item in inventory_items:
        if float(item.quantity) < float(item.min_stock or 0):
            low_stock_count += 1

    # 最近7天就诊趋势
    seven_days_ago = today_start - timedelta(days=7)
    visit_trend = []
    for i in range(7):
        day_start = seven_days_ago + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.query(Visit).filter(Visit.visit_date.between(day_start, day_end)).count()
        visit_trend.append({
            "date": day_start.strftime("%m-%d"),
            "count": count,
        })

    return {
        "today_visits": today_visits,
        "total_patients": total_patients,
        "total_herbs": total_herbs,
        "today_prescriptions": today_prescriptions,
        "pending_prescriptions": pending_prescriptions,
        "low_stock_count": low_stock_count,
        "visit_trend": visit_trend,
    }


@router.get("/visits", summary="就诊统计")
def visit_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """就诊趋势统计"""
    start_date = datetime.now() - timedelta(days=days)

    # 每日就诊数
    daily_stats = []
    for i in range(min(days, 60)):  # 最多返回60天
        day = (datetime.now() - timedelta(days=days - i)).date()
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        count = db.query(Visit).filter(Visit.visit_date.between(day_start, day_end)).count()
        daily_stats.append({"date": day.strftime("%Y-%m-%d"), "count": count})

    # 常见证型统计
    syndrome_stats = db.query(
        Visit.tcm_syndrome,
        func.count(Visit.id),
    ).filter(
        Visit.visit_date >= start_date,
        Visit.tcm_syndrome.isnot(None),
    ).group_by(Visit.tcm_syndrome).order_by(func.count(Visit.id).desc()).limit(10).all()

    return {
        "daily_stats": daily_stats,
        "syndrome_stats": [{"name": s, "count": c} for s, c in syndrome_stats if s],
        "total_visits": sum(d["count"] for d in daily_stats),
    }


@router.get("/herbs", summary="用药统计")
def herb_stats(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """用药频次统计"""
    start_date = datetime.now() - timedelta(days=days)

    # 最常用药物 (从处方明细中统计)
    herb_usage = db.query(
        PrescriptionItem.herb_name,
        func.count(PrescriptionItem.id).label("usage_count"),
        func.sum(PrescriptionItem.dose).label("total_dose"),
    ).join(
        Prescription, PrescriptionItem.prescription_id == Prescription.id
    ).filter(
        Prescription.created_at >= start_date,
    ).group_by(
        PrescriptionItem.herb_name,
    ).order_by(
        func.count(PrescriptionItem.id).desc(),
    ).limit(limit).all()

    return {
        "herb_usage": [
            {
                "name": h,
                "usage_count": int(c),
                "total_dose": float(t) if t else 0,
            }
            for h, c, t in herb_usage
        ],
        "period_days": days,
    }


@router.get("/prescriptions", summary="处方统计")
def prescription_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """处方统计"""
    start_date = datetime.now() - timedelta(days=days)

    total = db.query(Prescription).filter(Prescription.created_at >= start_date).count()

    # 按状态统计
    status_stats = db.query(
        Prescription.status,
        func.count(Prescription.id),
    ).filter(
        Prescription.created_at >= start_date,
    ).group_by(Prescription.status).all()

    # 常用方剂统计
    formula_stats = db.query(
        Prescription.formula_name,
        func.count(Prescription.id),
    ).filter(
        Prescription.created_at >= start_date,
        Prescription.formula_name.isnot(None),
    ).group_by(Prescription.formula_name).order_by(
        func.count(Prescription.id).desc()
    ).limit(10).all()

    return {
        "total": total,
        "status_stats": [{"status": s, "count": c} for s, c in status_stats],
        "formula_stats": [{"name": n or "自拟方", "count": c} for n, c in formula_stats],
        "period_days": days,
    }
