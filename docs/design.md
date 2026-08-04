# 基因分析助手网站 — 系统设计文档

> **文档版本**：v3.0（三日冲刺版）  
> **最后更新**：2026-08-03  
> **文档状态**：已定稿  

---

## 目录

1. [概述](#1-概述)
2. [系统架构](#2-系统架构)
3. [技术栈](#3-技术栈)
4. [组件与接口](#4-组件与接口)
5. [数据模型](#5-数据模型)
6. [正确性属性](#6-正确性属性)
7. [错误处理](#7-错误处理)
8. [测试策略](#8-测试策略)
9. [AI 功能设计规范](#9-ai-功能设计规范)

---

## 1. 概述

基因分析助手网站是一套面向基因分析与遗传咨询的综合性 Web 应用平台。系统包含三个核心模块：（1）基因分析助手；（2）交互式健康模拟器；（3）生活方式建议。

本文档阐述系统的技术架构与实现方案。三日冲刺版采用 **Streamlit（MVP 主界面）+ FastAPI（后端 API）+ Gradio（AI 演示）** 的组合架构，优先保证核心功能的可交付性。

> **设计原则**：80/20 法则——用 20% 的技术复杂度覆盖 80% 的 MVP 需求。

---

## 2. 系统架构

### 2.1 分层架构总览（三日冲刺版）

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Streamlit    │  │ Gradio       │  │ 报告页面      │       │
│  │ 主仪表板     │  │ AI 判读演示   │  │ HTML 导出    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘       │
│         │                 │                                  │
│         └────────┬────────┘                                  │
│                  │                                           │
│    ┌─────────────┼─────────────┐                             │
│    │      FastAPI 后端 API     │                             │
│    │  - 文件上传  - 变异分析    │                             │
│    │  - 风险计算  - 建议生成    │                             │
│    │  - 报告导出  - 数据库查询  │                             │
│    └─────────────┼─────────────┘                             │
│                  │                                           │
│    ┌─────────────┼─────────────┐                             │
│    │  PostgreSQL │ Redis Cache  │ 外部 API 层                │
│    │  (主存储)   │ (会话/查询)  │ ClinVar | PharmGKB        │
│    └─────────────┘              └──────────────────────────┘  │
│                  │                                           │
│    ┌─────────────┼─────────────┐                             │
│    │   本地数据文件              │  文件存储                   │
│    │   data/clinvar/           │  uploads/ / exports/        │
│    │   data/1000genomes/       │                             │
│    │   data/giab/              │                             │
│    │   data/refseq/            │                             │
│    └───────────────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

1. **上传阶段**：文件 → 校验 → VCF/TSV 解析 → 临时存储
2. **分析阶段**：变异 → 数据库注释（ClinVar + 本地缓存）→ PRS 风险计算 → 结果汇编
3. **模拟阶段**：基因档案 + 环境因素滑块 → GxE 模型 → 健康预测轨迹
4. **建议阶段**：风险档案 → 证据库 → 个性化建议 → 实施计划

---

## 3. 技术栈

### 3.1 前端

| 类别 | 技术选型 | 选择理由 |
|------|----------|----------|
| **主框架** | **Streamlit** | 纯 Python，30 分钟搭建数据仪表板；基因资源文件已验证可行 |
| **AI 演示** | **Gradio** | 一行 `gr.Interface` 构建 AI 判读演示；`share=True` 一键分享 |
| **可视化** | **D3.js + Recharts**（通过 Streamlit 组件嵌入） | 成熟稳定的二维图表方案 |
| **样式** | Streamlit 原生 + 自定义 CSS | 满足 MVP 视觉需求 |

> **已移除**：~~Three.js 3D 蛋白结构~~。3D 分子可视化是独立工程问题，不在 MVP 范围内。如需蛋白结构展示，可在后续版本中集成 pGenomeViz 或 IGV.js。

### 3.2 后端

| 类别 | 技术选型 |
|------|----------|
| API 框架 | Python FastAPI（async/await） |
| 数据处理 | Pandas、NumPy、Biopython |
| VCF 解析 | `pyvcf` + `pandas`（双方案，互为回退） |
| 基因算法 | 自定义 PRS 计算器、孟德尔遗传模拟器 |
| 认证 | JWT + 会话管理 |
| AI 集成 | OpenAI API / Claude API |

### 3.3 数据库与缓存

| 类别 | 技术选型 | 用途 |
|------|----------|------|
| 主数据库 | PostgreSQL | 用户、报告、变异、建议 |
| 缓存 | Redis | 会话管理、数据库查询缓存 |
| 搜索 | PostgreSQL `tsvector` / `tsquery` | 全文搜索替代 ES |

> **已降级**：~~Elasticsearch~~。PostgreSQL 全文搜索在 MVP 数据量下完全足够，ES 延后至 Phase 2。

### 3.4 外部服务与数据库

| 服务 | 访问方式 | 用途 |
|------|----------|------|
| ClinVar | NCBI E-utilities API + 本地 VCF 文件 | 变异临床意义注释 |
| OMIM | Web 查询 | 遗传病-基因关联 |
| PharmGKB | REST API | 药物基因组学建议 |
| 1000 Genomes | 本地缓存（CNGBdb 镜像下载） | 人群频率参考 |
| GIAB | 本地缓存（CNGBdb 镜像下载） | 变异检测基准 |
| RefSeq | 本地缓存（CNGBdb 镜像下载） | 参考序列 |
| AI 服务 | OpenAI API / Claude API | AI 生成解读与建议 |

---

## 4. 组件与接口

### 4.1 Streamlit 页面结构

```
app.py（主入口）
├── pages/
│   ├── 1_Upload.py          # 文件上传页面
│   ├── 2_Analysis.py        # 分析结果仪表板
│   ├── 3_Simulator.py       # 健康模拟器
│   ├── 4_Recommendations.py # 生活方式建议
│   └── 5_Report.py          # 报告导出
├── components/
│   ├── variant_table.py     # 变异信息表格组件
│   ├── risk_chart.py        # 风险可视化图表（D3.js/Recharts）
│   ├── genome_browser.py    # 简化版染色体浏览器
│   └── disclaimer.py        # FDA 免责声明横幅组件
├── utils/
│   ├── vcf_parser.py        # VCF 文件解析
│   ├── clinvar_client.py    # ClinVar API 客户端
│   ├── prs_calculator.py    # PRS 计算器
│   └── report_generator.py  # 报告生成器
└── gradio_app.py            # Gradio AI 判读演示（独立运行）
```

### 4.2 FastAPI 后端端点

```yaml
/api/upload:
  post:
    summary: 上传基因报告文件（VCF/TSV）
    returns: { report_id, status, variant_count }

/api/analysis/{report_id}:
  get:
    summary: 获取分析结果
    returns: { variants, risk_scores, annotations }

/api/simulate:
  post:
    summary: 运行健康模拟
    body: { genetic_profile, environmental_factors }
    returns: { health_trajectory, risk_projections, confidence_intervals }

/api/recommendations:
  post:
    summary: 生成个性化建议
    body: { report_id, preferences }
    returns: { recommendations[], evidence_links }

/api/report/{report_id}/export:
  get:
    summary: 导出报告（PDF/HTML）
    query: { format: "pdf"|"html" }
```

### 4.3 Gradio AI 判读界面

```python
# gradio_app.py — 独立运行的 AI 判读演示
import gradio as gr

def analyze_variant(gene_name, variant_desc):
    """基于 ClinVar + AI 模型进行变异判读"""
    # 1. 本地 ClinVar 缓存查询
    # 2. 如未命中，调用 NCBI E-utilities
    # 3. AI 模型生成解读文本（含 FDA 免责声明）
    return result_with_disclaimer

iface = gr.Interface(
    fn=analyze_variant,
    inputs=[
        gr.Textbox(label="基因名称", placeholder="如 BRCA1"),
        gr.Textbox(label="变异描述", placeholder="如 c.68_69delAG")
    ],
    outputs=gr.Markdown(label="AI 判读结果"),
    title="基因报告 AI 判读工具",
    description="⚠️ 本工具仅供学习参考，不提供临床诊断。"
)
```

---

## 5. 数据模型

### 5.1 核心实体（精简版）

```sql
-- 用户（匿名化）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymized_id VARCHAR(64) UNIQUE NOT NULL,
    consent_status JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 基因报告
CREATE TABLE genetic_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    file_format VARCHAR(20) NOT NULL,
    parsing_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 基因变异
CREATE TABLE genetic_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES genetic_reports(id) ON DELETE CASCADE,
    chromosome VARCHAR(2) NOT NULL,
    position BIGINT NOT NULL,
    reference_allele VARCHAR(1000) NOT NULL,
    alternative_allele VARCHAR(1000) NOT NULL,
    rs_id VARCHAR(50),
    clinvar_significance VARCHAR(50),
    odds_ratio DECIMAL(10,6),
    prs_weight DECIMAL(10,6),
    population_frequency DECIMAL(10,6),
    
    INDEX idx_variant_location (chromosome, position)
);

-- 模拟场景
CREATE TABLE simulation_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    genetic_profile JSONB NOT NULL,
    environmental_factors JSONB NOT NULL,
    simulation_results JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 建议
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    evidence_level VARCHAR(20),
    priority_level INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. 正确性属性

### 属性 1：变异匹配准确率
对于任何从有效报告中提取的基因变异，系统应以超过 99% 的准确率正确匹配到 ClinVar 数据库条目。

### 属性 2：PRS 计算一致性
对于任意一组基因变异，重复的 PRS 计算结果变异系数应低于 0.1%。

### 属性 3：孟德尔遗传正确性
对于已知基因型的三口之家，后代基因型预测应 100% 遵循孟德尔遗传定律。

### 属性 4：数据隐私保护
系统应在全流程中保持匿名化与加密，防止成功的重识别。

### 属性 5：容错性
单点故障时系统以降级功能继续运行——外部 API 不可用时回退到本地缓存数据。

---

## 7. 错误处理

### 7.1 错误分类

| 错误类别 | 示例 | 处理策略 |
|----------|------|----------|
| 用户输入错误 | 无效 VCF 格式 | 返回具体格式要求 + 示例 |
| 数据库连接错误 | PostgreSQL 不可用 | 指数退避重试（3 次） |
| 外部 API 故障 | ClinVar API 超时 | 回退至本地缓存 VCF 文件 |
| 基因分析错误 | 低置信度变异 | 标注"待人工复核" |

### 7.2 回退机制

- **ClinVar API 不可用** → 使用本地 `data/clinvar/clinvar_grch38.vcf.gz`
- **1000 Genomes API 不可用** → 使用本地 `data/1000genomes/`
- **AI 模型不可用** → 显示基于规则的数据解读（不显示 AI 标签）

---

## 8. 测试策略

### 8.1 MVP 测试重点

| 测试类型 | 范围 | 工具 | 优先级 |
|----------|------|------|--------|
| 单元测试 | PRS 计算、VCF 解析、孟德尔遗传 | pytest + Hypothesis | P0 |
| 集成测试 | 上传→分析→结果完整链路 | pytest + FastAPI TestClient | P0 |
| UI 测试 | Streamlit 页面渲染 | 手动测试 + 截图验证 | P1 |
| 安全测试 | 数据隔离、SQL 注入、XSS | OWASP ZAP 基础扫描 | P1 |
| 性能测试 | 核心交互 < 2s | 手动计时 + pytest-benchmark | P2 |

---

## 9. AI 功能设计规范

### 9.1 AI 使用场景

| 场景 | AI 功能 | 触发方式 | 输出类型 |
|------|---------|----------|----------|
| 变异判读 | 基于 ClinVar + ACMG 指南生成解读文本 | 分析完成后自动 | Markdown 文本 |
| 健康建议 | 基于 PRS + 生活方式生成个性化建议 | 模拟完成后可选手动 | 结构化列表 |
| 术语解释 | 基因学术语的简单化解释 | 用户悬停/点击术语 | 弹窗文本 |

### 9.2 AI 输出安全约束

1. **禁止生成诊断结论**：AI prompt 中硬编码禁止输出"您患有""确诊"等词语
2. **强制附加免责声明**：每条 AI 生成内容末尾自动追加 FDA 免责声明
3. **来源可追溯**：AI 生成的解读需引用具体 ClinVar 条目 ID 或文献 PMID
4. **置信度标注**：区分"高置信度（多源验证）"和"低置信度（AI 推测）"

### 9.3 Prompt 安全护栏模板

```
<role>你是一个基因数据分析助手，只能提供教育和参考信息。</role>

<constraints>
- 绝对禁止：做出临床诊断或治疗建议
- 绝对禁止：使用"您患有""确诊""应当服用"等表述
- 必须执行：每次回答末尾追加免责声明
- 必须执行：引用具体数据库条目（ClinVar ID、OMIM #号）
</constraints>

<disclaimer>
⚠️ 本解读由 AI 模型自动生成，仅供学习参考。请咨询具备资质的遗传咨询师或医生获取专业建议。
</disclaimer>
```

---

> **相关文档**：
> - [需求规格说明书](requirements.md) — 含优先级分级与 FDA 合规声明
> - [三日冲刺计划](tasks.md) — 分 Day 1/2/3 的开发任务安排
> - [基因资源手册](../../基因资源.docx) — 医学数据库 API、Python 工具链、Web 框架教程
