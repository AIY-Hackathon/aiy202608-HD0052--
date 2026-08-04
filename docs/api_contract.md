# GenoLife AI — API 契约文档

> **版本**：v1.0  
> **最后更新**：2026-08-04  
> **数据契约来源**：`genolife-ai/src/data/mockData.js`（React 前端）

---

## 1. 概览

| 端点 | 方法 | 用途 | 前端页面 |
|------|------|------|----------|
| `/api/health` | GET | 健康检查 | — |
| `/api/profile` | GET | 基因分析档案（概览 + 基因卡片 + 风险维度） | GeneMap |
| `/api/upload` | POST | 上传 VCF 基因报告 | 上传页 |
| `/api/analysis/{report_id}` | GET | 分析结果（变异 + 风险 + 档案） | 分析页 |
| `/api/simulate` | POST | 生活方式模拟 | LifeSimulation |
| `/api/recommendations` | GET | 个性化建议 + 30 天计划 | LifestylePlanner |

**Base URL**：`http://localhost:8000`

**统一响应格式**：

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

错误时：

```json
{
  "success": false,
  "data": null,
  "error": { "code": "INVALID_FILE_FORMAT", "message": "不是有效的 VCF 文件" }
}
```

---

## 2. GET /api/profile

返回基因分析档案，对齐 `mockData.js` 的 `userProfile` / `healthSummary` / `geneCards` / `riskDimensions`。

### 请求

