"""应用配置管理"""
import sys
import os
from pydantic_settings import BaseSettings


def _get_env_file() -> str:
    """PyInstaller 打包后 .env 在 exe 同目录，开发时在项目根目录"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), '.env')
    return ".env"


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "中医诊所管理平台"
    app_version: str = "0.1.0"

    # 数据库
    database_url: str = "sqlite:///./tcm_doctor.db"

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # Vision API（图片识别，支持 OpenAI 兼容格式的 Vision 端点）
    deepseek_vision_model: str = ""  # 留空则不支持图片，如 Pro/moonshotai/Kimi-K2.6
    deepseek_vision_base_url: str = ""  # 留空则与 deepseek_base_url 相同
    deepseek_vision_api_key: str = ""  # 留空则复用 deepseek_api_key

    # 向量数据库
    chroma_persist_dir: str = "./chroma_data"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # 服务配置
    host: str = "127.0.0.1"
    port: int = 8765

    model_config = {
        "env_file": _get_env_file(),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
