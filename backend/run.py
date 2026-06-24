"""PyInstaller 入口 — 启动 FastAPI 服务"""
import sys
import os


def main():
    # 设置工作目录为 exe 所在目录
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))

    import uvicorn
    from app.main import app
    from app.config import settings

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
