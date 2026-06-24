"""知识库路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.knowledge import KnowledgeEntry

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/search", summary="知识检索")
def search_knowledge(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    category: str | None = Query(None, description="分类筛选"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """知识库搜索 — 关键词 + 语义检索(如 ChromaDB 可用)"""
    results = []

    # 1. 关键词检索
    query = db.query(KnowledgeEntry)
    if category:
        query = query.filter(KnowledgeEntry.category == category)
    query = query.filter(
        (KnowledgeEntry.title.contains(q)) | (KnowledgeEntry.content.contains(q))
    )
    sql_results = query.limit(limit).all()
    seen_ids = set()
    for e in sql_results:
        seen_ids.add(e.id)
        results.append({
            "id": e.id,
            "title": e.title,
            "category": e.category,
            "source": e.source,
            "content": e.content[:500],
            "match_type": "关键词",
        })

    # 2. 语义检索 (ChromaDB，如果可用)
    try:
        from app.services.vector_store import vector_store
        vector_results = vector_store.search(q, top_k=limit, category=category)
        for r in vector_results:
            # 避免重复
            if r.get("id", "").startswith("entry_"):
                try:
                    entry_id = int(r["id"].replace("entry_", ""))
                    if entry_id in seen_ids:
                        continue
                except ValueError:
                    pass
            results.append({
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "category": r.get("category", ""),
                "source": r.get("source", ""),
                "content": r.get("content", "")[:500],
                "match_type": "语义",
                "score": r.get("score"),
            })
    except ImportError:
        pass
    except Exception:
        pass

    return results[:limit]


@router.post("/entries", summary="新增知识条目")
def create_entry(
    title: str,
    category: str,
    content: str,
    source: str | None = None,
    structured_data: dict | None = None,
    tags: list[str] | None = None,
    db: Session = Depends(get_db),
):
    entry = KnowledgeEntry(
        title=title,
        category=category,
        content=content,
        source=source,
        structured_data=structured_data,
        tags=tags,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # 同步到向量库
    try:
        from app.services.vector_store import vector_store
        vector_store.add_documents([{
            "id": f"entry_{entry.id}",
            "title": entry.title,
            "content": entry.content,
            "category": entry.category,
            "metadata": {"source": entry.source or ""},
        }])
    except Exception:
        pass

    return {"id": entry.id, "title": entry.title}


@router.get("/entries/{entry_id}", summary="知识条目详情")
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="条目不存在")
    return entry


@router.get("/entries", summary="知识条目列表")
def list_entries(
    category: str | None = Query(None, description="分类筛选"),
    source: str | None = Query(None, description="出处筛选"),
    search: str | None = Query(None, description="标题/内容关键词"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    # Build base filter
    base_filter = []
    if category:
        base_filter.append(KnowledgeEntry.category == category)
    if source:
        base_filter.append(KnowledgeEntry.source == source)
    if search:
        base_filter.append(
            (KnowledgeEntry.title.contains(search)) | (KnowledgeEntry.content.contains(search))
        )

    # Count with filter (uses index)
    count_q = db.query(func.count(KnowledgeEntry.id))
    for f in base_filter:
        count_q = count_q.filter(f)
    total = count_q.scalar()

    # Fetch only needed columns — use SQL SUBSTR to avoid loading full content
    content_preview = func.substr(KnowledgeEntry.content, 1, 200).label('content_preview')
    data_q = db.query(
        KnowledgeEntry.id,
        KnowledgeEntry.title,
        KnowledgeEntry.category,
        KnowledgeEntry.source,
        content_preview,
    )
    for f in base_filter:
        data_q = data_q.filter(f)
    items = data_q.order_by(KnowledgeEntry.source, KnowledgeEntry.id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": e.id,
                "title": e.title,
                "category": e.category,
                "source": e.source,
                "content_preview": e.content_preview or "",
            }
            for e in items
        ],
    }


@router.get("/sources", summary="知识库出处列表")
def list_sources(db: Session = Depends(get_db)):
    """返回所有出处及其条目数，供前端下拉筛选"""
    results = db.query(
        KnowledgeEntry.source,
        func.count(KnowledgeEntry.id),
    ).group_by(KnowledgeEntry.source).order_by(func.count(KnowledgeEntry.id).desc()).all()
    return [{"name": r[0], "count": r[1]} for r in results if r[0]]


@router.post("/rebuild-index", summary="重建向量索引")
def rebuild_index(db: Session = Depends(get_db)):
    """重建 ChromaDB 向量索引"""
    try:
        from app.services.vector_store import vector_store
        count = vector_store.rebuild_from_knowledge_db(db)
        return {"message": f"向量索引重建完成，已索引 {count} 条知识", "count": count}
    except ImportError:
        return {"message": "ChromaDB 未安装，请执行 pip install chromadb", "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引重建失败: {str(e)}")


@router.get("/stats", summary="知识库统计")
def knowledge_stats(db: Session = Depends(get_db)):
    """知识库统计信息"""
    total = db.query(KnowledgeEntry).count()
    categories = db.query(
        KnowledgeEntry.category,
        func.count(KnowledgeEntry.id),
    ).group_by(KnowledgeEntry.category).all()

    try:
        from app.services.vector_store import vector_store
        vs_stats = vector_store.get_stats()
    except Exception:
        vs_stats = {"available": False, "count": 0}

    return {
        "total_entries": total,
        "categories": [{"name": c, "count": n} for c, n in categories if c],
        "vector_store": vs_stats,
    }
