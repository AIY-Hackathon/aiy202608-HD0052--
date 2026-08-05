"""
基因分析引擎 — 对齐 GenoLife AI 新前端
========================================
基于 ClinVar 变异注释，生成前端所需的三种数据：

  1. geneCards        — 基因卡片列表（mockData.geneCards[]）
  2. riskDimensions   — 5 维健康风险评分（mockData.riskDimensions[]）
  3. risk_scores      — 疾病风险倍数（保留原有 PRS 能力）

健康维度（对齐前端 5 个维度）：
  metabolic / cognitive / cardiovascular / athletic / sleep

公式对齐前端 mockData.js 的 calculateHealthScore()。
"""
from __future__ import annotations

from math import log

# ============ 健康维度映射 ============

# 基因 → 健康维度（新前端）
DIMENSION_GENE_MAP: dict[str, set[str]] = {
    "metabolic": {"FTO", "MC4R", "TCF7L2", "LEP", "LEPR", "GCK", "HNF1A", "HNF4A", "KCNJ11"},
    "cognitive": {"APOE", "APP", "PSEN1", "PSEN2", "TOMM40", "CLU"},
    "cardiovascular": {"LDLR", "APOB", "PCSK9", "SCN5A", "AGT", "ACE", "ADD1", "CYP11B2", "KCNQ1", "KCNH2"},
    "athletic": {"ACTN3", "ACE", "MSTN", "PPARGC1A"},
    "sleep": {"CLOCK", "PER2", "PER3", "CRY1", "DEC2", "HCRTR2"},
}

# 维度标签（对齐前端 riskDimensions）
DIMENSION_LABELS: dict[str, str] = {
    "metabolic": "Metabolic",
    "cognitive": "Cognitive",
    "cardiovascular": "Cardiovascular",
    "athletic": "Athletic",
    "sleep": "Sleep",
}

# 维度基线分（前端 baseline: 50）
DIMENSION_BASELINE: dict[str, int] = {
    "metabolic": 50,
    "cognitive": 50,
    "cardiovascular": 50,
    "athletic": 50,
    "sleep": 50,
}

# 基因卡片元数据（符号 → 展示名/类别/图标）
GENE_CARD_META: dict[str, dict] = {
    "APOE": {"name": "Cognitive Health", "category": "Brain & Longevity", "icon": "🧠"},
    "FTO": {"name": "Metabolic Tendency", "category": "Metabolism", "icon": "⚡"},
    "ACTN3": {"name": "Muscle Performance", "category": "Athletic Performance", "icon": "💪"},
    "CLOCK": {"name": "Sleep & Circadian Rhythm", "category": "Sleep & Recovery", "icon": "🌙"},
    "TOMM40": {"name": "Neuroprotective Potential", "category": "Brain & Longevity", "icon": "🧠"},
    "LDLR": {"name": "Cholesterol Metabolism", "category": "Cardiovascular", "icon": "❤️"},
    "MC4R": {"name": "Appetite Regulation", "category": "Metabolism", "icon": "⚡"},
    "PER3": {"name": "Sleep Duration Preference", "category": "Sleep & Recovery", "icon": "🌙"},
    "MSTN": {"name": "Muscle Growth Potential", "category": "Athletic Performance", "icon": "💪"},
}

# 基因默认卡片（无变异时兜底）
DEFAULT_GENE_CARDS: list[str] = ["APOE", "FTO", "ACTN3", "CLOCK"]

# 基因风险等级划分（基于 ClinVar 意义）
RISK_LEVEL_MAP: dict[str, str] = {
    "Pathogenic": "elevated",
    "Likely_pathogenic": "elevated",
    "Uncertain_significance": "moderate",
    "Likely_benign": "low",
    "Benign": "low",
}

# 变异类型权重
SIGNIFICANCE_WEIGHT: dict[str, float] = {
    "Pathogenic": 1.0,
    "Likely_pathogenic": 0.8,
    "Uncertain_significance": 0.3,
    "Likely_benign": 0.1,
    "Benign": 0.0,
}

