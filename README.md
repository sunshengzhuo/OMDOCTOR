# 中医诊所管理平台 (OMDOCTOR)

集诊所管理 + AI 智能辨证 + 中西医结合于一体的桌面平台。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Electron 主进程                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ BrowserWindow │  │ PythonRunner │  │  Preload 桥接  │  │
│  │  (Chromium)   │  │ (子进程管理)  │  │ (IPC 通信)    │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────┘  │
└─────────┼─────────────────┼─────────────────────────────┘
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌──────────────────────────────────┐
│   Vue3 前端 SPA   │  │        FastAPI 后端 (8765)        │
│ ┌──────────────┐ │  │ ┌──────────────────────────────┐ │
│ │ Element Plus │ │  │ │          Routers              │ │
│ │ ECharts      │ │  │ │  /patients  /herbs  /rx     │ │
│ │ Pinia        │ │  │ │  /diagnosis  /knowledge      │ │
│ │ Vue Router   │ │  │ │  /stats  /backup  /config    │ │
│ └──────────────┘ │  │ └──────────────────────────────┘ │
│ ┌──────────────┐ │  │ ┌──────────────────────────────┐ │
│ │   api.ts     │ │  │ │         Services              │ │
│ │ (axios 请求) │ │──│ │  AI辨证  配伍检查  体质评估   │ │
│ └──────────────┘ │  │ │  向量检索  库存管理           │ │
└──────────────────┘  │ └──────────────────────────────┘ │
                      │ ┌──────────────────────────────┐ │
                      │ │      Data Layer               │ │
                      │ │  SQLite + SQLAlchemy 2.0      │ │
                      │ │  ChromaDB (可选)              │ │
                      │ └──────────────────────────────┘ │
                      └──────────┬───────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ DeepSeek │ │ 硅基流动  │ │ 知识库JSON│
              │  API     │ │  Vision  │ │  (29部)  │
              │(文字对话) │ │(图片识别)│ │          │
              └──────────┘ └──────────┘ └──────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面壳 | Electron 28 |
| 前端 | Vue 3 + Element Plus + TypeScript + Pinia + ECharts |
| 后端 | Python FastAPI + SQLAlchemy 2.0 + SQLite |
| AI 文字 | DeepSeek API (deepseek-chat / deepseek-reasoner) |
| AI 图片 | 硅基流动 Vision API (Kimi-K2.6) |
| 知识检索 | RAG 多路召回 (关键词 + ChromaDB 语义向量) |
| 打包 | electron-builder (NSIS) + PyInstaller |

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- npm

### 安装与启动

```bash
# 1. 克隆项目
git clone https://github.com/sunshengzhuo/OMDOCTOR.git
cd OMDOCTOR

# 2. 安装后端依赖
cd backend
pip install fastapi uvicorn sqlalchemy pydantic-settings httpx python-multipart

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 启动后端（端口 8765）
cd ../backend
python -m uvicorn app.main:app --reload --port 8765

# 5. 启动前端（端口 5173，自动代理 /api → 后端）
cd ../frontend
npm run dev
```

浏览器访问 `http://localhost:5173`，进入系统设置配置 DeepSeek API Key 即可使用。

### API Key 配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| API Key | DeepSeek 对话模型密钥 | `sk-xxx` |
| 对话模型 | 纯文字对话使用的模型 | `deepseek-chat` |
| Base URL | DeepSeek API 地址 | `https://api.deepseek.com` |
| Vision 模型 | 图片识别模型（第三方） | `Pro/moonshotai/Kimi-K2.6` |
| Vision URL | Vision API 地址 | `https://api.siliconflow.cn/v1` |
| Vision Key | Vision API 密钥（留空则复用对话 Key） | `sk-yyy` |

> 图片识别为可选功能。未配置 Vision 时，上传图片不会报错，AI 将基于文字描述进行分析。

### 桌面端打包

```bash
# 1. 编译 Electron 主进程
cd electron && npx tsc && cd ..

# 2. 构建前端
cd frontend && npm run build && cd ..

# 3. 打包后端为 exe（需先 pip install pyinstaller）
cd backend && python -m PyInstaller build.spec && cd ..

# 4. 生成安装包（需配置国内镜像）
ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/" \
ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/" \
npx electron-builder --win --x64
```

产出：`dist-electron/tcm-doctor-setup-0.1.0.exe`

## 功能模块

### 患者管理
- 患者信息 CRUD + 分页搜索
- 就诊记录（四诊信息录入 + 辨证论治 + AI 辅助辨证）
- 体质辨识（王琦九种体质量表 + 转化分 + 雷达图）

### 药品管理
- 药材字典（229 味，覆盖 18 个分类，支持异名搜索）
- 库存管理（入库/出库/预警/仓位/批次）
- 配伍禁忌引擎（十八反/十九畏 + 孕妇禁忌 + 毒性药检测）

### 处方管理
- 处方编辑器（经典方导入 → 加减药味 → 煎服法 → 实时安全检查）
- 处方审核 + 发药 + 库存扣减
- 经典方剂库（按出处/功效检索 + 加减变化展示）

### AI 智能问诊
- 对话式问诊（DeepSeek + RAG 知识库增强）
- 四诊辨证分析（结构化四诊输入 + AI 综合辨证）
- 图片识别（舌苔照片/面色/化验单/影像报告 → AI 读取分析）
- 中西医结合（西医病名/化验指标 → 中医辨证 + 中西医结合治疗方案）
- 安全硬约束（配伍禁忌 + 孕妇禁忌 + 毒性药自动检测）

