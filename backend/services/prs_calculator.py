"""
基因分析引擎 — 儿科遗传风险意识评估
======================================
基于 ClinVar 变异注释，生成前端所需的三种数据：

  1. geneCards        — 基因卡片列表（mockData.geneCards[]）
  2. riskDimensions   — 5 维健康风险评分（mockData.riskDimensions[]）
  3. risk_scores      — 疾病风险倍数（保留原有 PRS 能力）

健康维度（儿科 5 个维度）：
  metabolic / cardiovascular / neurodevelopmental / immunodeficiency / sensory

公式对齐前端 mockData.js 的 calculateHealthScore()。
"""
from __future__ import annotations

from math import log

# ============ 健康维度映射 ============

# 基因 → 健康维度（儿科）
DIMENSION_GENE_MAP: dict[str, set[str]] = {
    "metabolic": {"PAH", "CYP21A2", "CFTR", "DHCR7", "ACADM", "SLC2A1"},
    "cardiovascular": {"HBB", "FBN1", "MYH7", "CHD7", "G6PD"},
    "neurodevelopmental": {"SMN1", "SCN1A", "MECP2", "FMR1", "TSC1", "NF1"},
    "immunodeficiency": {"IL2RG", "BTK", "RAG1"},
    "sensory": {"GJB2", "SLC26A4", "COL1A1", "USH2A", "RB1"},
}

# 维度标签（对齐前端 riskDimensions，中英双语）
DIMENSION_LABELS: dict[str, str] = {
    "metabolic": "代谢与内分泌",
    "cardiovascular": "心血管与血液",
    "neurodevelopmental": "神经发育",
    "immunodeficiency": "免疫与感染",
    "sensory": "感官与结构",
}

# 维度基线分（前端 baseline: 50）
DIMENSION_BASELINE: dict[str, int] = {
    "metabolic": 50,
    "cardiovascular": 50,
    "neurodevelopmental": 50,
    "immunodeficiency": 50,
    "sensory": 50,
}

# 基因卡片元数据（符号 → 展示名/类别/图标）
GENE_CARD_META: dict[str, dict] = {
    "PAH": {"name": "苯丙酮尿症(PKU)", "category": "代谢与内分泌", "icon": "⚡"},
    "G6PD": {"name": "G6PD缺乏症", "category": "心血管与血液", "icon": "🩸"},
    "CYP21A2": {"name": "先天性肾上腺皮质增生(CAH)", "category": "代谢与内分泌", "icon": "⚡"},
    "SMN1": {"name": "脊髓性肌萎缩(SMA)", "category": "神经发育", "icon": "🧠"},
    "GJB2": {"name": "先天性听力损失", "category": "感官与结构", "icon": "👂"},
    "SLC26A4": {"name": "Pendred综合征/听力损失", "category": "感官与结构", "icon": "👂"},
    "CHD7": {"name": "CHARGE综合征", "category": "心血管与血液", "icon": "❤️"},
    "IL2RG": {"name": "X连锁严重联合免疫缺陷(SCID)", "category": "免疫与感染", "icon": "🛡️"},
    "BTK": {"name": "X连锁无丙种球蛋白血症(XLA)", "category": "免疫与感染", "icon": "🛡️"},
    "RAG1": {"name": "重组激活基因1缺陷(SCID)", "category": "免疫与感染", "icon": "🛡️"},
    "CFTR": {"name": "囊性纤维化(CF)", "category": "代谢与内分泌", "icon": "⚡"},
    "HBB": {"name": "镰状细胞病/地中海贫血", "category": "心血管与血液", "icon": "🩸"},
    "FBN1": {"name": "马凡综合征", "category": "心血管与血液", "icon": "❤️"},
    "MYH7": {"name": "肥厚型心肌病", "category": "心血管与血液", "icon": "❤️"},
    "SCN1A": {"name": "Dravet综合征", "category": "神经发育", "icon": "🧠"},
    "MECP2": {"name": "Rett综合征", "category": "神经发育", "icon": "🧠"},
    "FMR1": {"name": "脆性X综合征", "category": "神经发育", "icon": "🧠"},
    "TSC1": {"name": "结节性硬化症", "category": "神经发育", "icon": "🧠"},
    "NF1": {"name": "神经纤维瘤病1型", "category": "神经发育", "icon": "🧠"},
    "DHCR7": {"name": "Smith-Lemli-Opitz综合征", "category": "代谢与内分泌", "icon": "⚡"},
    "ACADM": {"name": "MCAD缺乏症", "category": "代谢与内分泌", "icon": "⚡"},
    "SLC2A1": {"name": "GLUT1缺乏症", "category": "代谢与内分泌", "icon": "⚡"},
    "COL1A1": {"name": "成骨不全症", "category": "感官与结构", "icon": "🦴"},
    "USH2A": {"name": "Usher综合征II型", "category": "感官与结构", "icon": "👁️"},
    "RB1": {"name": "视网膜母细胞瘤", "category": "感官与结构", "icon": "👁️"},
}