# 疾病风险映射（保留原有 PRS 能力）
DISEASE_GENE_MAP: dict[str, set[str]] = {
    "cardio": {"LDLR", "APOB", "PCSK9", "SCN5A", "KCNQ1", "KCNH2"},
    "diabetes": {"HNF1A", "HNF4A", "GCK", "TCF7L2", "KCNJ11"},
    "breast_cancer": {"BRCA1", "BRCA2", "PALB2", "CHEK2", "ATM"},
    "colorectal": {"APC", "MLH1", "MSH2", "MSH6", "PMS2", "MUTYH"},
    "alzheimer": {"APOE", "APP", "PSEN1", "PSEN2"},
    "obesity": {"MC4R", "FTO", "LEP", "LEPR"},
    "hypertension": {"AGT", "ACE", "ADD1", "CYP11B2"},
}


# ============ 基础函数 ============

def _normalize_gene(gene_name: str) -> str:
    """规范化基因名（大写、去符号后缀）。"""
    if not gene_name:
        return ""
    return gene_name.upper().split("-")[0].strip()


def significance_weight(clinvar_sig: str | None) -> float:
    """将 ClinVar 临床意义映射为权重。"""
    if not clinvar_sig:
        return 0.1
    for sig in clinvar_sig.split(";"):
        sig = sig.strip().replace(" ", "_")
        for key, weight in SIGNIFICANCE_WEIGHT.items():
            if sig.lower() == key.lower():
                return weight
    return 0.1


def classify_gene_to_dimension(gene_name: str) -> str | None:
    """将基因归类到健康维度。"""
    gene = _normalize_gene(gene_name)
    if not gene:
        return None
    for dim, genes in DIMENSION_GENE_MAP.items():
        if gene in genes:
            return dim
    return None


def classify_gene_to_disease(gene_name: str) -> str | None:
    """将基因归类到疾病类别（保留原 PRS 能力）。"""
    gene = _normalize_gene(gene_name)
    if not gene:
        return None
    for disease, genes in DISEASE_GENE_MAP.items():
        if gene in genes:
            return disease
    return None


# ============ 风险维度评分 ============

def calculate_dimension_scores(variants: list[dict]) -> list[dict]:
    """计算 5 维健康风险评分（对齐前端 riskDimensions[]）。

    维度分 = 50(基线) + Σ(变异权重 × 风险偏移)
    风险偏移基于 ClinVar 意义与 odds_ratio。
    """
    # 各维度累计风险贡献
    dim_risk: dict[str, float] = {dim: 50.0 for dim in DIMENSION_LABELS}

    for v in variants:
        dim = classify_gene_to_dimension(v.get("gene_name", ""))
        if not dim:
            continue
        weight = significance_weight(v.get("clinvar_significance"))
        odds = v.get("odds_ratio") or 1.0
        if odds > 1:
            # 风险基因：odds 越高，维度分越高（风险越大）
            contribution = weight * min((log(odds) / log(4)) * 15, 15)
        else:
            contribution = -weight * 5  # 保护性变异降低风险
        dim_risk[dim] += contribution

    # 生成前端结构
    result = []
    for dim in DIMENSION_LABELS:
        score = int(round(dim_risk[dim]))
        score = max(5, min(95, score))
        result.append({
            "key": dim,
            "label": DIMENSION_LABELS[dim],
            "score": score,
            "baseline": DIMENSION_BASELINE[dim],
        })
    return result


# ============ 健康评分（对齐前端公式）============

def calculate_health_score(
    factors: dict[str, float] | None = None,
    genetic_baseline: int = 72,
) -> int:
    """计算 0-100 健康评分（公式对齐前端 calculateHealthScore）。

    影响因素：sleep(3-10) exercise(0-7) diet(1-10) stress(1-10)
    """
    f = factors or {}
    sleep = float(f.get("sleep", 6))
    exercise = float(f.get("exercise", 3))
    diet = float(f.get("diet", 5))
    stress = float(f.get("stress", 6))

    sleep_impact = ((sleep - 6) / 7) * 8
    exercise_impact = ((exercise - 3) / 7) * 10
    diet_impact = ((diet - 5) / 9) * 12
    stress_impact = ((6 - stress) / 9) * 10  # 反向：低压力 = 高分

    total_deviation = sleep_impact + exercise_impact + diet_impact + stress_impact
    score = round(genetic_baseline + total_deviation)
    return max(35, min(98, score))


