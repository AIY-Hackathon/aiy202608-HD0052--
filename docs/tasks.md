# 基因分析助手网站 — 36 小时三路并行冲刺计划

> **文档版本**：v4.0（三开发者并行版）  
> **最后更新**：2026-08-04  
> **时间预算**：36 小时（三个开发者并行，每人约 12 小时）  
> **仓库地址**：`git@github.com:liang03060101-stack/AIY-Program.git`

---

## 目录

1. [冲刺总览](#1-冲刺总览)
2. [项目结构](#2-项目结构target-repo-structure)
3. [Part A：后端核心 API 与数据库（开发者 A）](#3-part-a后端核心-api-与数据库开发者-a)
4. [Part B：Streamlit 前端页面（开发者 B）](#4-part-bstreamlit-前端页面开发者-b)
5. [Part C：模拟引擎·AI 判读·报告生成（开发者 C）](#5-part-c模拟引擎ai-判读报告生成开发者-c)
6. [三路并行时间线](#6-三路并行时间线)
7. [协作接口约定（三个 Part 必须同时遵守）](#7-协作接口约定三个-part-必须同时遵守)
8. [Git 分支与提交规范](#8-git-分支与提交规范)

---

## 1. 冲刺总览

### 1.1 目标

36 小时内交付一个**可演示的基因分析助手 Web 应用**，覆盖 5 个用户页面：

| 页面 | 名称 | 用户操作 | 对应需求 |
|------|------|----------|----------|
| P1 | 上传页面 | 拖拽上传 VCF 文件，查看上传进度 | R1 |
| P2 | 分析仪表板 | 查看变异列表、ClinVar 注释、风险评分 | R1, R7 |
| P3 | 健康模拟器 | 调整环境因素滑块，查看健康轨迹曲线 | R3 |
| P4 | 生活方式建议 | 查看个性化建议列表，勾选已完成项 | R4 |
| P5 | 报告导出 | 选择章节，导出 PDF / HTML 报告 | R8 |

### 1.2 三人分工

```
┌──────────────────────────────────────────────────────┐
│                    Streamlit 前端 (B)                  │
│  P1 上传 → P2 分析 → P3 模拟 → P4 建议 → P5 报告     │
│         │          │          │          │            │
│         └──────────┼──────────┼──────────┘            │
│                    │          │                       │
│  ┌─────────────────┼──────────┼──────────────────┐   │
│  │     FastAPI 后端 API (A)    │  模拟·AI·报告 (C) │   │
│  │  /upload  /analysis        │  /simulate        │   │
│  │  PostgreSQL  ClinVar查询   │  /recommendations │   │
│  │  VCF解析  PRS计算          │  /report/export   │   │
│  │                            │  Gradio AI 判读   │   │
│  └────────────────────────────┴───────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 1.3 每个 Part 的交付物

| Part | 负责内容 | 关键交付物 | 预计小时 |
|------|----------|-----------|----------|
| **A** | 后端 API + 数据库 + VCF 解析 + ClinVar 查询 + PRS 计算 | `backend/`、数据库 DDL、5 个 API 端点 | ~12h |
| **B** | Streamlit 全部 5 个页面 + 可视化图表 + 免责声明组件 | `app.py`、`pages/`、`components/` | ~12h |
| **C** | GxE 模型 + 建议引擎 + 报告生成器 + Gradio AI 判读 | `engine/`、`gradio_app.py`、报告模板 | ~12h |

---

## 2. 项目结构（Target Repo Structure）

```
AIY-Program/
├── README.md
├── requirements.txt
├── run.bat / run.sh                 # 一键启动脚本
├── .env.example
│
├── backend/                         # [Part A] FastAPI 后端
│   ├── main.py                      # FastAPI 应用入口
│   ├── config.py                    # 数据库/Redis/ClinVar 配置
│   ├── models.py                    # SQLAlchemy 模型
│   ├── schemas.py                   # Pydantic 请求/响应模型
│   ├── database.py                  # 数据库连接与会话
│   ├── api/
│   │   ├── upload.py                # POST /api/upload
│   │   ├── analysis.py              # GET /api/analysis/{report_id}
│   │   ├── simulate.py              # POST /api/simulate
│   │   ├── recommendations.py       # POST /api/recommendations
│   │   └── report.py                # GET /api/report/{id}/export
│   ├── services/
│   │   ├── vcf_parser.py            # VCF 解析服务
│   │   ├── clinvar_client.py        # ClinVar 查询（本地VCF + API）
│   │   └── prs_calculator.py        # PRS 风险评分
│   └── tests/
│       ├── test_vcf_parser.py
│       ├── test_clinvar.py
│       └── test_prs.py
│
├── frontend/                        # [Part B] Streamlit 前端
│   ├── app.py                       # 主入口（导航 + 免责声明横幅）
│   ├── pages/
│   │   ├── 1_📤_上传报告.py          # P1 Upload
│   │   ├── 2_📊_分析结果.py          # P2 Analysis
│   │   ├── 3_🧬_健康模拟.py          # P3 Simulator
│   │   ├── 4_💡_生活建议.py          # P4 Recommendations
│   │   └── 5_📄_报告导出.py          # P5 Report Export
│   ├── components/
│   │   ├── disclaimer.py            # FDA 免责声明横幅
│   │   ├── variant_table.py         # 变异表格组件
│   │   ├── risk_chart.py            # 风险可视化图表
│   │   └── ai_badge.py              # AI 内容标注标签
│   └── static/
│       └── style.css                # 自定义样式
│
├── engine/                          # [Part C] 模拟引擎·建议·报告·AI
│   ├── gxe_model.py                 # GxE 交互数学模型
│   ├── recommendation_engine.py     # 个性化建议生成
│   ├── report_generator.py          # PDF/HTML 报告生成器
│   ├── ai_interpreter.py            # AI 变异判读（Claude/OpenAI API）
│   └── tests/
│       ├── test_gxe.py
│       └── test_recommendations.py
│
├── gradio_app.py                    # [Part C] Gradio AI 判读演示
│
├── data/                            # 本地数据库文件（已下载）
│   └── clinvar/
│       ├── clinvar_grch38.vcf.gz    # ClinVar VCF (184MB, 4.46M variants)
│       └── clinvar_grch38.vcf.gz.tbi
│
└── docs/                            # 项目文档
    ├── requirements.md
    ├── design.md
    └── tasks.md                     # ← 本文件
```

---

## 3. Part A：后端核心 API 与数据库（开发者 A）

> **职责**：FastAPI 应用、PostgreSQL + Redis、VCF 解析、ClinVar 查询、PRS 计算、全部 5 个 API 端点  
> **依赖**：ClinVar 本地数据（已有）  
> **提供给 B 的接口**：5 个 REST API 端点  
> **提供给 C 的接口**：`/api/simulate` 和 `/api/recommendations` 的请求/响应格式（由 C 定义）

### A.1 第一阶段（0–6h）：基础架构 + 数据层

- [ ] **A1.1 环境与项目骨架**（30 min）
  - 创建 `backend/` 目录结构
  - 编写 `requirements.txt`：`fastapi, uvicorn, sqlalchemy, asyncpg, redis, pandas, pysam, python-multipart`
  - 编写 `backend/main.py`（FastAPI 应用 + CORS + 健康检查端点 `/api/health`）
  - _关联需求：R9.1_

- [ ] **A1.2 数据库设计与迁移**（1 h）
  - 编写 `backend/models.py`：users、genetic_reports、genetic_variants、simulation_scenarios、recommendations（5 张表，参考 design.md §5）
  - 编写 `backend/database.py`：SQLAlchemy async engine + session factory
  - 编写 Alembic 初始化迁移脚本，生成 DDL
  - _关联需求：R5.7_

- [ ] **A1.3 VCF 解析器**（1.5 h）
  - 编写 `backend/services/vcf_parser.py`
  - 支持 `pandas.read_csv`（快速）和 `pysam.VariantFile`（标准）双方案
  - 提取字段：CHROM、POS、ID、REF、ALT、QUAL、FILTER、INFO(GENEINFO)、INFO(CLNSIG)
  - 单元测试：真实 ClinVar VCF 文件，验证解析数量 > 4.4M
  - _关联需求：R1.1, R1.2_

- [ ] **A1.4 ClinVar 查询客户端**（1.5 h）
  - 编写 `backend/services/clinvar_client.py`
  - 优先使用 `pysam.tabix_index` 按 chr:pos 查询本地 VCF
  - 未命中时回退到 NCBI E-utilities API（`esearch` + `esummary`）
  - 查询结果写入 Redis 缓存（TTL: 24h）
  - 单元测试：已知 rsID 查询，验证返回 CLNSIG 字段
  - _关联需求：R7.1, R7.2_

- [ ] **A.5 PRS 计算器**（1.5 h）
  - 编写 `backend/services/prs_calculator.py`
  - 基于 ClinVar odds_ratio + 人群频率计算加权 PRS
  - 返回 95% 置信区间
  - 单元测试：手工计算值对比，误差 < 0.1%
  - _关联需求：R1.4, R11.1_

### A.2 第二阶段（6–12h）：API 端点 + 集成

- [ ] **A2.1 POST `/api/upload`**（1.5 h）
  - 接收 multipart VCF 文件
  - 校验格式（VCF 头 `##fileformat=VCF`）
  - 调用 `vcf_parser` 提取变异
  - 写入 genetic_reports 和 genetic_variants 表
  - 返回 `{ report_id, variant_count, status }`
  - _关联需求：R1.1, R1.2, R1.7_

- [ ] **A2.2 GET `/api/analysis/{report_id}`**（1.5 h）
  - 查询 genetic_variants（by report_id）
  - 对每个变异调用 `clinvar_client` 获取临床注释
  - 调用 `prs_calculator` 计算综合风险评分
  - 返回 `{ variants[], risk_scores{}, quality_score }`
  - _关联需求：R1.3, R1.4, R1.5_

- [ ] **A2.3 POST `/api/simulate`**（1.5 h）
  - 接收 `{ report_id, environmental_factors{} }`（与 Part C 约定格式）
  - 调用 Part C 编写的 `engine/gxe_model.py`
  - 将结果写入 simulation_scenarios 表
  - 返回 `{ scenario_id, health_trajectory[], confidence_intervals{} }`
  - _关联需求：R3.2, R3.5, R3.6_

- [ ] **A2.4 POST `/api/recommendations`**（1 h）
  - 接收 `{ report_id, preferences{} }`
  - 调用 Part C 编写的 `engine/recommendation_engine.py`
  - 返回 `{ recommendations[], evidence_links[] }`
  - _关联需求：R4.1, R4.2, R4.4_

- [ ] **A2.5 GET `/api/report/{report_id}/export`**（1 h）
  - 接收 `?format=pdf|html` 参数
  - 调用 Part C 编写的 `engine/report_generator.py`
  - 返回文件流（Content-Disposition: attachment）
  - _关联需求：R8.1, R8.2, R8.4_

- [ ] **A2.6 端到端测试与调优**（1 h）
  - 使用示例 VCF 走完整 API 链路（upload → analysis → simulate → recommendations → export）
  - 性能检查：50MB VCF 文件 < 30s 返回
  - 错误处理：无效文件返回 422 而非 500

---

## 4. Part B：Streamlit 前端页面（开发者 B）

> **职责**：全部 5 个 Streamlit 页面 + 可视化组件 + 免责声明横幅 + CSS 样式  
> **依赖**：Part A 的 API 端点（开发阶段可先用 mock 数据）  
> **提供给 A 的反馈**：API 响应格式如不符合前端需求，及时沟通调整

### B.1 第一阶段（0–6h）：主框架 + P1 + P2

- [ ] **B1.1 Streamlit 主入口与导航**（1 h）
  - 创建 `frontend/app.py`
  - `st.set_page_config`（标题: "基因分析助手"、图标: 🧬、布局: wide）
  - 侧边栏导航（5 个页面链接）
  - 加载 `components/disclaimer.py` 显示 FDA 免责声明横幅（需用户点击"同意"后进入）
  - _关联需求：R6.1, R6.3, R6.4_

- [ ] **B1.2 组件：免责声明横幅**（30 min）
  - `frontend/components/disclaimer.py`
  - 使用 `st.warning` 或自定义 HTML 显示完整 FDA 免责声明
  - Session state 存储用户同意状态
  - _关联需求：R6.4_

- [ ] **B1.3 P1：上传页面**（1.5 h）
  - `frontend/pages/1_📤_上传报告.py`
  - `st.file_uploader` 拖拽上传（限制 .vcf / .tsv / .txt，最大 100MB）
  - 上传进度条
  - 调用 `POST /api/upload`，成功后 `st.session_state.report_id = ...`
  - 文件格式校验反馈（绿色✅/红色❌）
  - _关联需求：R1.1, R6.1, R6.7_

- [ ] **B1.4 P2：分析仪表板**（2.5 h）
  - `frontend/pages/2_📊_分析结果.py`
  - 调用 `GET /api/analysis/{report_id}` 获取数据
  - **变异表格**（`components/variant_table.py`）：
    - `st.dataframe` 展示：染色体、位置、基因、临床意义、风险评分
    - 按 CLNSIG 颜色编码（Pathogenic=红，Benign=绿，VUS=灰）
  - **风险概览卡片**：3 列 `st.metric`（总变异数、致病性变异数、综合风险评分）
  - **染色体分布图**（`components/risk_chart.py`）：
    - 使用 `st.bar_chart` 展示各染色体变异数量
  - **AI 标注**（`components/ai_badge.py`）：
    - 所有 AI 生成解读后追加 "🤖 AI 辅助解读" 标签 + 免责声明文本
  - _关联需求：R1.5, R6.2, R6.4_
  - _关联需求（验证）：R11.2, R11.5（质量得分展示）_

- [ ] **B1.5 组件：变异表格**（45 min）
  - `frontend/components/variant_table.py`
  - `st.dataframe` 配置：列宽、颜色条件格式化
  - ClinVar 星级评审图标（⭐1-4 星 + 评审状态）
  - 变异详情展开（点击展开 INFO 字段完整内容）
  - _关联需求：R6.2_

### B.2 第二阶段（6–12h）：P3 + P4 + P5 + 样式打磨

- [ ] **B2.1 P3：健康模拟器**（2 h）
  - `frontend/pages/3_🧬_健康模拟.py`
  - **环境因素控制面板**（侧边栏）：
    - `st.slider`：运动频率（0-7 次/周）、BMI（16-40）、吸烟量（0-40 支/天）、饮酒量（0-14 杯/周）、饮食质量（1-5 级）
  - **实时模拟按钮**："开始模拟"
  - 调用 `POST /api/simulate`，传入 `{ report_id, environmental_factors }`
  - **健康轨迹图**（`components/risk_chart.py`）：
    - `st.line_chart`：5 年/10 年/20 年风险预测曲线
    - 置信区间阴影带
  - **场景管理**：
    - "保存当前场景"按钮 → `st.session_state.saved_scenarios`
    - 多场景对比叠加图
  - _关联需求：R3.1, R3.2, R3.3, R3.5_
  - _关联需求（验证）：R3.7（滑块范围生物学合理性校验）_

- [ ] **B2.2 P4：生活方式建议**（2 h）
  - `frontend/pages/4_💡_生活建议.py`
  - 调用 `POST /api/recommendations` 获取建议列表
  - **建议卡片列表**：
    - 每条建议：标题（粗体）、描述、证据来源链接、难度标签（🟢容易/🟡中等/🔴困难）、影响星级
    - 按优先级排序（影响力 × 可行性）
  - **进度跟踪**：
    - 每条建议前方 `st.checkbox`（完成后打勾）
    - Session state 持久化进度
  - _关联需求：R4.1, R4.2, R4.4, R4.5, R4.7_

- [ ] **B2.3 P5：报告导出**（1.5 h）
  - `frontend/pages/5_📄_报告导出.py`
  - **章节选择**：`st.multiselect`（变异摘要、风险评估、健康模拟、生活方式建议）
  - **格式选择**：`st.radio`（PDF / HTML）
  - **预览**：HTML 格式支持 `st.markdown` 预览
  - **下载按钮**：调用 `GET /api/report/{report_id}/export?format=pdf`
  - **水印检查**：预览中可见 FDA 免责声明水印
  - _关联需求：R8.1, R8.2, R8.3, R8.4, R8.5, R8.6_

- [ ] **B2.4 自定义样式与响应式检查**（1 h）
  - `frontend/static/style.css`
  - 医疗健康主题配色（蓝色主色调 #2563EB、绿色辅助 #10B981）
  - 卡片阴影、圆角统一
  - 移动端响应式适配（`st.columns` 自适应列宽）
  - FDA 标注颜色统一（黄色🤖/蓝色📋/橙色⚠️/绿色📖）
  - _关联需求：R6.1, R6.5_

- [ ] **B2.5 端到端 UI 测试**（30 min）
  - 使用示例 VCF 走完整用户流程（P1→P2→P3→P4→P5）
  - 截图验证：每个页面渲染正确
  - 错误状态测试：API 不可用时页面显示友好错误提示

---

## 5. Part C：模拟引擎·AI 判读·报告生成（开发者 C）

> **职责**：GxE 交互模型、个性化建议引擎、PDF/HTML 报告生成器、Gradio AI 判读演示  
> **依赖**：Part A 提供的数据模型（GeneticProfile schema 由 A 定义）和 API 端点约定  
> **提供给 A 的接口**：`engine/` 下的函数签名和参数格式  
> **提供给 B 的接口**：报告生成函数签名、Gradio 页面链接

### C.1 第一阶段（0–6h）：核心计算引擎

- [ ] **C1.1 项目骨架创建**（30 min）
  - 创建 `engine/`、`gradio_app.py` 目录结构
  - 编写 `engine/__init__.py`
  - _关联需求：R3.1, R4.1_

- [ ] **C1.2 GxE 交互模型**（2 h）
  - `engine/gxe_model.py`
  - 实现基因-环境交互数学模型：
    - 输入：PRS 向量 + 环境因素向量（exercise, bmi, smoking, alcohol, diet）
    - 输出：5/10/20 年健康风险轨迹 + 95% 置信区间
  - 环境因素权重参考已发表文献（附 DOI 注释）
  - 生物学合理性校验：输入值范围检查（如 BMI 16-40、吸烟 0-40 支/天）
  - 单元测试：测试不同环境组合下风险变化方向正确性
  - _关联需求：R3.1, R3.2, R3.4, R3.7_

- [ ] **C1.3 个性化建议引擎**（2 h）
  - `engine/recommendation_engine.py`
  - 输入：`genetic_risk_profile{}`（从 Part A 的 PRS 结果） + `user_preferences{}`
  - 输出：优先级排序的建议列表 `recommendations[]`
  - 建议数据库（硬编码/JSON 文件，常见疾病-生活方式映射）：
    - 心血管疾病 → 有氧运动、低盐饮食、戒烟
    - 2 型糖尿病 → 低碳水饮食、体重管理、定期血糖筛查
    - 乳腺癌（BRCA1/2）→ 定期乳腺筛查、预防性咨询
    - 药物代谢（PharmGKB）→ 华法林/他莫昔芬等药物剂量建议
  - 优先级 = 风险等级(1-5) × 证据强度(1-3) × 可行性(1-3)
  - 每条建议附带：evidence_level、supporting_studies[]、difficulty_level、estimated_time
  - 单元测试：给定已知风险档案，验证输出建议的有序性与合理性
  - _关联需求：R4.1, R4.2, R4.3, R4.4_

- [ ] **C1.4 AI 变异判读模块**（1.5 h）
  - `engine/ai_interpreter.py`
  - 调用 Claude API / OpenAI API
  - 输入：基因名称 + 变异描述 + ClinVar 注释摘要
  - Prompt 安全护栏：禁止诊断语言、强制引用 ClinVar ID、末尾追加免责声明
  - 输出：Markdown 格式的判读文本
  - API 不可用时的回退方案：基于规则输出纯 ClinVar 数据摘要
  - _关联需求：R6.4_

### C.2 第二阶段（6–12h）：报告生成 + Gradio 演示 + 集成

- [ ] **C2.1 PDF 报告生成器**（2 h）
  - `engine/report_generator.py`
  - 输入：`report_id` → 查询 Part A 的 API 获取全部数据
  - 输出：PDF 文件（使用 `reportlab`）
  - 报告结构：封面 → 变异摘要表 → 风险评估 → 健康模拟图 → 建议清单 → 免责声明页
  - 水印："⚠️ 非临床诊断用途 | 仅供学习参考"
  - 页眉/页脚：报告标题 + 页码 + 生成时间戳
  - 中文字体支持（使用 reportlab 注册系统字体）
  - _关联需求：R8.1, R8.2, R8.5, R8.6_

- [ ] **C2.2 HTML 报告生成器**（1.5 h）
  - 同上，输出为单文件 HTML（内联 CSS，可直接在浏览器打开）
  - 使用 Jinja2 模板渲染
  - 嵌入 D3.js 交互图表（与 Part B 可视化保持风格一致）
  - 水印通过 CSS `position: fixed` 实现
  - _关联需求：R8.3, R8.4_

- [ ] **C2.3 Gradio AI 判读演示**（1.5 h）
  - `gradio_app.py`
  - 输入字段：
    - `gene_name`（文本框，如 BRCA1）
    - `variant_description`（文本框，如 c.68_69delAG）
    - `clinvar_id`（可选，文本框）
  - 输出字段：
    - `result`（Markdown 渲染的判读结果）
  - 调用 `engine/ai_interpreter.py`
  - 公共分享链接：`gr.Interface(share=True)`
  - 示例输入：BRCA1 / TP53 / CFTR 各一个已知致病变异
  - _关联需求：R6.4, R12_

- [ ] **C2.4 引擎集成测试**（1 h）
  - 测试 GxE 模型 × API 端点（调用 Part A 的 `/api/simulate`）
  - 测试建议引擎 × API 端点（调用 Part A 的 `/api/recommendations`）
  - 测试报告生成器输出文件完整性
  - 测试 Gradio 页面可访问性

- [ ] **C2.5 部署脚本与 README**（1 h）
  - 编写 `requirements.txt`（所有三个 Part 的依赖汇总）
  - 编写 `.env.example`（API Key 占位、数据库连接串）
  - 编写 `run.bat`（Windows 一键启动：FastAPI + Streamlit + Gradio）
  - 编写 `run.sh`（Mac/Linux 一键启动）
  - 更新仓库 `README.md`（项目介绍、安装步骤、启动方式、团队成员分工）
  - _关联需求：R10.1_

---

## 6. 三路并行时间线

```
Hour    Part A (后端)              Part B (前端)              Part C (引擎/AI)
═══════════════════════════════════════════════════════════════════════════════
 0-2   │ A1.1 骨架               │ B1.1 主入口              │ C1.1 骨架
       │ A1.2 数据库+模型        │ B1.2 免责声明组件        │
       │                         │                          │
 2-4   │ A1.3 VCF解析器          │ B1.3 P1 上传页面         │ C1.2 GxE模型 (前半)
       │                          │                          │
 4-6   │ A1.4 ClinVar查询        │ B1.4 P2 分析仪表板       │ C1.2 GxE模型 (后半)
       │                          │                          │
 6-8   │ A1.5 PRS计算器          │ B1.4 P2 分析仪表板(续)   │ C1.3 建议引擎
       │                          │ B1.5 变异表格组件        │
─── 📡 API 联调点 #1 (A+B+C 对齐接口格式) ──────────────────────────────────
 8-10  │ A2.1 /api/upload        │ B2.1 P3 健康模拟器        │ C1.4 AI判读模块
       │ A2.2 /api/analysis      │                          │
       │                          │                          │
10-12  │ A2.3 /api/simulate      │ B2.2 P4 生活建议          │ C2.1 PDF报告生成
       │ (配合C提供gxe_model)    │                          │
       │                          │                          │
─── 📡 API 联调点 #2 (全功能前后端对接) ────────────────────────────────────
12-18  │ A2.4 /api/recommend     │ B2.3 P5 报告导出         │ C2.2 HTML报告
       │ A2.5 /api/report/export │ B2.4 样式打磨            │ C2.3 Gradio AI演示
       │                          │                          │
18-24  │ A2.6 端到端测试          │ B2.5 UI端到端测试        │ C2.4 引擎集成测试
       │                          │                          │
─── 🔧 Bug修复窗口 (24-30h) ────────────────────────────────────────────────
24-30  │ A: API Bug修复 +        │ B: UI Bug修复 +          │ C: 引擎参数调优 +
       │    性能优化              │    兼容性调整             │    报告模板完善
       │                          │                          │
─── 🚀 最终集成与发布 (30-36h) ─────────────────────────────────────────────
30-36  │ 三人合流：所有分支合并 → 端到端集成测试 → 一键启动验证 → 发布 v1.0.0
       │ C2.5 README + 部署脚本完成
═══════════════════════════════════════════════════════════════════════════════
```

### 关键联调点

| 联调点 | 时间 | 内容 | 参与方 |
|--------|------|------|--------|
| 📡 #1 | Hour 8 | 确认 5 个 API 的请求/响应 JSON 格式 | A + B + C |
| 📡 #2 | Hour 12 | 前后端全功能对接（真实 API 替代 mock） | A + B |
| 🔧 Bug Fix | Hour 24-30 | 修复集成测试中发现的问题 | 全员 |
| 🚀 发布 | Hour 36 | 合并所有分支 → 一键启动 → Tag v1.0.0 | 全员 |

---

## 7. 协作接口约定（三个 Part 必须同时遵守）

### 7.1 API 请求/响应格式

所有 API 响应遵循统一格式：

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

错误响应：

```json
{
  "success": false,
  "data": null,
  "error": { "code": "INVALID_FILE_FORMAT", "message": "仅支持 .vcf 和 .tsv 格式" }
}
```

### 7.2 Part A 必须提供的数据 Schema

```python
# backend/schemas.py — 公用数据结构

class VariantOut(BaseModel):
    id: str
    chromosome: str          # e.g. "1", "X"
    position: int            # e.g. 66926
    reference: str           # e.g. "AG"
    alternative: str         # e.g. "A"
    rs_id: str | None
    gene_name: str | None
    clinvar_significance: str | None  # e.g. "Pathogenic", "Benign", "VUS"
    clinvar_review_status: str | None  # e.g. "reviewed_by_expert_panel"
    odds_ratio: float | None
    population_frequency: float | None
    quality_score: float | None

class AnalysisResult(BaseModel):
    report_id: str
    variants: list[VariantOut]
    risk_scores: dict[str, float]  # e.g. {"cardio": 1.8, "diabetes": 0.9}
    overall_risk_level: str         # "low" | "moderate" | "high"
    confidence_intervals: dict[str, tuple[float, float]]

class SimulationRequest(BaseModel):
    report_id: str
    environmental_factors: dict[str, float]
    # {"exercise_freq": 3, "bmi": 24.5, "smoking": 0, "alcohol": 2, "diet_quality": 4}

class SimulationResult(BaseModel):
    scenario_id: str
    health_trajectory: list[dict]  # [{"year": 5, "risk": 0.12}, ...]
    confidence_intervals: dict[str, list[float]]
```

### 7.3 Part C 必须提供的函数签名

```python
# engine/gxe_model.py
def calculate_gxe(genetic_profile: dict, environmental_factors: dict) -> dict:
    """返回 {"trajectory": [...], "confidence": {...}}"""
    pass

# engine/recommendation_engine.py
def generate(genetic_risk_profile: dict, user_preferences: dict | None = None) -> list[dict]:
    """返回 [{"title": "有氧运动", "priority": 85, ...}, ...]"""
    pass

# engine/report_generator.py
def generate_pdf(report_data: dict) -> bytes:
    """返回 PDF 文件字节流"""
    pass

def generate_html(report_data: dict) -> str:
    """返回 HTML 字符串"""
    pass
```

### 7.4 Part B 的文件命名约定

Streamlit 页面文件必须按 `N_📋_中文名.py` 命名，N 从 1 开始，确保侧边栏排序正确：

```
1_📤_上传报告.py
2_📊_分析结果.py
3_🧬_健康模拟.py
4_💡_生活建议.py
5_📄_报告导出.py
```

---

## 8. Git 分支与提交规范

### 8.1 分支策略

```
main ────────────────────────────────────────────────
  │
  ├── part-a-backend    ← 开发者 A 在此分支工作
  ├── part-b-frontend   ← 开发者 B 在此分支工作
  └── part-c-engine     ← 开发者 C 在此分支工作
```

### 8.2 初始设置（所有人执行）

```bash
git clone git@github.com:liang03060101-stack/AIY-Program.git
cd AIY-Program

# 开发者 A
git checkout -b part-a-backend

# 开发者 B
git checkout -b part-b-frontend

# 开发者 C
git checkout -b part-c-engine
```

### 8.3 提交规范

- **提交信息格式**：`[Part] 阶段: 描述`
  - 例：`[A] A1.3: VCF parser implemented with pysam + pandas`
  - 例：`[B] B1.4: Analysis dashboard with variant table and risk chart`
  - 例：`[C] C1.2: GxE model with 5 environmental factors`

- **每次提交前**：确保代码可运行、无 import 错误

- **推送频率**：每完成一个子任务（如 A1.3）立即 commit + push

### 8.4 合并节奏

| 时间 | 操作 |
|------|------|
| Hour 8 | Part A + C 各自 push，B 拉取最新 backend/engine 代码 |
| Hour 12 | 全员 push，准备首次三路合并 |
| Hour 30 | 最终合并：A → main，B → main，C → main（解决冲突） |
| Hour 36 | Tag: `v1.0.0-mvp` |

---

> **相关文档**：
> - [需求规格说明书](requirements.md) — 含优先级分级与 FDA 合规声明
> - [系统设计文档](design.md) — 技术架构、组件接口、数据模型
> - [基因资源手册](../../基因资源.docx) — 可复用的 Python 代码示例与数据库 API 参考
