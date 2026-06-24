# 中医诊所问诊管理平台 (TCM Doctor)

集诊所管理 + DeepSeek 智能辨证于一体的桌面平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面壳 | Electron 28 |
| 前端 | Vue 3 + Element Plus + TypeScript + Pinia + ECharts |
| 后端 | Python FastAPI + SQLAlchemy 2.0 + SQLite |
| AI | DeepSeek API + RAG (ChromaDB + bge-large-zh-v1.5) |
| 打包 | electron-builder + PyInstaller |

## 开发启动

```bash
# 安装依赖
npm install
cd frontend && npm install && cd ..

# 启动后端（端口 8765）
cd backend && python -m uvicorn app.main:app --reload --port 8765

# 启动前端（端口 5173，自动代理 /api → 后端）
cd frontend && npm run dev

# 启动 Electron（开发模式）
cd electron && npx tsc && cd .. && npx electron . --dev
```

## 已实现功能

### Phase 1 ✅ 项目骨架 + 患者管理
- Electron + FastAPI + Vue3 全链路架构
- 患者管理（CRUD + 分页搜索）
- 就诊记录（四诊信息录入 + 辨证论治）
- 体质辨识（王琦九种体质量表 + 转化分 + 雷达图）
- 药材字典（25味预置 + 异名搜索 + 分类筛选）
- 配伍禁忌引擎（十八反/十九畏 + 孕妇禁忌）
- 处方管理后端（CRUD + 配伍校验 + 审方 + 发药扣库存）
- 经典方库（4首预置）
- 中医暖色主题 + 适老化设计

### Phase 2 ✅ 药品管理完善
- 库存管理前端页面（入库/出库/预警/仓位）
- 药材选择器组件（异名模糊搜索 + 实时配伍检查）
- 配伍禁忌弹窗组件
- 扩展药材数据至 **229味**（覆盖18个分类）
- 扩展配伍禁忌至 **35条**（十八反 + 十九畏）

### Phase 3 ✅ 处方管理完善
- 处方列表（状态筛选 + 审核 + 发药 + 打印）
- 处方编辑器（核心交互：经典方导入→加减药味→煎服法→实时安全检查）
- 经典方库浏览（按出处/功效检索 + 加减变化展示 + 引入编辑器）
- 处方打印组件（Web打印 + 中医处方笺格式）

### Phase 4 ✅ 知识库 + AI 智能问诊
- ChromaDB 向量库集成（可选依赖，未安装时降级关键词检索）
- 21条知识条目（伤寒论条文 + 中医理论 + 辨证方法 + 医案）
- DeepSeek API 完整集成（对话式问诊 + 四诊辨证分析）
- RAG 多路召回（关键词 + 语义向量）
- AI 安全硬约束校验层（配伍禁忌 + 孕妇禁忌 + 毒性药检测）
- 知识检索页面（关键词 + 语义双路检索 + 条目管理 + 向量索引重建）
- 四诊分析对话框（结构化四诊输入 + 舌脉选项）

### Phase 5 ✅ 增值功能
- 工作台仪表盘（6项统计 + 7日就诊趋势图 + 库存预警 + 待办事项）
- 统计报表页（ECharts：就诊趋势/用药分析/处方统计）
- 统计后端API（/stats/dashboard, /stats/visits, /stats/herbs, /stats/prescriptions）
- 系统设置完善（API连接测试 + 数据备份导出/导入恢复/重置）

### Phase 6 ✅ 打包部署
- PyInstaller 配置（build.spec + run.py 入口）
- electron-builder 配置（electron-builder.yml，NSIS Windows 安装包）
- 数据备份/恢复API（/backup/export, /backup/import, /backup/reset）
- 扩展种子数据自动导入

## API 端点

| 模块 | 路径 | 说明 |
|------|------|------|
| 系统 | `/health` | 健康检查 |
| 系统 | `/api/v1/config` | 系统配置 |
| 患者 | `/api/v1/patients` | 患者 CRUD + 就诊 + 体质 |
| 药品 | `/api/v1/herbs` | 药材字典 + 配伍禁忌检查 |
| 药品 | `/api/v1/herbs/inventory/*` | 库存管理（入库/出库/预警/汇总） |
| 处方 | `/api/v1/prescriptions` | 处方 CRUD + 审核 + 发药 |
| 处方 | `/api/v1/prescriptions/classic-formulas` | 经典方库 |
| 问诊 | `/api/v1/diagnosis/chat` | 对话式智能问诊（DeepSeek+RAG） |
| 问诊 | `/api/v1/diagnosis/analyze` | 四诊辨证分析 |
| 问诊 | `/api/v1/diagnosis/status` | AI 服务状态 |
| 知识 | `/api/v1/knowledge/search` | 知识检索（关键词+语义） |
| 知识 | `/api/v1/knowledge/entries` | 知识条目管理 |
| 知识 | `/api/v1/knowledge/stats` | 知识库统计 |
| 统计 | `/api/v1/stats/dashboard` | 工作台数据 |
| 统计 | `/api/v1/stats/visits` | 就诊统计 |
| 统计 | `/api/v1/stats/herbs` | 用药统计 |
| 统计 | `/api/v1/stats/prescriptions` | 处方统计 |
| 备份 | `/api/v1/backup/export` | 导出备份 |
| 备份 | `/api/v1/backup/import` | 导入恢复 |