def calculate_dimension_scores_with_factors(
    variants: list[dict],
    factors: dict[str, float] | None = None,
) -> list[dict]:
    """基于遗传 + 生活方式因素的综合维度评分（对齐前端 calculateRiskDimensions）。"""
    base = calculate_dimension_scores(variants)
    f = factors or {}
    sleep = float(f.get("sleep", 6))
    exercise = float(f.get("exercise", 3))
    diet = float(f.get("diet", 5))
    stress = float(f.get("stress", 6))

    adjustments = {
        "metabolic": -(diet - 5) * 3 - (exercise - 3) * 2 + (stress - 5) * 1.5,
        "cognitive": -(sleep - 6) * 3 - (stress - 5) * 2 + (exercise - 3) * -0.5,
        "cardiovascular": -(exercise - 3) * 4 - (diet - 5) * 2 + (stress - 5) * 2,
        "athletic": -(exercise - 3) * -3 + (sleep - 6) * -1,
        "sleep": -(sleep - 6) * -5 + (stress - 5) * 3,
    }
    for dim in base:
        dim["score"] = max(5, min(95, int(round(dim["score"] + adjustments.get(dim["key"], 0)))))
    return base


def generate_trend_data(variants: list[dict], factors: dict[str, float] | None = None) -> list[dict]:
    """生成健康风险趋势（对齐前端 generateTrendData）。"""
    risks = calculate_dimension_scores_with_factors(variants, factors)
    years = [0, 1, 3, 5, 10, 15, 20]
    avg_risk = sum(r["score"] for r in risks) / len(risks) if risks else 50
    return [
        {
            "year": year,
            "current": int(round(avg_risk + year * 1.8)),
            "optimized": int(round(avg_risk * 0.7 + year * 0.9)),
        }
        for year in years
    ]


# ============ 基因卡片生成 ============

def risk_level_from_significance(sig: str | None) -> str:
    """将 ClinVar 意义映射为前端 riskLevel。"""
    if not sig:
        return "moderate"
    for s in sig.split(";"):
        s = s.strip().replace(" ", "_")
        if s in RISK_LEVEL_MAP:
            return RISK_LEVEL_MAP[s]
    return "moderate"


def generate_gene_cards(variants: list[dict], top_n: int = 4) -> list[dict]:
    """从变异生成前端 geneCards 结构。

    优先展示 DEFAULT_GENE_CARDS 中的基因（与前端演示一致）。
    若无变异数据，返回默认卡片。
    """
    # 收集有意义的变异基因
    gene_info: dict[str, list[dict]] = {}
    for v in variants:
        gene = _normalize_gene(v.get("gene_name", ""))
        if not gene:
            continue
        if gene not in gene_info:
            gene_info[gene] = []
        gene_info[gene].append(v)

    # 决定展示哪些基因（优先默认卡片中出现的）
    display_genes = [g for g in DEFAULT_GENE_CARDS if g in gene_info]
    display_genes += [g for g in gene_info if g not in DEFAULT_GENE_CARDS]
    display_genes = display_genes[:top_n]

    # 若无匹配基因，用默认卡片兜底
    if not display_genes:
        display_genes = DEFAULT_GENE_CARDS[:top_n]

    cards = []
    for gene in display_genes:
        variants_of_gene = gene_info.get(gene, [])
        meta = GENE_CARD_META.get(gene, {
            "name": f"{gene} Gene", "category": "Genetic Analysis", "icon": "🧬"
        })

        if variants_of_gene:
            sig = variants_of_gene[0].get("clinvar_significance")
            odds = variants_of_gene[0].get("odds_ratio")
            risk_level = risk_level_from_significance(sig)
            interpretation = _build_interpretation(gene, sig, odds)
            summary = _build_summary(gene, sig)
            recs = _build_recommendations(gene)
        else:
            risk_level = "moderate"
            sig = None
            odds = None
            interpretation = _build_interpretation(gene, None, None)
            summary = _build_summary(gene, None)
            recs = _build_recommendations(gene)

        cards.append({
            "id": gene.lower(),
            "symbol": gene,
            "name": meta["name"],
            "category": meta["category"],
            "riskLevel": risk_level,
            "summary": summary,
            "interpretation": interpretation,
            "recommendations": recs,
            "icon": meta["icon"],
            "clinvar_significance": sig,
            "odds_ratio": odds,
        })
    return cards


