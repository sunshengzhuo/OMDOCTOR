"""FastAPI 主入口"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import patient, herb, prescription, knowledge, diagnosis
from app.routers import stats, backup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时创建表 + 导入初始数据"""
    # 导入所有模型确保 Base.metadata 包含所有表
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # 首次启动时导入药材、配伍禁忌、经典方剂数据
    from app.seed import seed_all
    seed_all()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="中医诊所问诊管理平台 API — 集成 DeepSeek 智能辨证",
    lifespan=lifespan,
)

# CORS — 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:8765", "http://127.0.0.1:8765", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(patient.router, prefix="/api/v1")
app.include_router(herb.router, prefix="/api/v1")
app.include_router(prescription.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(diagnosis.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(backup.router, prefix="/api/v1")


@app.get("/health", tags=["系统"])
def health_check():
    """健康检查 — Electron 启动时轮询此接口"""
    return {"status": "ok", "version": settings.app_version}


@app.get("/api/v1/config", tags=["系统"])
def get_config():
    """获取系统配置"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "deepseek_configured": bool(settings.deepseek_api_key),
        "deepseek_model": settings.deepseek_model,
        "deepseek_base_url": settings.deepseek_base_url,
        "vision_configured": bool(settings.deepseek_vision_model),
        "deepseek_vision_model": settings.deepseek_vision_model,
        "deepseek_vision_base_url": settings.deepseek_vision_base_url,
        "vision_key_configured": bool(settings.deepseek_vision_api_key),
    }


@app.put("/api/v1/config", tags=["系统"])
def update_config(
    deepseek_api_key: str | None = None,
    deepseek_model: str | None = None,
    deepseek_base_url: str | None = None,
    deepseek_vision_model: str | None = None,
    deepseek_vision_base_url: str | None = None,
    deepseek_vision_api_key: str | None = None,
):
    """更新系统配置 — 同时写入 .env 文件持久化"""
    # .env 路径与 pydantic_settings 一致（项目根目录）
    env_path = Path(__file__).parent.parent / ".env"
    env_lines: dict[str, str] = {}

    # 读取已有 .env
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env_lines[k.strip()] = v.strip()

    # 更新内存 + env（忽略空字符串，防止误清已有配置）
    if deepseek_api_key:
        settings.deepseek_api_key = deepseek_api_key
        env_lines["DEEPSEEK_API_KEY"] = deepseek_api_key
    if deepseek_model:
        settings.deepseek_model = deepseek_model
        env_lines["DEEPSEEK_MODEL"] = deepseek_model
    if deepseek_base_url:
        settings.deepseek_base_url = deepseek_base_url
        env_lines["DEEPSEEK_BASE_URL"] = deepseek_base_url
    if deepseek_vision_model:
        settings.deepseek_vision_model = deepseek_vision_model
        env_lines["DEEPSEEK_VISION_MODEL"] = deepseek_vision_model
    if deepseek_vision_base_url:
        settings.deepseek_vision_base_url = deepseek_vision_base_url
        env_lines["DEEPSEEK_VISION_BASE_URL"] = deepseek_vision_base_url
    if deepseek_vision_api_key:
        settings.deepseek_vision_api_key = deepseek_vision_api_key
        env_lines["DEEPSEEK_VISION_API_KEY"] = deepseek_vision_api_key

    # 写回 .env（原子写入：先写临时文件再替换，避免 reload 期间读到空文件）
    tmp_path = env_path.with_suffix(".env.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for k, v in env_lines.items():
            f.write(f"{k}={v}\n")
    tmp_path.replace(env_path)

    return {"message": "配置已保存", "deepseek_configured": bool(settings.deepseek_api_key)}
