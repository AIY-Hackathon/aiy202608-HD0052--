# Part C 第二阶段开发状态

> **版本**：v2.0.0  
> **更新日期**：2026-08-05  
> **开发阶段**：第二阶段升级完成 — Explainable G×E Interactive Simulation Platform

---

## 核心升级总结

**从 "AI 健康评分系统" → "Explainable Gene × Environment Interactive Simulation Platform"**

核心理念：**Genes are not destiny.** 基因提供潜在倾向，环境因素决定可改变空间。

我们不是预测疾病，而是模拟不同生活方式选择如何影响未来健康趋势。

---

## 创新亮点

### 1. Health Trajectory Index (HTI)

`Health Score` → `Health Trajectory Index (HTI)`

HTI 是一个**教育性模拟指标**，而非健康评分。它展示：
- Genetic Background 的贡献
- Lifestyle Environment 的影响
- Gene × Environment Interaction 的交互效应
- 三者在时间轴上的累积趋势

**关键设计**：命名避免了"评分""风险"等疾病预测相关词汇，明确传达"这是一个模拟指标，不是诊断结果"。

### 2. Counterfactual Health Simulation（核心创新）

`engine/counterfactual.py` — "What if I changed my lifestyle?"

保持相同基因背景，只改变一个环境因素，系统重新模拟 HTI 变化。

这是比赛的**核心 Demo 卖点**：
> 同样的基因，不同的生活方式选择 → 不同的健康趋势。
> Interactive counterfactual simulation showing that lifestyle choices can reshape genetic trajectories.

### 3. Scenario Comparison

系统支持两个完整环境场景的 HTI 轨迹对比：
- Scenario A: Current Lifestyle
- Scenario B: Improved Lifestyle

输出 5/10/20 年两条轨迹的逐点差异，直观展示"同样的基因，不同的选择，不同的未来"。

### 4. Explainable AI Interpretation

每个 AI 输出包含 6 个字段：
| 字段 | 内容 |
|------|------|
| `genetic_story` | 基因背景叙述 |
| `main_driver` | 主导因素（基因/环境/交互） |
| `modifiable_factor` | 最具改善潜力的可调节因素 |
| `simulation_message` | 模拟洞察（核心叙述） |
| `scientific_note` | 科学依据说明 |
| `disclaimer` | 规范免责声明 |

### 5. Personalized Recommendations（非通用健康建议）

每条建议包含：
- `trigger_factor`: 触发该建议的具体因素
- `why_for_this_user`: **为什么这个建议适用于你**（个性化理由）
- `related_gene`: 与该建议相关的基因
- `confidence`: 科学可信度层

### 6. Scientific Confidence Layer

所有基因、建议、交互分析都带有三层可信度：
- `genetic_evidence`: 遗传证据等级
- `interaction_evidence`: 交互证据等级
- `lifestyle_evidence`: 生活方式证据等级

---

## 文件结构

```
engine/
├── __init__.py              # 包入口
├── config.py                # 模型参数（HTI命名 + 可信度层 + 反事实配置）
├── gxe_model.py             # G×E HTI 模拟引擎
├── counterfactual.py        # 反事实模拟 + 场景对比 ★ NEW
├── ai_interpreter.py        # 6字段解释输出（基因/驱动/因素/模拟/科学/免责）
├── recommendation_engine.py # 个性化建议（trigger + why + confidence）
├── report_generator.py      # HTML/PDF 报告生成器
├── knowledge/
│   └── gene_database.json   # 基因知识库（含 confidence 字段）
├── tests/
│   └── test_gxe.py          # 32 个测试用例
└── templates/               # 报告模板目录
```

---

## Demo 展示流程（比赛推荐）

```
Step 1: 输入基因档案（4 genes） + 当前生活方式（5 factors）
         → 系统输出 HTI 基线 + 5/10/20 年轨迹

Step 2: AI 解读
         → genetic_story + main_driver + modifiable_factor

Step 3: 反事实模拟（核心亮点）
         → What if I improved exercise? sleep? diet?
         → 单因素 HTI 变化 + "most impactful factor" 排名

Step 4: 场景对比（最终 Demo 画面）
         → 两条轨迹并排：Current vs Improved
         → "Same genes, different choices, different trajectory"
         → "Genes are not destiny"

Step 5: 个性化建议
         → 每条建议带 trigger_factor + why_for_this_user + related genes
         → 带 evidence confidence
```

---

## 测试结果

```
32 passed in 0.07s
- TestGxEModel: 10/10
- TestCounterfactual: 7/7
- TestAIInterpreter: 6/6
- TestRecommendationEngine: 6/6
- TestGeneDatabase: 3/3
```

## 运行命令

```bash
source .venv/bin/activate
python -m pytest engine/tests/test_gxe.py -v    # 全部测试
python -m engine.gxe_model                       # HTI 演示
python -m engine.counterfactual                  # 反事实模拟 + 场景对比
python -m engine.ai_interpreter                  # AI 6字段解释
python -m engine.recommendation_engine            # 个性化建议
```

---

## 科学合理性

### 参数来源
- **基因权重**：GWAS Catalog 荟萃分析效应量（群体水平 SNP-性状关联）
- **环境权重**：WHO 全球疾病负担研究 + 前瞻性队列研究
- **交互系数**：已发表 G×E 交互研究（候选基因-环境前瞻性队列）
- **时间参数**：纵向队列研究的年龄依赖趋势累积曲线

### 模型限制（透明标注）
- 个体 ≠ 群体：模型系数来自群体统计，不反映个体确定性结果
- 多基因交互：当前模型仅考虑单基因-环境交互
- 环境简化：仅包含 5 个主要可调节因素
- HTI 不是预测：它是模拟 + 教育工具，不是疾病预测

---

## 未来扩展方向

- 基因-基因上位效应（Epistasis）
- 更多环境因素（空气质量、社会支持、噪音）
- 基于真实 GWAS 效应量的参数自校准
- Gradio 交互式 Counterfactual Demo
- 中性因素分解（exercise type, diet composition）
