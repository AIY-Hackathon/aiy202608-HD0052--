# 基因分析助手网站（Gene Analysis Assistant）

一套服务于**基因分析与遗传咨询**的综合性 Web 应用平台，支持基因报告上传分析、基因-环境交互模拟、个性化生活方式建议三大核心功能。

> **⚠️ 免责声明**：本产品为教育研究型项目，**不构成医疗器械**，**不提供临床诊断**。所有 AI 生成的基因解读仅供学习参考，不得替代专业医疗建议。

---

## 📁 项目文档（规范性文档）

本项目的需求、设计、任务均以**规范性文档**形式管理，请在开始开发前完整阅读：

| 文档 | 说明 | 链接 |
|------|------|------|
| **需求规格说明书** | 13 项功能需求、优先级分级（P0-P3）、FDA AI/ML 合规声明 | [docs/requirements.md](docs/requirements.md) |
| **系统设计文档** | 技术架构、组件接口、数据模型、测试策略、AI 设计规范 | [docs/design.md](docs/design.md) |
| **36 小时冲刺计划** | 三开发者并行任务安排（A 后端 / B 前端 / C 引擎）、时间线、Git 规范 | [docs/tasks.md](docs/tasks.md) |

---

## 🧑💻 开发分工（三路并行）

| 开发者 | 分支 | 负责内容 | 目录 |
|--------|------|----------|------|
| **A — 后端** | `part-a-backend` | FastAPI API、数据库、VCF 解析、ClinVar 查询、PRS 计算 | `backend/` |
| **B — 前端** | `part-b-frontend` | Streamlit 5 个页面、可视化组件、免责声明 | `frontend/` |
| **C — 引擎** | `part-c-engine` | GxE 模型、建议引擎、报告生成、Gradio AI 判读 | `engine/` + `gradio_app.py` |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- （可选）PostgreSQL + Redis（本地开发可用 SQLite 替代）

### 安装

```bash
git clone git@github.com:liang03060101-stack/AIY-Program.git
cd AIY-Program

# 创建虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动后端（Part A）

```bash
uvicorn backend.main:app --reload
# API 文档: http://127.0.0.1:8000/docs
```

### 启动前端（Part B）

```bash
streamlit run frontend/app.py
# 页面: http://localhost:8501
```

### 启动 AI 判读（Part C）

```bash
python gradio_app.py
```

---

## 📊 数据资源

| 数据集 | 路径 | 大小 | 用途 |
|--------|------|------|------|
| ClinVar VCF (GRCh38) | `data/clinvar/clinvar_grch38.vcf.gz` | ~184 MB | 变异临床意义注释（4,458,175 条） |
| ClinVar Tabix 索引 | `data/clinvar/clinvar_grch38.vcf.gz.tbi` | 596 KB | 快速位置查询 |

> 数据文件较大，不入 Git 库。缺失时运行 `python download_data.py` 重新下载。

---

## 🧬 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | Streamlit + D3.js/Recharts（可视化） |
| AI 演示 | Gradio |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据处理 | Pandas、NumPy |
| 数据库 | PostgreSQL + Redis（缓存） |
| AI 模型 | Claude API / OpenAI API |