def _build_summary(gene: str, sig: str | None) -> str:
    """生成基因卡片摘要。"""
    if sig and sig.lower().startswith(("pathogenic", "likely_pathogenic")):
        return f"您的 {gene} 基因存在临床显著变异，与相关健康风险升高有关。"
    if sig and sig.lower().startswith("benign"):
        return f"您的 {gene} 基因未发现显著致病变异，遗传风险处于正常水平。"
    return f"您的 {gene} 基因与生活方式健康密切相关，遗传因素可被生活方式显著调节。"


def _build_interpretation(gene: str, sig: str | None, odds: float | None) -> str:
    """生成基因卡片解读。"""
    if odds and odds > 1:
        return (
            f"{gene} 基因变异的效应量约为 {odds:.1f} 倍。"
            "研究表明，规律运动、均衡饮食和良好睡眠可显著抵消遗传易感性，"
            "生活方式对表型的影响可达 30-40%。"
        )
    return (
        f"{gene} 基因影响身体的代谢与健康调节。"
        "遗传只是影响因素之一，积极的生活方式改变可大幅改善健康轨迹。"
    )


def _build_recommendations(gene: str) -> list[str]:
    """基于基因生成建议（对齐前端 geneCards.recommendations[]）。"""
    dim = classify_gene_to_dimension(gene)
    if dim == "metabolic":
        return [
            "优先选择高蛋白、高纤维饮食以增强饱腹感",
            "限制添加糖和精制碳水化合物的摄入",
            "每天目标 10,000 步",
        ]
    if dim == "cognitive":
        return [
            "每周进行 150 分钟以上有氧运动",
            "遵循地中海式饮食，补充 Omega-3",
            "保持阅读、拼图等认知训练活动",
        ]
    if dim == "cardiovascular":
        return [
            "每周进行 150 分钟中等强度有氧运动",
            "控制钠摄入，增加蔬果比例",
            "定期监测血压和血脂水平",
        ]
    if dim == "athletic":
        return [
            "每周加入 2-3 次高强度间歇训练",
            "力量训练每周 2-3 次以获得最佳效果",
            "高强度训练后注意充分恢复",
        ]
    if dim == "sleep":
        return [
            "早晨接触阳光以重置生物钟",
            "即使周末也保持一致的作息时间",
            "目标睡眠前 1-2 小时避免蓝光",
        ]
    return [
        "保持规律运动和均衡饮食",
        "定期体检，关注关键健康指标",
    ]


# ============ 建议引擎 ============

def generate_recommendations(factors: dict[str, float] | None = None) -> list[dict]:
    """生成个性化建议（对齐前端 generateRecommendations 输出结构）。

    每条建议含：id / pillar / icon / title / description / difficulty / impact / time
    """
    f = factors or {}
    sleep = float(f.get("sleep", 6))
    exercise = float(f.get("exercise", 3))
    diet = float(f.get("diet", 5))
    stress = float(f.get("stress", 6))

    recs: list[dict] = []

    if sleep < 7:
        recs.append({
            "id": "s1", "pillar": "sleep", "icon": "🌙",
            "title": "将睡眠增加到 7-8 小时",
            "description": "您的基因档案显示对睡眠不足高度敏感。每晚多睡 1 小时可降低代谢风险标志物。",
            "difficulty": "moderate", "impact": 4, "time": "今晚开始",
        })
    if exercise < 4:
        recs.append({
            "id": "e1", "pillar": "exercise", "icon": "🏃",
            "title": "每周增加一天锻炼",
            "description": "结合您的力量型基因型，每周增加一次高强度训练效果显著。",
            "difficulty": "moderate", "impact": 5, "time": "本周内",
        })
    if diet < 7:
        recs.append({
            "id": "d1", "pillar": "diet", "icon": "🥗",
            "title": "增加高纤维全食物摄入",
            "description": "您的代谢基因型受益于高纤维饮食，目标每日 30g 膳食纤维。",
            "difficulty": "easy", "impact": 4, "time": "立即开始",
        })
    if stress > 5:
        recs.append({
            "id": "st1", "pillar": "stress", "icon": "🧘",
            "title": "每天 10 分钟正念练习",
            "description": "您的昼夜节律基因对压力敏感，每日简短冥想可改善睡眠并降低皮质醇。",
            "difficulty": "easy", "impact": 3, "time": "每天 10 分钟",
        })
    if exercise >= 4 and sleep >= 7:
        recs.append({
            "id": "g1", "pillar": "general", "icon": "🎯",
            "title": "您正在养成良好习惯",
            "description": "继续保持！持续坚持才是改变基因表达的关键。可考虑增加活动多样性。",
            "difficulty": "easy", "impact": 2, "time": "持续进行",
        })

    return recs


