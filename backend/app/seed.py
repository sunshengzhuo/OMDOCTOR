"""初始化数据 — 首次启动时导入药材、配伍禁忌、经典方剂、知识条目"""
import json
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.herb import Herb, IncompatibilityRule
from app.models.prescription import ClassicFormula
from app.models.knowledge import KnowledgeEntry

DATA_DIR = Path(__file__).parent / "data"


def seed_herbs(db: Session) -> int:
    """导入中药材字典"""
    count = db.query(Herb).count()
    if count > 0:
        return count  # 已有数据，跳过

    # 优先使用扩展版数据
    data_file = DATA_DIR / "herbs_extended.json"
    if not data_file.exists():
        data_file = DATA_DIR / "herbs.json"

    if not data_file.exists():
        return 0

    with open(data_file, "r", encoding="utf-8") as f:
        herbs = json.load(f)

    for h in herbs:
        herb = Herb(
            name=h["name"],
            aliases=h.get("aliases"),
            category=h.get("category"),
            nature=h.get("nature"),
            flavor=h.get("flavor"),
            meridian_tropism=h.get("meridian_tropism"),
            efficacy=h.get("efficacy"),
            dosage_min=h.get("dosage_min"),
            dosage_max=h.get("dosage_max"),
            toxicity=h.get("toxicity", "无毒"),
            pregnancy_contraindicated=h.get("pregnancy_contraindicated", False),
            storage_condition=h.get("storage_condition"),
        )
        db.add(herb)

    db.commit()
    return len(herbs)


def seed_incompatibility_rules(db: Session) -> int:
    """导入配伍禁忌规则(十八反/十九畏)"""
    count = db.query(IncompatibilityRule).count()
    if count > 0:
        return count

    data_file = DATA_DIR / "incompatibility_rules.json"
    if not data_file.exists():
        return 0

    with open(data_file, "r", encoding="utf-8") as f:
        rules = json.load(f)

    for r in rules:
        # 通过药名查找 ID
        herb_a = db.query(Herb).filter(Herb.name == r["herb_a"]).first()
        herb_b = db.query(Herb).filter(Herb.name == r["herb_b"]).first()

        if herb_a and herb_b:
            rule = IncompatibilityRule(
                rule_type=r["rule_type"],
                herb_a_id=herb_a.id,
                herb_b_id=herb_b.id,
                description=r.get("description"),
                source=r.get("source"),
            )
            db.add(rule)

    db.commit()
    return len(rules)


def seed_classic_formulas(db: Session) -> int:
    """导入经典方剂（增量：按方名去重，只添加新方剂）"""
    data_file = DATA_DIR / "classic_formulas.json"
    if not data_file.exists():
        return db.query(ClassicFormula).count()

    with open(data_file, "r", encoding="utf-8") as f:
        formulas = json.load(f)

    # 获取已有方名集合
    existing_names = {n for (n,) in db.query(ClassicFormula.name).all()}

    added = 0
    for f_data in formulas:
        if f_data["name"] in existing_names:
            continue
        formula = ClassicFormula(
            name=f_data["name"],
            aliases=f_data.get("aliases"),
            source=f_data.get("source"),
            composition=f_data["composition"],
            efficacy=f_data.get("efficacy"),
            indications=f_data.get("indications"),
            usage=f_data.get("usage"),
            modifications=f_data.get("modifications"),
        )
        db.add(formula)
        existing_names.add(f_data["name"])
        added += 1

    if added:
        db.commit()

    total = db.query(ClassicFormula).count()
    if added:
        print(f"[Seed] 经典方剂新增 {added} 首，共 {total} 首")
    return total


def seed_knowledge(db: Session) -> int:
    """导入知识条目（增量：按标题去重，只添加新条目）
    从 knowledge_entries.json + books/ 目录下所有 JSON 批量加载
    """
    existing_titles = {t for (t,) in db.query(KnowledgeEntry.title).all()}
    added = 0

    # 1. 从主知识库文件加载
    data_file = DATA_DIR / "knowledge_entries.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for e in entries:
            if e["title"] in existing_titles:
                continue
            entry = KnowledgeEntry(
                title=e["title"],
                category=e.get("category"),
                content=e.get("content"),
                source=e.get("source"),
            )
            db.add(entry)
            existing_titles.add(e["title"])
            added += 1

    # 2. 从 books/ 目录批量加载完整医籍
    books_dir = DATA_DIR / "books"
    if books_dir.exists():
        for json_file in sorted(books_dir.glob("*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                book_entries = json.load(f)
            book_added = 0
            for e in book_entries:
                if e["title"] in existing_titles:
                    continue
                entry = KnowledgeEntry(
                    title=e["title"],
                    category=e.get("category", "条文"),
                    content=e.get("content"),
                    source=e.get("source"),
                )
                db.add(entry)
                existing_titles.add(e["title"])
                added += 1
                book_added += 1
            if book_added:
                print(f"[Seed] {json_file.name} 新增 {book_added} 条")

    if added:
        db.commit()

    total = db.query(KnowledgeEntry).count()
    if added:
        print(f"[Seed] 知识条目共新增 {added} 条，总计 {total} 条")
    return total


def seed_all():
    """执行所有数据初始化"""
    db = SessionLocal()
    try:
        h = seed_herbs(db)
        i = seed_incompatibility_rules(db)
        f = seed_classic_formulas(db)
        k = seed_knowledge(db)
        print(f"[Seed] 导入完成: 药材={h}, 配伍禁忌={i}, 经典方={f}, 知识条目={k}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
