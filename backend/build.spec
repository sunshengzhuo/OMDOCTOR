# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置 — 将 FastAPI 后端打包为单个可执行文件"""

import sys
from pathlib import Path

block_cipher = None

# 收集所有隐式依赖
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'sqlite3',
    'httpx',
    'anyio',
    'sniffio',
    'app.main',
    'app.config',
    'app.database',
    'app.models',
    'app.models.patient',
    'app.models.visit',
    'app.models.herb',
    'app.models.prescription',
    'app.models.knowledge',
    'app.routers',
    'app.routers.patient',
    'app.routers.herb',
    'app.routers.prescription',
    'app.routers.knowledge',
    'app.routers.diagnosis',
    'app.routers.stats',
    'app.routers.backup',
    'app.schemas',
    'app.schemas.patient',
    'app.schemas.herb',
    'app.schemas.prescription',
    'app.schemas.diagnosis',
    'app.services',
    'app.services.incompatibility_checker',
    'app.services.constitution_evaluator',
    'app.services.ai_diagnosis_service',
    'app.services.vector_store',
]

# 数据文件
backend_dir = Path(SPECPATH)
datas = [
    (str(backend_dir / 'app' / 'data'), 'app/data'),
]

# ChromaDB 是可选的，如果安装了就打包
try:
    import chromadb
    hiddenimports.append('chromadb')
    hiddenimports.append('sentence_transformers')
except ImportError:
    pass

a = Analysis(
    [str(backend_dir / 'run.py')],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy.testing', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tcm-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