# 基因默认卡片（无变异时兜底 — 优先展示的核心基因）
DEFAULT_GENE_CARDS: list[str] = [
    "PAH", "G6PD", "SMN1", "GJB2", "CYP21A2", "CHD7", "IL2RG", "CFTR", "HBB"
]

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

# 疾病风险映射（儿科遗传病）
DISEASE_GENE_MAP: dict[str, set[str]] = {
    "metabolic_disorder": {"PAH", "CYP21A2", "CFTR", "DHCR7", "ACADM", "SLC2A1"},
    "cardiovascular": {"FBN1", "MYH7", "CHD7", "HBB"},
    "neurodevelopmental": {"SMN1", "SCN1A", "MECP2", "FMR1", "TSC1", "NF1"},
    "immunodeficiency": {"IL2RG", "BTK", "RAG1"},
    "hearing_loss": {"GJB2", "SLC26A4"},
    "vision_disorder": {"USH2A", "RB1"},
    "hematologic": {"HBB", "G6PD"},
    "skeletal_dysplasia": {"COL1A1", "FBN1"},
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

    维度分 = 50(基线) + Σ(变异权重 × 风险偏移 × 基因型剂量)
    """
    dim_risk: dict[str, float] = {dim: 50.0 for dim in DIMENSION_LABELS}

    for v in variants:
        dim = classify_gene_to_dimension(v.get("gene_name", ""))
        if not dim:
            continue
        weight = significance_weight(v.get("clinvar_significance"))
        odds = v.get("odds_ratio")
        dosage = v.get("allele_dosage")
        if dosage is None:
            dose_factor = 1
        elif dosage == 0:
            continue
        else:
            dose_factor = dosage

        if odds and odds > 1:
            contribution = weight * min((log(odds) / log(4)) * 15, 15)
        else:
            sig = (v.get("clinvar_significance") or "").lower()
            if "pathogenic" in sig:
                base = 6.0
            elif "uncertain" in sig or "vus" in sig:
                base = 1.5
            elif "benign" in sig:
                base = -1.0
            else:
                base = 0.5
            contribution = base
        dim_risk[dim] += contribution * dose_factor

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


# ============ 健康评分（对齐前端公式 — 婴儿成长因子版）============

def calculate_health_score(
    factors: dict[str, float] | None = None,
    genetic_baseline: int = 72,
) -> int:
    """计算 0-100 健康评分（公式对齐前端 calculateHealthScore）。

    影响因素：nutrition_type(0-10) sleep_quality(0-10)
              development_stimulation(0-10) medical_adherence(0-10)
              environmental_safety(0-10)
    """
    f = factors or {}
    nutrition = float(f.get("nutrition_type", 7))
    sleep = float(f.get("sleep_quality", 7))
    stimulation = float(f.get("development_stimulation", 6))
    adherence = float(f.get("medical_adherence", 9))
    safety = float(f.get("environmental_safety", 8))

    nutrition_impact = ((nutrition - 7) / 10) * 8
    sleep_impact = ((sleep - 7) / 10) * 8
    stimulation_impact = ((stimulation - 6) / 10) * 10
    adherence_impact = ((adherence - 9) / 10) * 12
    safety_impact = ((safety - 8) / 10) * 8

    total_deviation = (
        nutrition_impact + sleep_impact + stimulation_impact
        + adherence_impact + safety_impact
    )
    score = round(genetic_baseline + total_deviation)
    return max(35, min(98, score))


def calculate_dimension_scores_with_factors(
    variants: list[dict],
    factors: dict[str, float] | None = None,
) -> list[dict]:
    """基于遗传 + 早期成长因素的综合维度评分（对齐前端 calculateRiskDimensions）。"""
    base = calculate_dimension_scores(variants)
    f = factors or {}
    nutrition = float(f.get("nutrition_type", 7))
    sleep = float(f.get("sleep_quality", 7))
    stimulation = float(f.get("development_stimulation", 6))
    adherence = float(f.get("medical_adherence", 9))
    safety = float(f.get("environmental_safety", 8))

    adjustments = {
        "metabolic": -(nutrition - 7) * 3 - (adherence - 9) * 2,
        "cardiovascular": -(adherence - 9) * 3 - (safety - 8) * 2,
        "neurodevelopmental": -(stimulation - 6) * 3 - (sleep - 7) * 2 - (nutrition - 7) * 1.5,
        "immunodeficiency": -(adherence - 9) * 3 - (safety - 8) * 2.5 - (nutrition - 7) * 1.5,
        "sensory": -(stimulation - 6) * 2 - (adherence - 9) * 2 - (safety - 8) * 1.5,
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


def generate_gene_cards(variants: list[dict], top_n: int = 9) -> list[dict]:
    """从变异生成前端 geneCards 结构。"""
    gene_info: dict[str, list[dict]] = {}
    for v in variants:
        gene = _normalize_gene(v.get("gene_name", ""))
        if not gene:
            continue
        if gene not in gene_info:
            gene_info[gene] = []
        gene_info[gene].append(v)

    display_genes = [g for g in DEFAULT_GENE_CARDS if g in gene_info]
    display_genes += [g for g in gene_info if g not in DEFAULT_GENE_CARDS]
    display_genes = display_genes[:top_n]

    if not display_genes:
        display_genes = DEFAULT_GENE_CARDS[:top_n]

    cards = []
    for gene in display_genes:
        variants_of_gene = gene_info.get(gene, [])
        meta = GENE_CARD_META.get(gene, {
            "name": f"{gene} 基因", "category": "遗传分析", "icon": "🧬"
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
        return (
            f"宝宝的 {gene} 基因存在临床显著变异，"
            "建议遵循新生儿筛查随访和专科医生指导进行管理。"
        )
    if sig and sig.lower().startswith("benign"):
        return f"宝宝的 {gene} 基因未发现显著致病变异，遗传风险处于正常水平。"
    return (
        f"{gene} 基因与婴幼儿健康发育密切相关，"
        "早期干预和定期监测可有效调节遗传风险。"
    )


def _build_interpretation(gene: str, sig: str | None, odds: float | None) -> str:
    """生成基因卡片解读（儿科语境）。"""
    science = _get_gene_science(gene)
    base = science.get("function", f"{gene} 基因影响婴幼儿健康发育。")
    if odds and odds > 1:
        return (
            f"{base} 该基因变异效应量约为 {odds:.1f} 倍。"
            "早期干预（喂养、医疗随访、发育支持）可显著改善预后，"
            "父母的日常照护对孩子的发育轨迹具有深远影响。"
        )
    return (
        f"{base} 基因只是影响因素之一，"
        "积极的早期干预和定期健康监测可大幅改善孩子的发育轨迹。"
    )


def _build_recommendations(gene: str) -> list[str]:
    """基于基因生成儿科建议。"""
    dim = classify_gene_to_dimension(gene)
    if dim == "metabolic":
        return [
            "严格遵循新生儿筛查随访和专科医生饮食指导",
            "记录喂养情况和生长发育曲线",
            "定期监测相关代谢指标",
        ]
    if dim == "cardiovascular":
        return [
            "定期进行心脏专科评估和影像学检查",
            "遵医嘱进行预防性用药和活动管理",
            "关注喂养耐受性和生长发育情况",
        ]
    if dim == "neurodevelopmental":
        return [
            "尽早开始早期干预和康复训练",
            "定期进行发育评估和里程碑监测",
            "与儿科神经专科医生保持定期随访",
        ]
    if dim == "immunodeficiency":
        return [
            "严格遵循感染预防措施和免疫球蛋白替代治疗",
            "按时完成疫苗接种计划（遵医嘱调整）",
            "出现发热或感染迹象立即就医",
        ]
    if dim == "sensory":
        return [
            "定期进行听力和视力筛查评估",
            "根据筛查结果尽早适配辅助设备",
            "配合早期言语/视觉康复训练",
        ]
    return [
        "定期儿科随访和生长发育监测",
        "关注宝宝的喂养、睡眠和发育里程碑",
    ]


# ============ 建议引擎（儿科版）============

def generate_recommendations(factors: dict[str, float] | None = None) -> list[dict]:
    """生成个性化育儿建议（对齐前端 generateRecommendations 输出结构）。"""
    f = factors or {}
    nutrition = float(f.get("nutrition_type", 7))
    sleep = float(f.get("sleep_quality", 7))
    stimulation = float(f.get("development_stimulation", 6))
    adherence = float(f.get("medical_adherence", 9))
    safety = float(f.get("environmental_safety", 8))

    recs: list[dict] = []

    if nutrition < 8:
        recs.append({
            "id": "n1", "pillar": "nutrition", "icon": "🍼",
            "title": "优化喂养方式",
            "description": "母乳喂养为宝宝提供最佳营养和免疫保护。如因特殊情况无法纯母乳，请咨询医生选择最适合的配方方案。",
            "difficulty": "moderate", "impact": 5, "time": "立即开始",
        })
    if sleep < 8:
        recs.append({
            "id": "sl1", "pillar": "sleep", "icon": "😴",
            "title": "建立规律睡眠习惯",
            "description": "婴儿睡眠直接影响大脑发育和生长激素分泌。建立固定的睡前程序，确保安全的睡眠环境。",
            "difficulty": "moderate", "impact": 4, "time": "今晚开始",
        })
    if stimulation < 7:
        recs.append({
            "id": "ds1", "pillar": "development", "icon": "🎯",
            "title": "增加早期感官刺激",
            "description": "互动游戏、语言暴露和适龄感官刺激对宝宝神经发育至关重要，尤其对有神经发育风险基因的宝宝。",
            "difficulty": "easy", "impact": 5, "time": "每天进行",
        })
    if adherence < 9:
        recs.append({
            "id": "ma1", "pillar": "medical", "icon": "🏥",
            "title": "加强医疗随访依从性",
            "description": "新生儿筛查异常结果的随访、专科预约和按时用药直接决定宝宝的预后。请确保不遗漏关键随访。",
            "difficulty": "moderate", "impact": 5, "time": "本周内",
        })
    if safety < 8:
        recs.append({
            "id": "es1", "pillar": "safety", "icon": "🏠",
            "title": "改善家居环境安全",
            "description": "避免毒素暴露、确保安全睡眠环境(SIDS预防)、做好感染防护，为宝宝提供安全的成长空间。",
            "difficulty": "easy", "impact": 4, "time": "立即开始",
        })
    if adherence >= 9 and nutrition >= 8:
        recs.append({
            "id": "g1", "pillar": "general", "icon": "🎯",
            "title": "您在为宝宝打下坚实的健康基础",
            "description": "坚持科学的喂养和照护方案，定期儿科随访。持续的优质照护是改变基因表达的关键。",
            "difficulty": "easy", "impact": 2, "time": "持续进行",
        })

    return recs


# ============ 30 天计划（儿科版）============

def generate_thirty_day_plan(goal: str | None = None) -> dict:
    """生成 30 天新生儿照护计划（对齐前端 thirtyDayPlan 结构）。"""
    return {
        "goal": goal or "建立科学的婴儿照护方案，优化早期发育轨迹",
        "weeks": [
            {
                "label": "第 1 周 — 基础建立",
                "theme": "记录与觉察",
                "tasks": [
                    {"day": "第 1-2 天", "title": "建立喂养日记", "desc": "记录每次喂养时间、时长和方式，了解宝宝的喂养规律。"},
                    {"day": "第 3-4 天", "title": "建立睡眠日志", "desc": "记录宝宝睡眠时间和质量，观察睡眠模式。"},
                    {"day": "第 5-7 天", "title": "整理医疗档案", "desc": "汇总新生儿筛查报告、疫苗接种记录和专科预约时间表。"},
                ],
            },
            {
                "label": "第 2 周 — 激活",
                "theme": "小改变，大影响",
                "tasks": [
                    {"day": "第 8-9 天", "title": "建立睡前程序", "desc": "固定的洗澡→喂养→安抚→入睡流程，帮助宝宝建立昼夜节律。"},
                    {"day": "第 10-12 天", "title": "每日亲子互动时间", "desc": "每天至少 15 分钟专注的亲子互动——说话、唱歌、眼神交流。"},
                    {"day": "第 13-14 天", "title": "完成一次专科随访", "desc": "确认所有新生儿筛查随访预约已安排并按时就诊。"},
                ],
            },
            {
                "label": "第 3 周 — 整合",
                "theme": "建立节奏",
                "tasks": [
                    {"day": "第 15-17 天", "title": "环境安全检查", "desc": "检查家居安全隐患——睡眠环境、过敏原、清洁用品存放。"},
                    {"day": "第 18-19 天", "title": "感官刺激活动", "desc": "引入适龄的黑白卡、摇铃和触觉玩具，丰富感官体验。"},
                    {"day": "第 20-21 天", "title": "学习婴儿发育里程碑", "desc": "了解接下来 1-3 个月的发育里程碑，知道何时该关注。"},
                ],
            },
            {
                "label": "第 4 周 — 维持",
                "theme": "终身习惯",
                "tasks": [
                    {"day": "第 22-24 天", "title": "回顾与反思", "desc": "对比第 1 天的记录，观察宝宝的发育趋势和规律变化。"},
                    {"day": "第 25-27 天", "title": "与儿科医生沟通", "desc": "整理问题和观察，准备下一次儿科随访的讨论要点。"},
                    {"day": "第 28-30 天", "title": "规划下一个月", "desc": "设定新的照护目标。宝宝的健康发展是一场持续的旅程。"},
                ],
            },
        ],
    }


# ============ 兼容辅助 ============

def calculate_prs(variants: list[dict], disease: str | None = None) -> dict:
    """计算疾病多基因风险评分（保留原 PRS 能力）。"""
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
    """为单个变异生成 0-1 风险评分。"""
    weight = significance_weight(clinvar_sig)
    if odds_ratio and odds_ratio > 1:
        return round(min(weight * (log(odds_ratio) / log(4)) + weight * 0.2, 0.99), 2)
    return round(weight, 2)


# =============================================================================
# 关键基因智能抓取 + 科学分析（儿科版）
# =============================================================================

_GENE_SCIENCE: dict[str, dict] = {
    "PAH": {
        "name": "Phenylalanine Hydroxylase",
        "cn_name": "苯丙氨酸羟化酶",
        "function": "编码苯丙氨酸羟化酶。致病性变异导致苯丙酮尿症(PKU)——一种可通过饮食控制的可治疗先天性代谢缺陷。未经治疗的PKU导致严重智力障碍。",
        "evidence": "high",
        "variants": ["rs62514927"],
        "population_impact": "PKU 发病率约 1/10,000-1/15,000（全球），中国约 1/11,000",
        "lifestyle": "严格苯丙氨酸限制饮食可完全预防神经系统损伤。新生儿筛查+早期饮食干预是关键。",
    },
    "G6PD": {
        "name": "Glucose-6-Phosphate Dehydrogenase",
        "cn_name": "葡萄糖-6-磷酸脱氢酶",
        "function": "编码G6PD酶，保护红细胞免受氧化损伤。致病性变异导致G6PD缺乏症——全球最常见的遗传性酶缺乏症，接触氧化性触发因素可诱发急性溶血。",
        "evidence": "high",
        "variants": ["rs1050828", "rs1050829"],
        "population_impact": "全球约 4 亿人携带G6PD缺乏变异，中国南方发病率较高",
        "lifestyle": "避免蚕豆、特定药物(如磺胺类、阿司匹林)和樟脑丸等氧化性触发因素，可完全预防溶血发作。",
    },
    "CYP21A2": {
        "name": "Cytochrome P450 21A2",
        "cn_name": "21-羟化酶",
        "function": "编码21-羟化酶，参与皮质醇和醛固酮合成。致病性变异导致先天性肾上腺皮质增生症(CAH)——盐耗型危象可危及生命。",
        "evidence": "high",
        "variants": [],
        "population_impact": "CAH 经典型发病率约 1/15,000，中国约 1/16,000",
        "lifestyle": "激素替代治疗+应激剂量调整是管理核心。新生儿筛查可早期发现并预防危象。",
    },
    "SMN1": {
        "name": "Survival Motor Neuron 1",
        "cn_name": "运动神经元存活蛋白1",
        "function": "编码SMN蛋白，对运动神经元存活至关重要。纯合缺失/致病变异导致脊髓性肌萎缩(SMA)——婴幼儿最常见的致死性神经肌肉疾病。",
        "evidence": "high",
        "variants": [],
        "population_impact": "SMA 发病率约 1/6,000-1/10,000，携带率约 1/40-1/50",
        "lifestyle": "新生儿筛查+症状前治疗(基因治疗/药物)可显著改变病程。治疗时机至关重要。",
    },
    "GJB2": {
        "name": "Gap Junction Beta 2 (Connexin 26)",
        "cn_name": "缝隙连接蛋白β2",
        "function": "编码连接蛋白26(Cx26)，对内耳钾离子循环至关重要。致病性变异是遗传性先天性听力损失最常见的原因。",
        "evidence": "high",
        "variants": ["rs80338939"],
        "population_impact": "GJB2 变异占遗传性听力损失的约 50%，中国人群携带率较高",
        "lifestyle": "新生儿听力筛查+早期助听器/人工耳蜗(<12月龄)+语言康复可使语言发育接近正常。",
    },
    "SLC26A4": {
        "name": "Solute Carrier Family 26 Member 4",
        "cn_name": "溶质载体家族26成员4",
        "function": "编码pendrin蛋白，参与内耳离子平衡和甲状腺碘转运。致病性变异导致Pendred综合征——先天性听力损失伴甲状腺肿。",
        "evidence": "high",
        "variants": [],
        "population_impact": "SLC26A4 变异是中国人群遗传性听力损失的第二大常见原因",
        "lifestyle": "避免头部外伤(可加速听力下降)，早期听力干预和甲状腺功能监测。",
    },
    "CHD7": {
        "name": "Chromodomain Helicase DNA Binding Protein 7",
        "cn_name": "染色质解旋酶DNA结合蛋白7",
        "function": "编码染色质重塑因子。致病性变异导致CHARGE综合征——涉及眼、心脏、鼻腔、发育、生殖器和耳部异常的多系统先天性疾病。",
        "evidence": "high",
        "variants": [],
        "population_impact": "CHARGE 综合征发病率约 1/8,500-1/10,000",
        "lifestyle": "多学科综合管理(心脏科、耳鼻喉科、眼科、发育儿科)至关重要。",
    },
    "IL2RG": {
        "name": "Interleukin 2 Receptor Gamma",
        "cn_name": "白细胞介素-2受体γ链",
        "function": "编码IL-2受体共同γ链，对淋巴细胞发育至关重要。致病性变异导致X连锁严重联合免疫缺陷(SCID-X1)——缺乏功能性T细胞和NK细胞。",
        "evidence": "high",
        "variants": [],
        "population_impact": "SCID-X1 是最常见的SCID类型，占所有SCID的约 45%",
        "lifestyle": "TREC新生儿筛查+早期造血干细胞移植/基因治疗可挽救生命。治疗前严格感染防护。",
    },
    "BTK": {
        "name": "Bruton Tyrosine Kinase",
        "cn_name": "Bruton酪氨酸激酶",
        "function": "编码B细胞发育必需的酪氨酸激酶。致病性变异导致X连锁无丙种球蛋白血症(XLA)——B细胞缺乏，抗体生成障碍，反复细菌感染。",
        "evidence": "high",
        "variants": [],
        "population_impact": "XLA 发病率约 1/200,000（男性）",
        "lifestyle": "定期免疫球蛋白替代治疗(IVIG/SCIG)可维持正常生长发育和预防感染。",
    },
    "RAG1": {
        "name": "Recombination Activating Gene 1",
        "cn_name": "重组激活基因1",
        "function": "编码V(D)J重组关键酶。致病性变异导致多种形式的SCID或Omenn综合征——T/B细胞严重缺乏。",
        "evidence": "high",
        "variants": [],
        "population_impact": "RAG1/2 缺陷约占所有SCID的 20-30%",
        "lifestyle": "新生儿TREC筛查+早期造血干细胞移植是当前标准治疗。",
    },
    "CFTR": {
        "name": "Cystic Fibrosis Transmembrane Conductance Regulator",
        "cn_name": "囊性纤维化跨膜传导调节因子",
        "function": "编码氯离子通道蛋白。致病性变异导致囊性纤维化(CF)——影响呼吸和消化系统的多系统疾病。CFTR调节剂是变异特异性靶向治疗。",
        "evidence": "high",
        "variants": ["rs113993960"],
        "population_impact": "CF 在白人中发病率约 1/2,500-3,500，亚洲人群较为罕见",
        "lifestyle": "早期营养支持、呼吸道清理、CFTR调节剂治疗和感染预防的多学科管理。",
    },
    "HBB": {
        "name": "Hemoglobin Subunit Beta",
        "cn_name": "β-珠蛋白",
        "function": "编码β-珠蛋白链。致病性变异导致镰状细胞病和β-地中海贫血——全球最常见的严重单基因遗传病。新生儿筛查可显著降低死亡率。",
        "evidence": "high",
        "variants": ["rs334"],
        "population_impact": "镰状细胞病在非洲裔人群中发病率约 1/365；地中海贫血在地中海、中东和东南亚高发",
        "lifestyle": "预防性抗生素、疫苗接种、羟基脲治疗和定期专科随访。",
    },
    "FBN1": {
        "name": "Fibrillin-1",
        "cn_name": "原纤蛋白-1",
        "function": "编码细胞外基质蛋白。致病性变异导致马凡综合征——以主动脉根部扩张、晶状体脱位和骨骼特征为主要表现的结缔组织疾病。",
        "evidence": "high",
        "variants": [],
        "population_impact": "马凡综合征发病率约 1/5,000-1/10,000",
        "lifestyle": "定期心脏影像监测、预防性β受体阻滞剂/ARB治疗、避免高强度对抗性运动。",
    },
    "MYH7": {
        "name": "Myosin Heavy Chain 7",
        "cn_name": "β-肌球蛋白重链",
        "function": "编码心肌肌球蛋白重链。致病性变异是家族性肥厚型心肌病最常见的遗传原因，可在婴儿期表现为心衰。",
        "evidence": "high",
        "variants": [],
        "population_impact": "肥厚型心肌病发病率约 1/500，MYH7 变异占家族性病例的约 30-40%",
        "lifestyle": "定期心脏评估、避免竞技性运动和脱水、遵医嘱进行风险分层管理。",
    },
    "SCN1A": {
        "name": "Sodium Voltage-Gated Channel Alpha Subunit 1",
        "cn_name": "电压门控钠通道α1亚基",
        "function": "编码脑钠通道Nav1.1。致病性变异导致Dravet综合征——婴儿期起病的药物难治性癫痫，常伴发热敏感和发育倒退。",
        "evidence": "high",
        "variants": [],
        "population_impact": "Dravet 综合征发病率约 1/15,700-1/40,000",
        "lifestyle": "避免过热和钠通道阻滞剂类抗癫痫药物。发热管理和睡眠充足可降低发作风险。",
    },
    "MECP2": {
        "name": "Methyl-CpG Binding Protein 2",
        "cn_name": "甲基CpG结合蛋白2",
        "function": "编码转录调控因子。致病性变异导致Rett综合征——6-18月龄出现发育倒退、手部刻板动作和语言丧失的严重神经发育障碍。",
        "evidence": "high",
        "variants": [],
        "population_impact": "Rett 综合征发病率约 1/10,000-1/15,000（女性）",
        "lifestyle": "早期康复干预(物理治疗、沟通辅助、手部功能训练)可改善功能预后。",
    },
    "FMR1": {
        "name": "Fragile X Mental Retardation 1",
        "cn_name": "脆性X智力低下蛋白",
        "function": "编码FMRP蛋白，调控突触蛋白合成。CGG重复扩增(>200)导致脆性X综合征——最常见的遗传性智力障碍。",
        "evidence": "high",
        "variants": [],
        "population_impact": "脆性X综合征发病率约 1/4,000(男性)和 1/8,000(女性)，前突变携带率约 1/250-1/800",
        "lifestyle": "早期行为干预、言语治疗、特殊教育和感觉统合训练的早期综合干预。",
    },
    "TSC1": {
        "name": "TSC Complex Subunit 1",
        "cn_name": "结节性硬化症蛋白1",
        "function": "编码hamartin蛋白，负调控mTOR信号通路。致病性变异导致结节性硬化症——多系统错构瘤疾病，影响大脑、皮肤、肾脏和心脏。",
        "evidence": "high",
        "variants": [],
        "population_impact": "结节性硬化症发病率约 1/6,000-1/10,000",
        "lifestyle": "婴儿痉挛的早期识别和治疗、mTOR抑制剂靶向治疗、定期多系统监测。",
    },
    "NF1": {
        "name": "Neurofibromin 1",
        "cn_name": "神经纤维瘤蛋白",
        "function": "编码Ras-GAP蛋白，负调控Ras信号通路。致病性变异导致神经纤维瘤病1型——咖啡牛奶斑、神经纤维瘤和视路胶质瘤。",
        "evidence": "high",
        "variants": [],
        "population_impact": "NF1 发病率约 1/2,500-1/3,000，是最常见的常染色体显性遗传肿瘤易感综合征之一",
        "lifestyle": "定期肿瘤筛查(视路胶质瘤、神经纤维瘤)、学习支持和早期干预。",
    },
    "DHCR7": {
        "name": "7-Dehydrocholesterol Reductase",
        "cn_name": "7-脱氢胆固醇还原酶",
        "function": "编码胆固醇合成关键酶。致病性变异导致Smith-Lemli-Opitz综合征——以发育迟缓、小头畸形和多发畸形为特征的胆固醇合成障碍。",
        "evidence": "high",
        "variants": [],
        "population_impact": "SLOS 发病率约 1/20,000-1/60,000",
        "lifestyle": "胆固醇补充治疗可改善部分症状。发育支持和多学科管理。",
    },
    "ACADM": {
        "name": "Acyl-CoA Dehydrogenase Medium Chain",
        "cn_name": "中链酰基辅酶A脱氢酶",
        "function": "编码脂肪酸β-氧化关键酶。致病性变异导致MCAD缺乏症——空腹可诱发低血糖和代谢危象的脂肪酸氧化障碍。新生儿筛查+喂养指导几乎消除了相关死亡率。",
        "evidence": "high",
        "variants": ["rs77931234"],
        "population_impact": "MCAD 缺乏症发病率约 1/10,000-1/20,000，北欧裔中更高",
        "lifestyle": "规律喂养、避免长时间空腹。疾病期间需特别关注能量摄入。",
    },
    "SLC2A1": {
        "name": "Solute Carrier Family 2 Member 1 (GLUT1)",
        "cn_name": "葡萄糖转运蛋白1",
        "function": "编码GLUT1葡萄糖转运蛋白，介导葡萄糖跨越血脑屏障。致病性变异导致GLUT1缺乏症——早发性癫痫和发育迟缓。",
        "evidence": "high",
        "variants": [],
        "population_impact": "GLUT1 缺乏症发病率约 1/90,000",
        "lifestyle": "生酮饮食是有效的治疗策略——通过提供酮体绕过葡萄糖转运缺陷为大脑供能。",
    },
    "COL1A1": {
        "name": "Collagen Type I Alpha 1 Chain",
        "cn_name": "I型胶原α1链",
        "function": "编码I型胶原主要成分。致病性变异导致成骨不全症(OI)——以骨骼脆弱、反复骨折、蓝巩膜和听力损失为特征。",
        "evidence": "high",
        "variants": [],
        "population_impact": "成骨不全症发病率约 1/15,000-1/20,000",
        "lifestyle": "物理治疗增强肌力、安全环境改造防跌倒、双膦酸盐治疗和多学科管理。",
    },
    "USH2A": {
        "name": "Usherin",
        "cn_name": "Usherin蛋白",
        "function": "编码usherin蛋白，对耳蜗和内耳毛细胞以及视网膜光感受器细胞的结构完整性至关重要。致病性变异导致Usher综合征II型——先天性听力损失伴视网膜色素变性。",
        "evidence": "high",
        "variants": [],
        "population_impact": "Usher综合征发病率约 1/6,000-1/25,000，II型最常见",
        "lifestyle": "早期人工耳蜗植入+定期眼科随访+低视力辅助和定向行走训练。",
    },
    "RB1": {
        "name": "Retinoblastoma 1",
        "cn_name": "视网膜母细胞瘤蛋白",
        "function": "编码pRb肿瘤抑制蛋白，调控细胞周期。致病性变异导致视网膜母细胞瘤——婴幼儿最常见的眼内恶性肿瘤，可危及视力和生命。",
        "evidence": "high",
        "variants": [],
        "population_impact": "视网膜母细胞瘤发病率约 1/15,000-1/20,000 活产儿",
        "lifestyle": "从出生开始的定期眼底筛查+早期治疗可挽救视力并实现>95%的生存率。",
    },
}

_EVIDENCE_WEIGHT = {"high": 1.0, "moderate": 0.7, "low": 0.4}


def _get_gene_science(gene: str) -> dict:
    """获取基因科学信息（兜底用通用信息）。"""
    if gene in _GENE_SCIENCE:
        return _GENE_SCIENCE[gene]
    dim = classify_gene_to_dimension(gene)
    return {
        "name": f"{gene}",
        "cn_name": f"{gene} 基因",
        "function": f"{gene} 基因参与婴幼儿健康发育调控。具体机制因变异位点而异，建议结合 ClinVar 注释和儿科医生指导解读。",
        "evidence": "moderate",
        "variants": [],
        "population_impact": "人群频率因人群和地区而异",
        "lifestyle": "科学的早期照护和定期儿科随访可部分调节遗传风险",
    }


def identify_key_genes(
    variants: list[dict],
    top_n: int = 6,
    min_score: float = 1.0,
    population: str | None = None,
) -> list[dict]:
    """从用户样本中智能抓取关键基因（儿科版）。"""
    _POP_FREQ: dict[str, dict[str, float]] = {
        "rs62514927": {"EAS": 0.02, "EUR": 0.01, "AFR": 0.01, "SAS": 0.01, "LAT": 0.01},
        "rs1050828": {"EAS": 0.05, "EUR": 0.01, "AFR": 0.20, "SAS": 0.03, "LAT": 0.05},
        "rs1050829": {"EAS": 0.03, "EUR": 0.01, "AFR": 0.15, "SAS": 0.02, "LAT": 0.03},
        "rs113993960": {"EAS": 0.01, "EUR": 0.02, "AFR": 0.01, "SAS": 0.01, "LAT": 0.01},
        "rs334": {"EAS": 0.01, "EUR": 0.01, "AFR": 0.10, "SAS": 0.02, "LAT": 0.03},
        "rs80338939": {"EAS": 0.05, "EUR": 0.02, "AFR": 0.03, "SAS": 0.04, "LAT": 0.03},
        "rs77931234": {"EAS": 0.01, "EUR": 0.02, "AFR": 0.01, "SAS": 0.01, "LAT": 0.01},
    }
    _pop_code = None
    if population:
        _pop_map = {
            "东亚": "EAS", "欧洲": "EUR", "非洲": "AFR", "南亚": "SAS", "拉丁": "LAT",
            "east_asian": "EAS", "european": "EUR", "african": "AFR",
            "south_asian": "SAS", "latino": "LAT",
            "EAS": "EAS", "EUR": "EUR", "AFR": "AFR", "SAS": "SAS", "LAT": "LAT",
        }
        _pop_code = _pop_map.get(str(population))

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

        population_factor = 1.0
        population_rarity_note = ""
        if _pop_code:
            freqs = []
            for v in gene_variants:
                rs = v.get("rs_id")
                if rs and rs in _POP_FREQ and _pop_code in _POP_FREQ[rs]:
                    freqs.append(_POP_FREQ[rs][_pop_code])
            if freqs:
                avg_freq = sum(freqs) / len(freqs)
                population_factor = round(1.0 + max(0.0, (0.5 - avg_freq)) * 1.0, 3)
                population_rarity_note = (
                    f"该基因的变异等位基因在{_pop_code}人群中的平均频率约 "
                    f"{avg_freq*100:.0f}%（{'较常见' if avg_freq >= 0.3 else '较稀有'}），"
                    f"{'值得关注' if avg_freq < 0.3 else '属常见变异'}"
                )

        dosage_factor = 1.0
        max_dosage = max((v.get("allele_dosage") or 0) for v in gene_variants) if gene_variants else 0
        if max_dosage >= 2:
            dosage_factor = 1.6
        elif max_dosage == 1:
            dosage_factor = 1.2

        score = (severity_score + 1) * evidence_w * importance * population_factor * dosage_factor

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
            "population_factor": population_factor,
            "dosage_factor": dosage_factor,
            "max_allele_dosage": max_dosage,
            "population_note": population_rarity_note,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


def generate_scientific_analysis(
    variants: list[dict],
    population: str | None = None,
) -> dict:
    """生成多样化的科学分析结果（儿科版）。"""
    key_genes = identify_key_genes(variants, population=population)

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
    """生成科学总结文本（儿科版）。"""
    if not key_genes:
        return (
            "未在宝宝的样本中识别到显著的关键基因变异。"
            "宝宝的基因档案总体处于常见人群范围。"
        )
    gene_str = "、".join(g["symbol"] for g in key_genes[:3])
    if load == "高":
        return (
            f"宝宝的样本中识别到 {len(key_genes)} 个关键基因（{gene_str}）。"
            f"遗传负荷较高，强烈建议结合专业遗传咨询解读，"
            "并通过早期干预和定期随访管理可调节风险。"
        )
    return (
        f"宝宝的样本中识别到 {len(key_genes)} 个关键基因（{gene_str}）。"
        "整体遗传负荷处于中等水平，通过科学的早期照护可有效调节发育轨迹。"
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
