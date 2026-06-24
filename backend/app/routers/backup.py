"""数据备份与恢复路由"""
import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.config import settings

router = APIRouter(prefix="/backup", tags=["数据管理"])


@router.get("/export", summary="导出数据备份")
def export_backup():
    """导出 SQLite 数据库文件"""
    db_path = settings.database_url.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        # 尝试相对路径
        db_path = os.path.join(os.getcwd(), "tcm_doctor.db")

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库文件不存在")

    # 复制到临时文件（避免锁定）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_path = os.path.join(os.getcwd(), f"tcm_backup_{timestamp}.db")
    shutil.copy2(db_path, temp_path)

    return FileResponse(
        path=temp_path,
        filename=f"tcm_backup_{datetime.now().strftime('%Y-%m-%d')}.db",
        media_type="application/octet-stream",
        background=None,  # 可选：后台清理临时文件
    )


@router.post("/import", summary="导入数据恢复")
async def import_backup(file: UploadFile = File(...)):
    """导入 SQLite 数据库文件恢复数据"""
    if not file.filename.endswith(('.db', '.sqlite', '.sqlite3')):
        raise HTTPException(status_code=400, detail="请上传 .db 格式的备份文件")

    # 保存上传文件
    upload_dir = os.path.join(os.getcwd(), "backups")
    os.makedirs(upload_dir, exist_ok=True)
    upload_path = os.path.join(upload_dir, f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 替换当前数据库
    db_path = settings.database_url.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        db_path = os.path.join(os.getcwd(), "tcm_doctor.db")

    # 备份当前数据库
    if os.path.exists(db_path):
        backup_path = db_path + f".bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(db_path, backup_path)

    # 用上传文件替换
    shutil.copy2(upload_path, db_path)

    # 清理
    os.remove(upload_path)

    return {"message": "数据恢复成功，请重启应用以加载新数据"}


@router.post("/reset", summary="清空数据")
def reset_data(db: Session = Depends(get_db)):
    """清空所有数据（保留表结构）"""
    from app.models.herb import Herb, IncompatibilityRule, HerbInventory, InventoryTransaction
    from app.models.prescription import ClassicFormula, Prescription, PrescriptionItem
    from app.models.patient import Patient
    from app.models.visit import Visit
    from app.models.knowledge import KnowledgeEntry

    # 按依赖顺序删除
    for model in [PrescriptionItem, Prescription, InventoryTransaction, HerbInventory,
                  IncompatibilityRule, Visit, Patient, ClassicFormula, KnowledgeEntry, Herb]:
        db.query(model).delete()

    db.commit()

    # 重新导入种子数据
    from app.seed import seed_all
    seed_all()

    return {"message": "数据已清空并重新初始化"}