### 知识库
- 医籍文库（29 部中医经典，1313 条知识条目）
- 知识检索（关键词 + 语义向量双路检索）
- 经典方剂数据（伤寒论/金匮要略/温病条辨等出处方剂）

### 数据统计
- 工作台仪表盘（统计卡片 + 7 日就诊趋势 + 库存预警 + 待办）
- 统计报表（就诊趋势/用药分析/处方统计 ECharts 图表）

### 系统管理
- 系统设置（API 配置 + 连接测试 + 持久化到 .env）
- 数据备份/恢复（SQLite 导出/导入/重置）

## 数据概况

| 数据类型 | 数量 |
|----------|------|
| 药材 | 229 味（18 个分类） |
| 配伍禁忌规则 | 35 条（十八反 + 十九畏） |
| 知识库条目 | 1313 条 |
| 知识库来源 | 29 部中医经典 |

### 知识库收录典籍

| 类别 | 典籍 |
|------|------|
| 经典 | 伤寒论、金匮要略、黄帝内经·素问、黄帝内经·灵枢、温病条辨 |
| 专科 | 傅青主女科、妇人大全良方、脾胃论、丹溪心法 |
| 针灸 | 中医针灸学、针灸甲乙经 |
| 医案 | 临证指南医案、黄煌经方医案、岳美中医案集、蒲辅周医案、经方实验录 |
| 综合 | 医学衷中参西录 |

## 项目结构

```
OMDOCTOR/
├── electron/                # Electron 主进程
│   ├── main.ts             # 窗口管理 + 后端启动
│   ├── preload.ts          # 安全桥接
│   ├── python-runner.ts    # Python 子进程管理
│   └── tsconfig.json
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── layouts/        # 主布局（侧边栏导航）
│   │   ├── views/          # 页面组件
│   │   │   ├── dashboard/  # 工作台 + 统计报表
│   │   │   ├── patient/    # 患者管理 + 就诊记录 + 体质辨识
│   │   │   ├── herb/       # 药材字典 + 库存管理
│   │   │   ├── prescription/ # 处方编辑 + 经典方库
│   │   │   ├── knowledge/  # 知识检索 + 医籍文库
│   │   │   ├── diagnosis/  # 智能问诊（AI + 图片识别）
│   │   │   └── settings/   # 系统设置
│   │   ├── components/     # 公共组件（药材选择器/配伍警报）
│   │   ├── utils/          # api.ts（axios 封装）
│   │   └── styles/         # 中医暖色主题
│   └── vite.config.ts
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 入口 + CORS + 配置API
│   │   ├── config.py       # pydantic_settings 配置管理
│   │   ├── database.py     # SQLAlchemy 引擎 + 会话
│   │   ├── models/         # ORM 模型（患者/就诊/药材/方剂/知识库）
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── routers/        # API 路由（7 个模块）
│   │   ├── services/       # 业务逻辑
│   │   │   ├── ai_diagnosis_service.py  # AI 辨证（DeepSeek + Vision + RAG）
│   │   │   ├── incompatibility_checker.py # 配伍禁忌检查
│   │   │   ├── constitution_evaluator.py  # 体质辨识评估
│   │   │   └── vector_store.py            # ChromaDB 向量检索
│   │   └── data/           # 种子数据 + 29 部典籍 JSON
│   ├── run.py              # PyInstaller 入口
│   ├── build.spec          # PyInstaller 配置
│   ├── tcm_doctor.db       # SQLite 数据库（含完整数据）
│   └── pyproject.toml
├── resources/               # 应用图标
├── electron-builder.yml     # electron-builder 打包配置
└── package.json             # Electron 根配置
```

## API 端点

| 模块 | 路径 | 说明 |
|------|------|------|
| 系统 | `GET /health` | 健康检查 |
| 系统 | `GET/PUT /api/v1/config` | 系统配置（API Key 持久化） |
| 患者 | `/api/v1/patients` | 患者 CRUD |
| 患者 | `/api/v1/patients/{id}/visits` | 就诊记录 |
| 患者 | `/api/v1/patients/{id}/constitution` | 体质辨识 |
| 药品 | `/api/v1/herbs` | 药材字典 + 详情 |
| 药品 | `/api/v1/herbs/inventory/*` | 库存管理（入库/出库/预警/汇总） |
| 药品 | `/api/v1/herbs/incompatibility-check` | 配伍禁忌检查 |
| 处方 | `/api/v1/prescriptions` | 处方 CRUD + 审核 + 发药 |
| 处方 | `/api/v1/prescriptions/classic-formulas` | 经典方剂库 |
| 问诊 | `POST /api/v1/diagnosis/chat` | 对话式智能问诊 |
| 问诊 | `POST /api/v1/diagnosis/analyze` | 四诊辨证分析 |
| 问诊 | `POST /api/v1/diagnosis/upload-image` | 上传诊断图片 |
| 问诊 | `GET /api/v1/diagnosis/status` | AI 服务状态 |
| 知识 | `/api/v1/knowledge/search` | 知识检索 |
| 知识 | `/api/v1/knowledge/entries` | 知识条目管理 |
| 知识 | `/api/v1/knowledge/sources` | 知识来源列表 |
| 统计 | `/api/v1/stats/dashboard` | 工作台数据 |
| 统计 | `/api/v1/stats/visits` | 就诊统计 |
| 备份 | `/api/v1/backup/export` | 导出备份 |
| 备份 | `/api/v1/backup/import` | 导入恢复 |