```
GET /api/profile
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "user": {
      "name": "用户",
      "healthScore": 70,
      "geneticAge": 0,
      "chronologicalAge": 0
    },
    "summary": {
      "score": 70,
      "level": "moderate",
      "levelLabel": "Moderate Genetic Risk",
      "aiSummary": "正在分析您的基因数据。当前展示为基于常见基因位点的参考档案。"
    },
    "geneCards": [
      {
        "id": "apoe",
        "symbol": "APOE",
        "name": "Cognitive Health",
        "category": "Brain & Longevity",
        "riskLevel": "moderate",
        "summary": "您的 APOE 基因与生活方式健康密切相关...",
        "interpretation": "APOE 基因影响身体的代谢与健康调节...",
        "recommendations": [
          "每周进行 150 分钟以上有氧运动",
          "遵循地中海式饮食，补充 Omega-3",
          "保持阅读、拼图等认知训练活动"
        ],
        "icon": "🧠",
        "clinvar_significance": "Pathogenic",
        "odds_ratio": 3.0,
        "genotype": null
      }
    ],
    "riskDimensions": [
      { "key": "metabolic", "label": "Metabolic", "score": 50, "baseline": 50 },
      { "key": "cognitive", "label": "Cognitive", "score": 62, "baseline": 50 },
      { "key": "cardiovascular", "label": "Cardiovascular", "score": 50, "baseline": 50 },
      { "key": "athletic", "label": "Athletic", "score": 50, "baseline": 50 },
      { "key": "sleep", "label": "Sleep", "score": 50, "baseline": 50 }
    ]
  },
  "error": null
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `user.healthScore` | int 0-100 | 健康评分 |
| `summary.level` | string | `low` / `moderate` / `high` |
| `geneCards[].symbol` | string | 基因符号（APOE/FTO/ACTN3/CLOCK 等） |
| `geneCards[].riskLevel` | string | `low` / `moderate` / `elevated` / `advantage` |
| `riskDimensions[].key` | string | `metabolic` / `cognitive` / `cardiovascular` / `athletic` / `sleep` |
| `riskDimensions[].score` | int 5-95 | 维度风险分 |
| `riskDimensions[].baseline` | int | 基线（恒为 50） |

---

## 3. POST /api/upload

上传 VCF 基因报告文件，后端解析并分析。

### 请求

`multipart/form-data`，字段名 `file`。

```
POST /api/upload
Content-Type: multipart/form-data
file: example.vcf
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "report_id": "c8628358daf5",
    "variant_count": 3,
    "status": "completed",
    "original_filename": "example.vcf",
    "created_at": "2026-08-04T14:08:43.201646"
  },
  "error": null
}
```

### 错误码

| HTTP | 错误码 | 场景 |
|------|--------|------|
| 422 | `INVALID_FILE_FORMAT` | 不支持的文件扩展名 |
| 422 | `INVALID_VCF` | 不是有效的 VCF 文件 |
| 413 | `FILE_TOO_LARGE` | 超过 100MB |
| 500 | `DB_WRITE_FAILED` | 数据库写入失败 |

---

## 4. GET /api/analysis/{report_id}

返回一次上传的完整分析结果。

### 请求

```
GET /api/analysis/c8628358daf5
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "report": {
      "id": "c8628358daf5",
      "filename": "example.vcf",
      "format": "vcf",
      "status": "completed",
      "variant_count": 3,
      "created_at": "2026-08-04T14:08:43"
    },
    "variants": [
      {
        "id": "v_001",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
        "rs_id": "rs123",
        "gene_name": "APOE",
        "clinvar_significance": "Pathogenic",
        "clinvar_review_status": "reviewed_by_expert_panel",
        "odds_ratio": 3.52,
        "population_frequency": null,
        "risk_score": 0.87
      }
    ],
    "risk_scores": { "cardio": 1.0, "alzheimer": 2.4 },
    "overall_risk_level": "moderate",
    "confidence_intervals": { "alzheimer": [2.0, 2.8] },
    "profile": {
      "geneCards": [ ... ],
      "riskDimensions": [ ... ]
    }
  },
  "error": null
}
```

---

## 5. POST /api/simulate

接收生活因素，返回健康评分、风险维度、趋势和建议。对齐 `mockData.js` 的 `calculateHealthScore` / `calculateRiskDimensions` / `generateTrendData` / `generateRecommendations`。

### 请求

```json
{
  "factors": {
    "sleep": 5,
    "exercise": 2,
    "diet": 3,
    "stress": 8
  }
}
```

**因素范围**：

| key | 范围 | 说明 |
|-----|------|------|
| `sleep` | 3-10 | 睡眠时长（小时） |
| `exercise` | 0-7 | 每周运动天数 |
| `diet` | 1-10 | 饮食质量评分 |
| `stress` | 1-10 | 压力水平 |

### 响应示例

```json
{
  "success": true,
  "data": {
    "healthScore": 65,
    "optimizedScore": 84,
    "riskDimensions": [
      { "key": "metabolic", "label": "Metabolic", "score": 62, "baseline": 50 }
    ],
    "trendData": [
      { "year": 0, "current": 56, "optimized": 39 },
      { "year": 1, "current": 58, "optimized": 40 },
      { "year": 20, "current": 91, "optimized": 57 }
    ],
    "recommendations": [
      {
        "id": "s1",
        "pillar": "sleep",
        "icon": "🌙",
        "title": "将睡眠增加到 7-8 小时",
        "description": "您的基因档案显示对睡眠不足高度敏感...",
        "difficulty": "moderate",
        "impact": 4,
        "time": "今晚开始"
      }
    ]
  },
  "error": null
}
```

---

## 6. GET /api/recommendations

返回个性化建议和 30 天计划。建议字段对齐 `generateRecommendations`，30 天计划对齐 `thirtyDayPlan`。

### 请求

```
GET /api/recommendations?sleep=5&exercise=2&diet=3&stress=8
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "e1",
        "pillar": "exercise",
        "icon": "🏃",
        "title": "每周增加一天锻炼",
        "description": "结合您的力量型基因型...",
        "difficulty": "moderate",
        "impact": 5,
        "time": "本周内"
      }
    ],
    "thirtyDayPlan": {
      "goal": "改善代谢健康并降低长期心血管风险",
      "weeks": [
        {
          "label": "第 1 周 — 基础建立",
          "theme": "觉察与基线",
          "tasks": [
            { "day": "第 1-2 天", "title": "记录基线", "desc": "不做任何改变地记录睡眠、饮食和活动。" }
          ]
        }
      ]
    }
  },
  "error": null
}
```

### 建议字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `pillar` | string | `sleep` / `exercise` / `diet` / `stress` / `general` |
| `difficulty` | string | `easy` / `moderate` / `hard` |
| `impact` | int 1-5 | 影响程度 |
| `time` | string | 建议执行时间 |

---

## 7. 前端对接指南

### 7.1 从 mockData 切换为真实 API

React 前端当前直接 `import` mockData。切换步骤：

1. 创建 `src/api/client.js`（见仓库 `genolife-ai/src/api/client.js`）
2. 页面组件改为调用 API 客户端
3. 设置 `VITE_API_BASE` 环境变量指向后端

### 7.2 模拟器（LifeSimulation）

前端 `LifeSimulation.jsx` 当前用本地函数 `calculateHealthScore` / `calculateRiskDimensions` 实时计算。**推荐保持本地计算**（滑块调整需即时响应），仅在初始化时用 `/api/profile` 获取基因基线，用 `/api/simulate` 获取初始建议。

### 7.3 建议页（LifestylePlanner）

`LifestylePlanner.jsx` 的 `thirtyDayPlan` 直接替换为 `/api/recommendations?include_plan=true` 的返回。

---

## 8. 本地联调

```bash
# 1. 启动后端
cd AIY-Program
venv/Scripts/activate  # Windows
uvicorn backend.main:app --reload

# 2. 测试 API 文档
# 浏览器打开 http://127.0.0.1:8000/docs
```

### 快速测试命令

```bash
# 健康检查
curl http://127.0.0.1:8000/api/health

# 基因档案
curl http://127.0.0.1:8000/api/profile

# 模拟
curl -X POST http://127.0.0.1:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"factors":{"sleep":5,"exercise":2,"diet":3,"stress":8}}'

# 建议
curl "http://127.0.0.1:8000/api/recommendations?sleep=5&exercise=2&diet=3&stress=8"
```