# ============ 30 天计划 ============

def generate_thirty_day_plan(goal: str | None = None) -> dict:
    """生成 30 天健康计划（对齐前端 thirtyDayPlan 结构）。"""
    return {
        "goal": goal or "改善代谢健康并降低长期心血管风险",
        "weeks": [
            {
                "label": "第 1 周 — 基础建立",
                "theme": "觉察与基线",
                "tasks": [
                    {"day": "第 1-2 天", "title": "记录基线", "desc": "不做任何改变地记录睡眠、饮食和活动。"},
                    {"day": "第 3-4 天", "title": "每日 30 分钟步行", "desc": "简单的每日散步——留意身体感受。"},
                    {"day": "第 5-7 天", "title": "审视餐盘", "desc": "为每餐拍照，仅觉察，不评判。"},
                ],
            },
            {
                "label": "第 2 周 — 激活",
                "theme": "小改变，大影响",
                "tasks": [
                    {"day": "第 8-9 天", "title": "提前 30 分钟就寝", "desc": "您的生物钟基因对渐进式调整反应良好。"},
                    {"day": "第 10-12 天", "title": "2 次 HIIT 训练", "desc": "发挥您的力量基因优势，进行短时高强度训练。"},
                    {"day": "第 13-14 天", "title": "替换一次加工零食", "desc": "用坚果或水果代替。您的代谢基因会感谢您。"},
                ],
            },
            {
                "label": "第 3 周 — 整合",
                "theme": "建立动量",
                "tasks": [
                    {"day": "第 15-17 天", "title": "周日备餐", "desc": "计划并准备 3 天的高纤维餐食。"},
                    {"day": "第 18-19 天", "title": "早晨光照", "desc": "户外 10 分钟晨光以重置昼夜节律。"},
                    {"day": "第 20-21 天", "title": "尝试新活动", "desc": "您的力量基因偏好多样化的爆发性活动。"},
                ],
            },
            {
                "label": "第 4 周 — 维持",
                "theme": "终身习惯",
                "tasks": [
                    {"day": "第 22-24 天", "title": "反思精力水平", "desc": "记录与第 1 天的对比，留意趋势。"},
                    {"day": "第 25-27 天", "title": "分享进展", "desc": "社会支持有助于巩固基因表达的改变。"},
                    {"day": "第 28-30 天", "title": "规划下一个 30 天", "desc": "设定新目标。健康是一场持续旅程。"},
                ],
            },
        ],
    }


# ============ 兼容辅助 ============

def calculate_prs(variants: list[dict], disease: str | None = None) -> dict:
    """计算疾病多基因风险评分（保留原 PRS 能力，供真实分析使用）。"""
    if not variants:
        risk = {d: 1.0 for d in DISEASE_GENE_MAP}
        return {
            "risk_scores": risk,
            "overall_risk_level": "low",
            "confidence_intervals": {d: [0.85, 1.15] for d in DISEASE_GENE_MAP},
        }

    diseases = list(DISEASE_GENE_MAP.keys()) if disease is None else [disease]
    risk_multipliers: dict[str, float] = {}

    for disease_key in diseases:
        relevant = [
            v for v in variants
            if classify_gene_to_disease(v.get("gene_name", "")) == disease_key
        ]
        if not relevant:
            risk_multipliers[disease_key] = 1.0
            continue

        combined = 1.0
        for v in relevant:
            weight = significance_weight(v.get("clinvar_significance"))
            if weight <= 0:
                continue
            odds = v.get("odds_ratio") or 1.0
            combined *= max(1.0, odds) ** weight
        risk_multipliers[disease_key] = round(min(combined, 10.0), 2)

    max_risk = max(risk_multipliers.values()) if risk_multipliers else 1.0
    if max_risk < 1.2:
        level = "low"
    elif max_risk < 2.0:
        level = "moderate"
    else:
        level = "high"

    confidence = {
        k: [
            round(max(v * 0.85, 0.1), 2),
            round(min(v * 1.15, 12.0), 2),
        ]
        for k, v in risk_multipliers.items()
    }

    return {
        "risk_scores": risk_multipliers,
        "overall_risk_level": level,
        "confidence_intervals": confidence,
    }


