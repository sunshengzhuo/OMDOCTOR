"""配伍禁忌检查引擎 — 十八反/十九畏核心逻辑"""
from sqlalchemy.orm import Session
from app.models.herb import Herb, IncompatibilityRule


def check_prescription_herbs(herb_ids: list[int], db: Session) -> list[dict]:
    """
    检查一组药材ID是否存在配伍禁忌。

    返回: [{"herb_a": "甘草", "herb_b": "甘遂", "rule_type": "十八反", "description": "..."}]
    """
    if len(herb_ids) < 2:
        return []

    conflicts = db.query(IncompatibilityRule).filter(
        (IncompatibilityRule.herb_a_id.in_(herb_ids))
        & (IncompatibilityRule.herb_b_id.in_(herb_ids))
    ).all()

    herbs = db.query(Herb).filter(Herb.id.in_(herb_ids)).all()
    herb_map = {h.id: h.name for h in herbs}

    results = []
    for rule in conflicts:
        # 确保两个药材都在当前处方中
        if rule.herb_a_id in herb_ids and rule.herb_b_id in herb_ids:
            results.append({
                "herb_a": herb_map.get(rule.herb_a_id, f"ID:{rule.herb_a_id}"),
                "herb_b": herb_map.get(rule.herb_b_id, f"ID:{rule.herb_b_id}"),
                "rule_type": rule.rule_type,
                "description": rule.description,
            })
    return results


def check_dosage_limits(herb_id: int, dose: float, db: Session) -> dict | None:
    """
    检查药材剂量是否超限。

    返回: None 表示安全，或 {"herb_name": "...", "max_dose": ..., "actual_dose": ...}
    """
    herb = db.query(Herb).filter(Herb.id == herb_id).first()
    if not herb:
        return None

    if herb.dosage_max and dose > float(herb.dosage_max):
        return {
            "herb_name": herb.name,
            "max_dose": float(herb.dosage_max),
            "actual_dose": dose,
            "toxicity": herb.toxicity,
        }
    return None


def check_pregnancy_contraindications(herb_ids: list[int], db: Session) -> list[str]:
    """检查孕妇禁忌药材"""
    herbs = db.query(Herb).filter(
        Herb.id.in_(herb_ids),
        Herb.pregnancy_contraindicated == True,
    ).all()
    return [f"⚠️ {h.name} 孕妇禁用 (毒性: {h.toxicity})" for h in herbs]
