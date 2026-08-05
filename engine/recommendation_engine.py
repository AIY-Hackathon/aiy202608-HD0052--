# =============================================================================
# engine/recommendation_engine.py — 儿科个性化早期照护推荐引擎
# =============================================================================
#
# 每条建议包含：
#   - title:             简短标题
#   - description:       建议描述
#   - trigger_factor:    触发该建议的环境因素
#   - why_for_this_user: 为什么该建议适用于该宝宝
#   - evidence_level:    证据等级（strong/moderate/preliminary）
#   - related_gene:      相关基因列表
#   - difficulty:        实施难度
#   - impact:            影响预估（1-5）
#   - time:              预估时间
#
# 目标用户：新生儿父母/监护人
# =============================================================================
from __future__ import annotations

from typing import Any

from engine.config import (
    DIMENSION_CONFIG,
    ENVIRONMENT_RANGES,
    ENVIRONMENT_WEIGHTS,
    GENE_WEIGHTS,
    INTERACTION_COEFFICIENTS,
)


# =============================================================================
# 1. 建议模板库 — 儿科早期干预
# =============================================================================

RECOMMENDATION_TEMPLATES: list[dict[str, Any]] = [
    # ── 代谢与内分泌 ──
    {
        "id": "met_feeding",
        "pillar": "nutrition",
        "dimension": "metabolic",
        "title": "优化喂养方案以支持代谢健康",
        "description": (
            "对于携带代谢相关基因变异（如PAH、ACADM、G6PD）的宝宝，"
            "科学的喂养方案是最核心的早期干预措施。母乳喂养提供最佳营养和免疫保护；"
            "特定代谢疾病需遵医嘱使用特殊配方奶粉。"
        ),
        "trigger_factor": "nutrition_type",
        "trigger_condition": "below_optimal",
        "why_template": (
            "喂养方式是当前影响宝宝代谢发育轨迹最重要的可改变因素。"
            "您的宝宝携带 {genes} 基因变异，科学的喂养管理可直接改善发育预后。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "每日持续",
        "evidence_level": "strong",
        "reference": "WHO/UNICEF 母乳喂养指南 | 新生儿筛查管理共识",
    },
    {
        "id": "met_adherence",
        "pillar": "medical",
        "dimension": "metabolic",
        "title": "严格遵循新生儿筛查随访和专科管理",
        "description": (
            "新生儿筛查异常结果的及时随访是改变代谢遗传病预后的关键窗口期。"
            "对于PKU、MCAD缺乏症、CAH等可治疗的先天性代谢缺陷，"
            "早期诊断和规范治疗的依从性直接决定宝宝的神经系统发育和长期健康。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "医疗依从性是代谢遗传病管理中最重要的环境调节因素。"
            "宝宝携带 {genes} 变异，按时完成随访和规范治疗可显著改善发育轨迹。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "按专科预约频率",
        "evidence_level": "strong",
        "reference": "新生儿筛查随访指南 | PKU/CAH/MCAD 管理共识",
    },
    {
        "id": "met_safety",
        "pillar": "safety",
        "dimension": "metabolic",
        "title": "避免代谢触发因素（特定食物/药物/空腹）",
        "description": (
            "G6PD缺乏症宝宝需严格避免氧化性触发因素（蚕豆、磺胺类药物、樟脑丸等）；"
            "MCAD缺乏症宝宝需避免长时间空腹，疾病期间需特别关注能量摄入。"
            "了解并记录宝宝的特定触发因素是预防急性事件的第一道防线。"
        ),
        "trigger_factor": "environmental_safety",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，特定的环境/饮食触发因素可能诱发急性代谢危象。"
            "建立完整的触发因素清单并告知所有照护者是关键的预防措施。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "持续管理",
        "evidence_level": "strong",
        "reference": "G6PD缺乏症管理指南 | MCAD缺乏症紧急处理方案",
    },

    # ── 心血管与血液 ──
    {
        "id": "cv_monitoring",
        "pillar": "medical",
        "dimension": "cardiovascular",
        "title": "建立定期心脏专科评估计划",
        "description": (
            "对于携带心肌病/结缔组织病相关基因变异（MYH7、FBN1、CHD7）的宝宝，"
            "定期心脏影像学评估（超声心动图）和专科随访是标准管理方案。"
            "早期发现主动脉扩张或心肌肥厚可及时启动保护性治疗。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 基因变异，定期的结构性心脏评估"
            "对早期发现和干预至关重要。预防性管理可显著改善长期预后。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "每 6-12 个月",
        "evidence_level": "strong",
        "reference": "AHA/ACC 心肌病指南 | 马凡综合征管理共识",
    },
    {
        "id": "cv_prophylaxis",
        "pillar": "medical",
        "dimension": "cardiovascular",
        "title": "预防性抗生素和疫苗接种（血液病管理）",
        "description": (
            "对于携带HBB基因变异（镰状细胞病/地中海贫血）的宝宝，"
            "预防性抗生素、按时完成疫苗接种和定期血液科随访"
            "是降低感染风险和改善预后的核心措施。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，感染预防是降低并发症风险的关键。"
            "规范的预防性用药和疫苗接种计划可显著降低严重感染的发生率。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "按免疫计划和随访频率",
        "evidence_level": "strong",
        "reference": "镰状细胞病管理指南 | WHO 免疫接种建议",
    },

    # ── 神经发育 ──
    {
        "id": "nd_early_intervention",
        "pillar": "development",
        "dimension": "neurodevelopmental",
        "title": "尽早启动早期干预和康复训练",
        "description": (
            "对于携带神经发育相关基因变异（SMN1、FMR1、MECP2、SCN1A等）的宝宝，"
            "早期干预的时间窗口至关重要。物理治疗、作业治疗、言语治疗和"
            "发育支持的早期启动可显著改善功能预后。SMN1的基因治疗/药物治疗"
            "在症状前阶段启动效果最佳。"
        ),
        "trigger_factor": "development_stimulation",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 基因变异，早期干预是改变发育轨迹"
            "最有力的环境因素。研究表明早期启动康复训练可获得更好的功能预后。"
        ),
        "difficulty": "hard",
        "impact": 5,
        "time": "尽早开始，持续进行",
        "evidence_level": "strong",
        "reference": "SMA 治疗指南 | 早期干预效果研究 | 神经发育障碍管理共识",
    },
    {
        "id": "nd_stimulation",
        "pillar": "development",
        "dimension": "neurodevelopmental",
        "title": "丰富的早期感官刺激和互动游戏",
        "description": (
            "每天定时的亲子互动、语言暴露、适龄感官刺激（黑白卡、摇铃、触觉玩具）"
            "对宝宝的神经发育至关重要。对于携带FMR1、MECP2、NF1等基因变异的宝宝，"
            "丰富的环境刺激和早期教育支持是改善发育轨迹的核心环境因素。"
        ),
        "trigger_factor": "development_stimulation",
        "trigger_condition": "below_optimal",
        "why_template": (
            "早期刺激是当前影响宝宝神经发育轨迹的可改变因素。"
            "宝宝的 {genes} 基因档案提示环境富集对发育有重要促进作用。"
        ),
        "difficulty": "easy",
        "impact": 5,
        "time": "每日 15-30 分钟",
        "evidence_level": "strong",
        "reference": "早期干预效果研究 | Heckman 人力资本投资理论",
    },
    {
        "id": "nd_sleep",
        "pillar": "sleep",
        "dimension": "neurodevelopmental",
        "title": "建立规律睡眠习惯支持大脑发育",
        "description": (
            "婴儿睡眠直接影响大脑发育、突触可塑性和生长激素分泌。"
            "建立固定的睡前程序（洗澡→喂养→安抚→入睡）和规律的作息时间。"
            "对于SCN1A变异携带者，充足睡眠可降低癫痫发作阈值。"
        ),
        "trigger_factor": "sleep_quality",
        "trigger_condition": "below_optimal",
        "why_template": (
            "睡眠质量是当前影响宝宝神经发育轨迹的重要因素。"
            "宝宝携带 {genes} 变异，充足的规律睡眠对大脑发育和发作阈值管理尤为重要。"
        ),
        "difficulty": "moderate",
        "impact": 4,
        "time": "每晚建立固定程序",
        "evidence_level": "strong",
        "reference": "婴幼儿睡眠研究 | Dravet综合征管理指南",
    },

    # ── 免疫与感染 ──
    {
        "id": "imm_protection",
        "pillar": "safety",
        "dimension": "immunodeficiency",
        "title": "严格感染防护和早期就医意识",
        "description": (
            "对于携带原发性免疫缺陷相关基因变异（IL2RG、BTK、RAG1）的宝宝，"
            "严格的环境感染防护是移植/治疗前的关键措施。包括：限制访客、"
            "手部卫生、避免人群密集场所、出现发热立即就医。"
            "SCID患儿在HSCT前必须进行保护性隔离。"
        ),
        "trigger_factor": "environmental_safety",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，免疫功能严重受损。"
            "在确定性治疗（HSCT/基因治疗）前，严格的感染防护是挽救生命的关键。"
        ),
        "difficulty": "hard",
        "impact": 5,
        "time": "24/7 持续防护",
        "evidence_level": "strong",
        "reference": "SCID 管理指南 | 原发性免疫缺陷感染预防共识",
    },
    {
        "id": "imm_ivig",
        "pillar": "medical",
        "dimension": "immunodeficiency",
        "title": "按时完成免疫球蛋白替代治疗和疫苗接种",
        "description": (
            "对于BTK突变所致XLA，定期IVIG/SCIG替代治疗是维持正常生长发育的基石。"
            "遵医嘱调整疫苗接种计划（活疫苗可能禁忌），确保按时完成所有适龄接种。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，定期免疫球蛋白替代治疗是维持免疫功能的"
            "标准方案。按时治疗可预防感染并支持正常生长发育。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "每 3-4 周一次",
        "evidence_level": "strong",
        "reference": "XLA 管理指南 | 免疫缺陷疫苗接种建议",
    },

    # ── 感官与结构 ──
    {
        "id": "sen_hearing",
        "pillar": "medical",
        "dimension": "sensory",
        "title": "完成诊断性听力评估并尽早干预",
        "description": (
            "对于携带听力损失相关基因变异（GJB2、SLC26A4、USH2A）的宝宝，"
            "新生儿听力筛查后的诊断性听力学评估至关重要。"
            "确诊后尽早（<12月龄）适配助听器或评估人工耳蜗，"
            "配合言语康复训练，可实现接近正常的语言发育。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，早期听力干预的时间窗口非常关键。"
            "12月龄前开始干预的语言预后显著优于延迟干预。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "尽早评估并持续康复",
        "evidence_level": "strong",
        "reference": "婴幼儿听力联合委员会(JCIH)立场声明 | 人工耳蜗植入指南",
    },
    {
        "id": "sen_vision",
        "pillar": "medical",
        "dimension": "sensory",
        "title": "建立定期眼科筛查计划",
        "description": (
            "对于携带视网膜母细胞瘤(RB1)或Usher综合征(USH2A)相关基因变异的宝宝，"
            "从出生开始的定期眼底筛查是挽救视力和生命的关键——"
            "早期发现的RB治愈率>95%。USH2A需定期OCT和视野检查监测视网膜变性进展。"
        ),
        "trigger_factor": "medical_adherence",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，定期眼科筛查是直接改变预后的环境干预。"
            "RB1的早期发现可保住眼球并挽救生命。请勿错过任何筛查。"
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "按眼科筛查频率（视风险等级）",
        "evidence_level": "strong",
        "reference": "RB1 筛查指南 | Usher综合征管理共识",
    },
    {
        "id": "sen_safety",
        "pillar": "safety",
        "dimension": "sensory",
        "title": "预防跌倒和头部外伤（成骨不全/听力损失管理）",
        "description": (
            "对于携带COL1A1（成骨不全）的宝宝，家居安全改造（软垫地板、"
            "家具圆角处理）和正确抱姿是预防骨折的基础。"
            "SLC26A4相关EVA的宝宝需避免头部外伤以防加速听力下降。"
        ),
        "trigger_factor": "environmental_safety",
        "trigger_condition": "below_optimal",
        "why_template": (
            "宝宝携带 {genes} 变异，骨折/听力下降风险增高。"
            "环境安全改造和正确护理技巧是降低伤害风险的第一道防线。"
        ),
        "difficulty": "easy",
        "impact": 4,
        "time": "立即改造并持续维护",
        "evidence_level": "moderate",
        "reference": "成骨不全管理指南 | 大前庭导水管综合征管理建议",
    },

    # ── 通用建议 ──
    {
        "id": "gen_checkup",
        "pillar": "general",
        "dimension": "general",
        "title": "建立多学科儿科随访计划",
        "description": (
            "根据宝宝的基因筛查结果，建立包含儿科遗传专科、相关亚专科"
            "（心脏科/神经科/免疫科/内分泌科/眼科/耳鼻喉科）和"
            "发育儿科的多学科随访时间表。定期评估生长发育和里程碑达成情况。"
        ),
        "trigger_factor": "general",
        "trigger_condition": "always",
        "why_template": (
            "宝宝的基因档案（{genes}）提示需要多学科综合管理。"
            "协调各专科的随访计划可确保不遗漏任何关键评估节点。"
        ),
        "difficulty": "moderate",
        "impact": 4,
        "time": "按各专科建议频率",
        "evidence_level": "strong",
        "reference": "ACMG SF v3.2 管理建议 | 儿科遗传咨询指南",
    },
    {
        "id": "gen_record",
        "pillar": "general",
        "dimension": "general",
        "title": "建立宝宝健康档案和发育日记",
        "description": (
            "记录每日喂养、睡眠、大小便、生长发育（体重/身长/头围）和"
            "重要里程碑的达成情况。系统的记录有助于早期发现偏离正常范围的变化，"
            "也为儿科随访提供客观信息。对携带遗传风险基因的宝宝尤为重要。"
        ),
        "trigger_factor": "general",
        "trigger_condition": "always",
        "why_template": (
            "宝宝的基因档案提示需要密切关注发育轨迹。"
            "系统的日常记录是最基础也最有效的家庭监测工具。"
        ),
        "difficulty": "easy",
        "impact": 3,
        "time": "每日 5-10 分钟",
        "evidence_level": "moderate",
        "reference": "儿童保健随访指南 | 发育监测实用工具",
    },
]


# =============================================================================
# 2. 主入口
# =============================================================================

def generate(
    genetic_risk_profile: dict[str, Any],
    user_preferences: dict | None = None,
    environment: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """生成个性化早期照护建议列表 —— 协作接口。"""
    pref = user_preferences or {}

    dim_scores = genetic_risk_profile.get("dimension_scores", {})
    risk_genes = genetic_risk_profile.get("risk_genes", [])
    overall_level = genetic_risk_profile.get("overall_level", "moderate")
    env = environment or {}

    scored = []
    for rec in RECOMMENDATION_TEMPLATES:
        if not _recommendation_applies(rec, dim_scores, risk_genes, env, pref):
            continue

        priority = _calculate_priority(rec, dim_scores, overall_level)
        if priority <= 0:
            continue

        why = _personalize_why(rec, env, risk_genes, dim_scores)
        related = _find_related_genes(rec, risk_genes)

        scored.append({
            "title": rec["title"],
            "description": rec["description"],
            "trigger_factor": _build_trigger_description(rec, env),
            "why_for_this_user": why,
            "evidence_level": rec.get("evidence_level", "moderate"),
            "related_gene": related,
            "difficulty": rec["difficulty"],
            "impact": rec["impact"],
            "time": rec.get("time", ""),
            "priority": priority,
            "pillar": rec["pillar"],
            "icon": rec.get("icon", "🎯"),
            "reference": rec.get("reference", ""),
            "confidence": {
                "genetic_evidence": _gene_evidence_level(related),
                "interaction_evidence": rec.get("evidence_level", "moderate"),
                "lifestyle_evidence": _lifestyle_evidence_level(rec["difficulty"], rec.get("evidence_level", "moderate")),
            },
        })

    scored.sort(key=lambda r: r["priority"], reverse=True)
    return scored[:8]


# =============================================================================
# 3. 优先级计算
# =============================================================================

def _calculate_priority(rec: dict, dim_scores: dict[str, Any], overall_level: str) -> int:
    """优先级 = 维度趋势权重(0-40) + 证据强度(0-30) + 影响×可行性(0-30)"""
    score = 0

    dim = rec.get("dimension", "general")
    if dim == "general":
        score += 20
    else:
        dim_score = dim_scores.get(dim, 50)
        if isinstance(dim_score, dict):
            dim_score = dim_score.get("score", 50)
        trend_weight = (100 - min(float(dim_score), 95)) / 2
        score += min(40.0, trend_weight)

    evidence_map = {"strong": 30, "moderate": 20, "preliminary": 10}
    score += evidence_map.get(rec.get("evidence_level", "moderate"), 15)

    impact = rec.get("impact", 3)
    difficulty_map = {"easy": 1.0, "moderate": 0.7, "hard": 0.4}
    feasibility = difficulty_map.get(rec.get("difficulty", "moderate"), 0.5)
    score += impact * feasibility * 10

    return int(round(score))


def _recommendation_applies(
    rec: dict,
    dim_scores: dict[str, Any],
    risk_genes: list[str],
    env: dict[str, float],
    prefs: dict,
) -> bool:
    """判断建议是否适用。"""
    dim = rec.get("dimension", "general")
    if dim != "general":
        dim_score = dim_scores.get(dim, 50)
        if isinstance(dim_score, dict):
            dim_score = dim_score.get("score", 50)
        if float(dim_score) >= 90 and rec.get("evidence_level") != "strong":
            return False

    trigger = rec.get("trigger_factor", "")
    condition = rec.get("trigger_condition", "always")
    if trigger in env and condition == "below_optimal":
        ranges = ENVIRONMENT_RANGES.get(trigger)
        if ranges and env[trigger] >= ranges["optimal"]:
            return False
    if trigger in env and condition == "above_optimal":
        ranges = ENVIRONMENT_RANGES.get(trigger)
        if ranges and env[trigger] <= ranges["optimal"]:
            return False
    if trigger in env and condition == "above_zero":
        if env[trigger] <= 0:
            return False

    preferred_difficulty = prefs.get("difficulty")
    if preferred_difficulty and rec.get("difficulty") != preferred_difficulty:
        return False

    return True


# =============================================================================
# 4. 个性化 why_for_this_user
# =============================================================================

def _personalize_why(
    rec: dict,
    env: dict[str, float],
    risk_genes: list[str],
    dim_scores: dict[str, Any],
) -> str:
    """根据宝宝的模拟结果个性化 why_for_this_user。"""
    template = rec.get("why_template", "")
    dim = rec.get("dimension", "general")

    related = _find_related_genes(rec, risk_genes)
    template = template.replace("{genes}", "、".join(related) if related else "基因档案")

    trigger = rec.get("trigger_factor", "")
    if trigger in env:
        template = template.replace("{score}", f"{env[trigger]:.0f}")

    if not template:
        dim_name = DIMENSION_CONFIG.get(dim, {}).get("label", dim)
        template = (
            f"基于宝宝的 {dim_name} 维度评分和 {', '.join(related) if related else '基因'} "
            f"档案，该干预措施针对模拟中识别的可改变因素。"
        )

    return template


def _build_trigger_description(rec: dict, env: dict[str, float]) -> str:
    """构建 trigger_factor 描述。"""
    trigger = rec.get("trigger_factor", "")
    condition = rec.get("trigger_condition", "always")

    if trigger in env and condition == "below_optimal":
        ranges = ENVIRONMENT_RANGES.get(trigger)
        optimal = ranges["optimal"] if ranges else "?"
        return (
            f"{trigger}（当前: {env[trigger]:.0f}，最佳: ~{optimal}）"
            f"在当前模拟中低于最佳水平"
        )
    if trigger in env and condition == "above_optimal":
        return f"{trigger}（当前: {env[trigger]:.0f}）高于最佳水平"
    if trigger in env and condition == "above_zero":
        return f"{trigger} 暴露正在影响发育轨迹"
    if condition == "always":
        return f"与宝宝基因档案相关的通用建议"
    return f"被识别为相关的可改变因素"


def _find_related_genes(rec: dict, risk_genes: list[str]) -> list[str]:
    """找到与该建议相关的基因。"""
    dim = rec.get("dimension", "general")
    related = []
    for gene in risk_genes:
        gw = GENE_WEIGHTS.get(gene, {})
        if dim in gw and gw[dim] > 0:
            related.append(gene)
    return related[:3] if related else risk_genes[:2]


# =============================================================================
# 5. 可信度层
# =============================================================================

def _gene_evidence_level(genes: list[str]) -> str:
    if not genes:
        return "moderate"
    from engine.config import EVIDENCE_CONFIDENCE
    levels = [EVIDENCE_CONFIDENCE.get(g, {}).get("genetic_evidence", "moderate") for g in genes]
    if "high" in levels:
        return "high"
    return "moderate"


def _lifestyle_evidence_level(difficulty: str, base_evidence: str) -> str:
    if base_evidence == "strong":
        return "high"
    if difficulty == "hard":
        return "moderate"
    return "moderate"


# =============================================================================
# 6. 便捷函数
# =============================================================================

def generate_from_simulation(
    simulation_result: dict[str, Any],
    genetic_profile: dict[str, float] | None = None,
    environment: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """从 G×E 模拟结果生成建议。"""
    dim_scores_raw = simulation_result.get("dimension_scores", {})
    dim_scores = {
        key: data.get("score", 50) if isinstance(data, dict) else data
        for key, data in dim_scores_raw.items()
    }

    risk_genes = list(genetic_profile.keys()) if genetic_profile else []

    baseline = simulation_result.get("baseline_hti", 72)
    if baseline >= 85:
        overall = "advantage"
    elif baseline >= 55:
        overall = "moderate"
    else:
        overall = "attention"

    profile = {
        "dimension_scores": dim_scores,
        "risk_genes": risk_genes,
        "overall_level": overall,
    }

    return generate(profile, None, environment)


# =============================================================================
# 7. 运行示例
# =============================================================================

if __name__ == "__main__":
    from engine.gxe_model import simulate_health_trajectory

    print("=" * 70)
    print("儿科推荐引擎 v3.0 — 演示")
    print("=" * 70)

    genetic = {
        "PAH": 0.4, "G6PD": 0.3, "SMN1": 0.5, "GJB2": 0.35,
        "CHD7": 0.35, "IL2RG": 0.5, "CFTR": 0.35,
    }
    env = {
        "nutrition_type": 7, "sleep_quality": 7,
        "development_stimulation": 6, "medical_adherence": 9,
        "environmental_safety": 8,
    }
    sim = simulate_health_trajectory(genetic, env)

    recs = generate_from_simulation(sim, genetic, env)
    print(f"\n生成了 {len(recs)} 条个性化建议:\n")
    for i, r in enumerate(recs, 1):
        diff = {"easy": "简单", "moderate": "中等", "hard": "困难"}.get(r["difficulty"], r["difficulty"])
        print(f"{i}. [{r['priority']:3d}] {r['title']}")
        print(f"   触发: {r['trigger_factor']}")
        print(f"   原因: {r['why_for_this_user'][:120]}...")
        print(f"   基因: {r['related_gene']} | 难度: {diff} | 影响: {'★' * r['impact']}")
        print(f"   证据: {r['evidence_level']} | 可信度: {r['confidence']}")
        print()

    print(f"{'=' * 70}")
    print("演示完成。")
    print(f"{'=' * 70}")