def risk_score_for_variant(clinvar_sig: str | None, odds_ratio: float | None = None) -> float:
    """为单个变异生成 0-1 风险评分（前端展示用）。"""
    weight = significance_weight(clinvar_sig)
    if odds_ratio and odds_ratio > 1:
        return round(min(weight * (log(odds_ratio) / log(4)) + weight * 0.2, 0.99), 2)
    return round(weight, 2)


# =============================================================================
# 关键基因智能抓取 + 科学分析
# =============================================================================

# 基因科学知识库
_GENE_SCIENCE: dict[str, dict] = {
    "APOE": {
        "name": "Apolipoprotein E",
        "cn_name": "载脂蛋白E",
        "function": "编码载脂蛋白E，参与脂蛋白代谢、胆固醇转运和神经修复。ε4 等位基因与阿尔茨海默病风险升高相关。",
        "evidence": "high",
        "variants": ["rs429358", "rs7412"],
        "population_impact": "约 25% 人群携带至少一个 ε4 等位基因",
        "lifestyle": "规律有氧运动可降低 ε4 携带者认知风险约 30%；地中海饮食有保护作用",
    },
    "FTO": {
        "name": "Fat Mass and Obesity-Associated",
        "cn_name": "肥胖相关基因",
        "function": "调控食欲和能量消耗。风险等位基因与体重管理挑战相关，但运动可显著抵消其效应。",
        "evidence": "high",
        "variants": ["rs9939609"],
        "population_impact": "约 40-45% 人群携带风险等位基因（A）",
        "lifestyle": "规律运动可降低 FTO 相关体重影响约 27%；高蛋白高纤维饮食有效",
    },
    "CLOCK": {
        "name": "Circadian Locomotor Output Cycles Kaput",
        "cn_name": "生物钟基因",
        "function": "核心昼夜节律调控因子，影响睡眠-觉醒周期和代谢节律。变异与睡眠偏好和节律稳定性相关。",
        "evidence": "moderate",
        "variants": ["rs1801260"],
        "population_impact": "常见多态性，影响睡眠偏好（晨型/夜型）",
        "lifestyle": "保持规律作息、固定就寝时间可优化节律；限时进食有助代谢同步",
    },
    "ACTN3": {
        "name": "Alpha-Actinin-3",
        "cn_name": "α-辅肌动蛋白-3",
        "function": "编码快肌纤维结构蛋白。R577X 多态性与爆发力/耐力表现相关，是正常的人类基因变异。",
        "evidence": "high",
        "variants": ["rs1815739"],
        "population_impact": "约 18% 人群完全缺乏 ACTN3 蛋白（耐力型）",
        "lifestyle": "力量型基因型适合高强度间歇训练；耐力型适合长距离有氧",
    },
    "BRCA1": {
        "name": "Breast Cancer Gene 1",
        "cn_name": "乳腺癌基因1",
        "function": "DNA 损伤修复关键基因。致病变异显著升高乳腺癌和卵巢癌风险。",
        "evidence": "high",
        "variants": ["rs80357906"],
        "population_impact": "致病性变异罕见（约 1/400），但外显率高",
        "lifestyle": "定期乳腺筛查、预防性咨询；健康生活方式可降低部分风险",
    },
    "LDLR": {
        "name": "Low-Density Lipoprotein Receptor",
        "cn_name": "低密度脂蛋白受体",
        "function": "清除血液中 LDL 胆固醇。变异可导致家族性高胆固醇血症，升高心血管风险。",
        "evidence": "high",
        "variants": ["rs121908025"],
        "population_impact": "杂合致病变异约 1/250，显著升高 LDL",
        "lifestyle": "低饱和脂肪饮食 + 规律运动 + 他汀治疗（遵医嘱）",
    },
}

_EVIDENCE_WEIGHT = {"high": 1.0, "moderate": 0.7, "low": 0.4}


def _get_gene_science(gene: str) -> dict:
    """获取基因科学信息（兜底用通用信息）。"""
    if gene in _GENE_SCIENCE:
        return _GENE_SCIENCE[gene]
    dim = classify_gene_to_dimension(gene)
    disease = classify_gene_to_disease(gene)
    return {
        "name": f"{gene}",
        "cn_name": f"{gene} 基因",
        "function": f"{gene} 基因参与健康调控。具体机制因变异位点而异，建议结合 ClinVar 注释解读。",
        "evidence": "moderate",
        "variants": [],
        "population_impact": "人群频率因人群而异",
        "lifestyle": "保持健康生活方式可部分调节遗传风险",
    }


def identify_key_genes(
    variants: list[dict],
    top_n: int = 6,
    min_score: float = 1.0,
) -> list[dict]:
    """从用户样本中智能抓取关键基因。

    综合评分 = 变异严重度(0-3) × 证据权重(0.4-1.0) × 基因重要性(1-2)
    """
    gene_info: dict[str, list[dict]] = {}
    for v in variants:
        gene = _normalize_gene(v.get("gene_name", ""))
        if not gene:
            continue
        gene_info.setdefault(gene, []).append(v)

    if not gene_info:
        return []

    results = []
    for gene, gene_variants in gene_info.items():
        worst_sig = min(gene_variants, key=lambda v: _severity_of_sig(v.get("clinvar_significance")))
        severity = _severity_of_sig(worst_sig.get("clinvar_significance"))
        severity_score = 3 - severity

        science = _get_gene_science(gene)
        evidence_w = _EVIDENCE_WEIGHT.get(science.get("evidence", "moderate"), 0.7)
        importance = 2.0 if classify_gene_to_dimension(gene) or classify_gene_to_disease(gene) else 1.0
        score = (severity_score + 1) * evidence_w * importance

        if score < min_score:
            continue

        rs_ids = [v.get("rs_id") for v in gene_variants if v.get("rs_id")]
        results.append({
            "symbol": gene,
            "name": science.get("name", gene),
            "cn_name": science.get("cn_name", gene),
            "function": science.get("function", ""),
            "evidence_level": science.get("evidence", "moderate"),
            "population_impact": science.get("population_impact", ""),
            "lifestyle": science.get("lifestyle", ""),
            "risk_level": risk_level_from_significance(worst_sig.get("clinvar_significance")),
            "severity_score": round(severity_score, 1),
            "score": round(score, 2),
            "dimension": classify_gene_to_dimension(gene),
            "disease": classify_gene_to_disease(gene),
            "variants_found": rs_ids,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


def generate_scientific_analysis(variants: list[dict]) -> dict:
    """生成多样化的科学分析结果。"""
    key_genes = identify_key_genes(variants)

    dimension_scores = calculate_dimension_scores(variants)
    avg_score = sum(d["score"] for d in dimension_scores) / len(dimension_scores) if dimension_scores else 50

    affected = [d for d in dimension_scores if d["score"] >= 55 or d["score"] <= 45]

    high_risk = sum(1 for g in key_genes if g["risk_level"] in ("elevated", "high"))
    total = len(key_genes) if key_genes else 1
    load = "高" if high_risk / total > 0.5 else ("中" if high_risk > 0 else "低")

    return {
        "key_genes": key_genes,
        "polygenic_score": round(avg_score, 1),
        "affected_dimensions": affected,
        "genetic_load": load,
        "high_risk_gene_count": high_risk,
        "total_analyzed_genes": len(key_genes),
        "summary": _build_science_summary(key_genes, load),
    }


def _build_science_summary(key_genes: list[dict], load: str) -> str:
    """生成科学总结文本。"""
    if not key_genes:
        return "未在您的样本中识别到显著的关键基因变异。您的基因档案总体处于常见人群范围。"
    gene_str = "、".join(g["symbol"] for g in key_genes[:3])
    if load == "高":
        return (
            f"您的样本中识别到 {len(key_genes)} 个关键基因（{gene_str}）。"
            f"遗传负荷较高，建议结合专业遗传咨询解读，并通过生活方式优化管理可调节风险。"
        )
    return (
        f"您的样本中识别到 {len(key_genes)} 个关键基因（{gene_str}）。"
        "整体遗传负荷处于中等水平，多数风险可通过健康生活方式有效调节。"
    )


def _severity_of_sig(sig: str | None) -> int:
    """变异严重度排序（越小越严重）。"""
    if not sig:
        return 3
    s = sig.lower()
    if "pathogenic" in s:
        return 0
    if "uncertain" in s:
        return 1
    if "benign" in s:
        return 2
    return 3
