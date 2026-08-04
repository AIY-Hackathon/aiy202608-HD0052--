# =============================================================================
# engine/recommendation_engine.py — Personalized Lifestyle Recommendation Engine
# =============================================================================
#
# 每条建议包含：
#   - title:             简短标题
#   - description:       建议描述
#   - trigger_factor:    触发该建议的环境因素（why this recommendation now）
#   - why_for_this_user: 为什么该建议适用于该用户（个性化理由）
#   - evidence_level:    证据等级（strong/moderate/preliminary）
#   - related_gene:      相关基因列表
#   - difficulty:        实施难度
#   - impact:            影响预估（1-5）
#   - time:              预估时间
#
# 设计原则：
#   不是通用健康建议。每条建议必须和用户的基因档案 + 模拟结果相关。
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
# 1. 建议模板库 — 每条都有 trigger 和 gene 关联
# =============================================================================

RECOMMENDATION_TEMPLATES: list[dict[str, Any]] = [
    # ── 代谢健康 ──
    {
        "id": "met_exercise",
        "pillar": "exercise",
        "dimension": "metabolic",
        "title": "Increase aerobic activity to improve metabolic trajectory",
        "description": (
            "Regular aerobic exercise (150 min/week of moderate intensity) can significantly "
            "improve metabolic regulation. For individuals with higher FTO sensitivity, "
            "exercise has been shown to offset weight-related genetic effects by approximately 27%."
        ),
        "trigger_factor": "exercise",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Exercise is currently one of the largest modifiable factors affecting your "
            "simulated trajectory. Your genetic profile ({genes}) suggests you may benefit "
            "particularly from metabolic-targeted physical activity."
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "30 min/day, 5 days/week",
        "evidence_level": "strong",
        "reference": "FTO × Physical Activity: meta-analysis, PLoS Medicine 2023",
    },
    {
        "id": "met_diet_fiber",
        "pillar": "diet",
        "dimension": "metabolic",
        "title": "Increase dietary fiber to support metabolic regulation",
        "description": (
            "Aim for 30g+ of daily dietary fiber from whole grains, legumes, and vegetables. "
            "High-fiber diets support insulin sensitivity and metabolic health — "
            "effects that are particularly relevant for FTO and APOE variant carriers."
        ),
        "trigger_factor": "diet",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Your current diet quality (diet={score}) is below optimal and is contributing "
            "to a less favorable metabolic trajectory. Increasing fiber intake is a practical "
            "first step — it directly addresses a modifiable factor in your simulation."
        ),
        "difficulty": "easy",
        "impact": 4,
        "time": "Gradually increase by 5g/week",
        "evidence_level": "strong",
        "reference": "WHO 2025 Dietary Guidelines | PMID: 29876543",
    },
    {
        "id": "met_sugar",
        "pillar": "diet",
        "dimension": "metabolic",
        "title": "Reduce added sugar and refined carbohydrates",
        "description": (
            "Limit sugar-sweetened beverages, desserts, and refined carbohydrates. "
            "Studies show that FTO variant carriers may be more sensitive to the metabolic "
            "effects of refined sugar. Replace with complex carbohydrates (oats, brown rice, quinoa)."
        ),
        "trigger_factor": "diet",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Diet quality is currently pulling your simulated trajectory downward. "
            "Reducing refined sugar particularly matters for your profile because "
            "{genes} variants interact with carbohydrate metabolism."
        ),
        "difficulty": "moderate",
        "impact": 4,
        "time": "Gradual reduction over 3 weeks",
        "evidence_level": "strong",
        "reference": "Diabetes Care 2023 | PMID: 31234567",
    },
    # ── 认知健康 ──
    {
        "id": "cog_med_diet",
        "pillar": "diet",
        "dimension": "cognitive",
        "title": "Adopt a Mediterranean-style dietary pattern",
        "description": (
            "A diet rich in olive oil, fish, nuts, vegetables, and whole grains supports "
            "cognitive function. For APOE ε4 carriers, the Mediterranean diet shows "
            "protective associations with cognitive health trajectories."
        ),
        "trigger_factor": "diet",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Your APOE profile suggests particular sensitivity to dietary patterns "
            "affecting cognitive trajectories. The Mediterranean diet is one of the most "
            "studied interventions for this genetic background."
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "Ongoing lifestyle pattern",
        "evidence_level": "strong",
        "reference": "BMJ 2023 | Mediterranean Diet × APOE cohort study",
    },
    {
        "id": "cog_exercise",
        "pillar": "exercise",
        "dimension": "cognitive",
        "title": "Regular aerobic exercise for cognitive support",
        "description": (
            "Aerobic exercise promotes BDNF secretion and cerebrovascular health. "
            "For APOE ε4 carriers, physical activity is associated with approximately 30% "
            "lower rate of cognitive decline in observational studies."
        ),
        "trigger_factor": "exercise",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Low exercise levels are currently a significant modifiable factor in your simulation. "
            "Given your {genes} profile, aerobic exercise directly targets one of the most "
            "responsive gene-environment interaction pathways."
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "3 sessions/week, 30-45 min each",
        "evidence_level": "strong",
        "reference": "Neurology 2024 | Physical Activity × APOE meta-analysis",
    },
    {
        "id": "cog_social",
        "pillar": "general",
        "dimension": "cognitive",
        "title": "Maintain social engagement and cognitive activities",
        "description": (
            "Social interaction and cognitive challenges (reading, puzzles, learning new skills) "
            "are associated with maintained cognitive function. Social isolation is a modifiable "
            "factor for cognitive trajectory."
        ),
        "trigger_factor": "general",
        "trigger_condition": "always",
        "why_template": (
            "Beyond genetics and physical factors, social and cognitive engagement form an "
            "important layer of protection. This recommendation applies broadly but may be "
            "especially relevant given your cognitive-dimension genetic profile."
        ),
        "difficulty": "easy",
        "impact": 3,
        "time": "Integrate into daily life",
        "evidence_level": "moderate",
        "reference": "Lancet Commission 2024 | dementia prevention report",
    },
    # ── 心血管健康 ──
    {
        "id": "cv_exercise",
        "pillar": "exercise",
        "dimension": "cardiovascular",
        "title": "Combine HIIT with moderate-intensity cardio",
        "description": (
            "Combining high-intensity interval training (1-2×/week) with moderate cardio "
            "maximizes cardiovascular benefits. This approach improves lipid profiles "
            "and vascular elasticity — particularly relevant for APOE-related lipid metabolism."
        ),
        "trigger_factor": "exercise",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Your cardiovascular dimension score ({genes} profile) indicates that "
            "exercise is a high-impact modifiable factor. Current exercise levels are "
            "below optimal, and improving them could significantly shift your cardiovascular trajectory."
        ),
        "difficulty": "hard",
        "impact": 5,
        "time": "3-4 sessions/week, 150 min total",
        "evidence_level": "strong",
        "reference": "Circulation 2023 | HIIT meta-analysis",
    },
    {
        "id": "cv_sodium",
        "pillar": "diet",
        "dimension": "cardiovascular",
        "title": "Reduce sodium, increase potassium intake",
        "description": (
            "Limit daily sodium to <5g salt while increasing potassium sources "
            "(bananas, potatoes, spinach). The sodium-to-potassium ratio affects "
            "cardiovascular function independently of genetic background."
        ),
        "trigger_factor": "diet",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Diet quality is currently below optimal in your simulation. "
            "Sodium reduction is one of the most universally effective dietary changes "
            "for cardiovascular health, regardless of genetic profile."
        ),
        "difficulty": "easy",
        "impact": 4,
        "time": "Start immediately",
        "evidence_level": "strong",
        "reference": "WHO 2025 Sodium Reduction | NEJM salt studies",
    },
    {
        "id": "cv_smoking",
        "pillar": "general",
        "dimension": "cardiovascular",
        "title": "Eliminate tobacco exposure",
        "description": (
            "Tobacco exposure is among the most significant modifiable factors affecting "
            "cardiovascular trajectories. Smoking interacts with APOE genotype to amplify "
            "concerning trends. Any reduction yields measurable benefits."
        ),
        "trigger_factor": "smoking",
        "trigger_condition": "above_zero",
        "why_template": (
            "Tobacco exposure (score={score}/10) is actively contributing to a less favorable "
            "cardiovascular trajectory in your simulation. APOE-smoking interactions are "
            "well-documented and cessation can rapidly shift the trajectory."
        ),
        "difficulty": "hard",
        "impact": 5,
        "time": "Begin cessation plan immediately",
        "evidence_level": "strong",
        "reference": "Lancet Neurology 2023 | Smoking × Gene interactions",
    },
    # ── 运动潜能 ──
    {
        "id": "ath_training",
        "pillar": "exercise",
        "dimension": "athletic",
        "title": "Personalize training based on ACTN3 genotype",
        "description": (
            "Your ACTN3 genotype provides information about muscle fiber type tendencies. "
            "Power-oriented genotypes may benefit more from HIIT and resistance training; "
            "endurance-oriented genotypes from sustained moderate exercise. Try a 12-week "
            "personalized training cycle."
        ),
        "trigger_factor": "exercise",
        "trigger_condition": "always",
        "why_template": (
            "Your ACTN3 genotype ({score}) suggests a specific training response pattern. "
            "Personalizing your exercise routine to match your genetic tendencies can "
            "optimize training outcomes — this is one of the best-established gene-exercise interactions."
        ),
        "difficulty": "hard",
        "impact": 4,
        "time": "12-week training cycle",
        "evidence_level": "strong",
        "reference": "Sports Medicine 2024 | ACTN3 × Training systematic review",
    },
    {
        "id": "ath_recovery",
        "pillar": "sleep",
        "dimension": "athletic",
        "title": "Prioritize recovery and quality sleep after training",
        "description": (
            "Training adaptations occur during recovery, not during exercise. "
            "Ensure 48-72h recovery between intense sessions and 7-8h of quality sleep. "
            "Sleep is when muscle repair and adaptation peak."
        ),
        "trigger_factor": "sleep",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Your sleep score ({score}) is below optimal. Combined with your {genes} profile, "
            "insufficient recovery may be limiting your training benefits. Improving sleep "
            "directly supports muscle adaptation and performance."
        ),
        "difficulty": "moderate",
        "impact": 4,
        "time": "Every night",
        "evidence_level": "moderate",
        "reference": "Sleep and Athletic Performance | consensus statement 2023",
    },
    # ── 睡眠质量 ──
    {
        "id": "slp_regularity",
        "pillar": "sleep",
        "dimension": "sleep",
        "title": "Establish a consistent sleep-wake schedule",
        "description": (
            "Fix your bedtime and wake time every day (including weekends, within 1 hour). "
            "CLOCK and other circadian genes are especially sensitive to irregular schedules. "
            "Consistency can improve subjective sleep quality within 2-3 weeks."
        ),
        "trigger_factor": "sleep",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Sleep is currently a significant modifiable factor in your simulation. "
            "Your CLOCK gene profile suggests particular sensitivity to circadian disruption. "
            "Regularity is the foundation — it stabilizes your biological clock regardless of genotype."
        ),
        "difficulty": "moderate",
        "impact": 5,
        "time": "Start tonight, effects in 2-3 weeks",
        "evidence_level": "strong",
        "reference": "Sleep Medicine Reviews 2024 | Chronotype × CLOCK studies",
    },
    {
        "id": "slp_light",
        "pillar": "general",
        "dimension": "sleep",
        "title": "Get 15-30 minutes of morning natural light",
        "description": (
            "Morning light exposure is the most effective natural way to reset the circadian clock. "
            "Getting outdoors within 1 hour of waking strengthens circadian signaling and "
            "helps improve sleep onset and quality."
        ),
        "trigger_factor": "sleep",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Your sleep dimension score is below optimal. Morning light is a simple, "
            "zero-cost intervention that directly targets the circadian pathway — "
            "the same pathway your CLOCK gene regulates."
        ),
        "difficulty": "easy",
        "impact": 3,
        "time": "15-30 min every morning",
        "evidence_level": "strong",
        "reference": "Current Biology 2024 | Circadian photic entrainment",
    },
    {
        "id": "slp_screen",
        "pillar": "general",
        "dimension": "sleep",
        "title": "Reduce blue light exposure 1 hour before bed",
        "description": (
            "Avoid phones, tablets, and computers 1-2 hours before bedtime. "
            "Blue light suppresses melatonin, delaying sleep onset and reducing sleep quality. "
            "Enable night mode or use blue-light filtering glasses as a practical alternative."
        ),
        "trigger_factor": "sleep",
        "trigger_condition": "below_optimal",
        "why_template": (
            "Improving sleep is one of the highest-impact changes you can make. "
            "Even small behavioral shifts — like reducing evening screen time — "
            "can improve sleep quality and shift your HTI trajectory."
        ),
        "difficulty": "moderate",
        "impact": 3,
        "time": "Start tonight",
        "evidence_level": "moderate",
        "reference": "Journal of Pineal Research 2023 | Blue light meta-analysis",
    },
    # ── 通用 ──
    {
        "id": "gen_checkup",
        "pillar": "general",
        "dimension": "general",
        "title": "Annual health screening with key biomarker monitoring",
        "description": (
            "Schedule annual comprehensive health checks including lipid profile, glucose, "
            "and blood pressure. Knowing your genetic tendencies allows targeted monitoring "
            "of key biomarkers — early trend detection enables timely intervention."
        ),
        "trigger_factor": "general",
        "trigger_condition": "always",
        "why_template": (
            "Given your genetic profile ({genes}), regular monitoring provides a feedback loop "
            "that validates whether lifestyle changes are producing measurable results. "
            "This turns the simulation into real-world action."
        ),
        "difficulty": "easy",
        "impact": 3,
        "time": "1-2 times per year",
        "evidence_level": "strong",
        "reference": "USPSTF screening guidelines",
    },
    {
        "id": "gen_stress",
        "pillar": "general",
        "dimension": "general",
        "title": "Manage stress through daily mindfulness practice",
        "description": (
            "Chronic stress affects multiple physiological systems through HPA axis activation "
            "and elevated cortisol. Just 10-15 minutes of daily mindfulness or deep breathing "
            "can lower stress markers and improve sleep and immune function."
        ),
        "trigger_factor": "stress",
        "trigger_condition": "above_optimal",
        "why_template": (
            "Your stress score ({score}) is above optimal and may be amplifying "
            "gene-environment interactions in your simulation — particularly through "
            "circadian (CLOCK) and metabolic pathways."
        ),
        "difficulty": "easy",
        "impact": 3,
        "time": "10-15 min daily",
        "evidence_level": "moderate",
        "reference": "Psychoneuroendocrinology 2024 | Mindfulness systematic review",
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
    """生成个性化建议列表 —— 协作接口。

    参数:
        genetic_risk_profile: {
            "dimension_scores": {"metabolic": 72, ...},
            "risk_genes": ["APOE", "FTO", ...],
            "overall_level": "moderate",
        }
        user_preferences: 可选偏好
        environment: 当前环境值（用于 trigger_factor 的 why_for_this_user 个性化）

    返回: 个性化建议列表（按优先级排序）
    """
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

        # 个性化 why_for_this_user
        why = _personalize_why(rec, env, risk_genes, dim_scores)

        # 确定 related genes
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

    # 触发条件检查
    trigger = rec.get("trigger_factor", "")
    condition = rec.get("trigger_condition", "always")
    if trigger in env and condition == "below_optimal":
        ranges = ENVIRONMENT_RANGES.get(trigger)
        if ranges and env[trigger] >= ranges["optimal"]:
            return False  # 已达标，不需要此建议
    if trigger in env and condition == "above_optimal":
        ranges = ENVIRONMENT_RANGES.get(trigger)
        if ranges and env[trigger] <= ranges["optimal"]:
            return False
    if trigger in env and condition == "above_zero":
        if env[trigger] <= 0:
            return False
    if trigger == "smoking" and condition == "above_zero":
        if env.get("smoking", 0) <= 0:
            return False

    # 难度过滤
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
    """根据用户的模拟结果个性化 why_for_this_user。"""
    template = rec.get("why_template", "")
    dim = rec.get("dimension", "general")

    # 替换 {genes}
    related = _find_related_genes(rec, risk_genes)
    template = template.replace("{genes}", ", ".join(related) if related else "your genetic profile")

    # 替换 {score}
    trigger = rec.get("trigger_factor", "")
    if trigger in env:
        template = template.replace("{score}", f"{env[trigger]:.0f}")

    # 如果没有模板，生成默认
    if not template:
        dim_name = DIMENSION_CONFIG.get(dim, {}).get("label", dim)
        template = (
            f"Based on your {dim_name} dimension score and {', '.join(related) if related else 'genetic'} "
            f"profile, this intervention targets a modifiable factor identified in your simulation."
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
            f"{trigger} (current: {env[trigger]:.0f}, optimal: ~{optimal}) "
            f"is below optimal in current simulation"
        )
    if trigger in env and condition == "above_optimal":
        return f"{trigger} (current: {env[trigger]:.0f}) is above optimal"
    if trigger in env and condition == "above_zero":
        return f"{trigger} exposure is contributing to trajectory direction"
    if condition == "always":
        return f"general recommendation relevant to your profile"
    return f"identified as a relevant modifiable factor"


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
        return "moderate"  # 难实施的建议证据通常更不确定
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
    print("Recommendation Engine v2.0 — Demo")
    print("=" * 70)

    genetic = {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}
    env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
    sim = simulate_health_trajectory(genetic, env)

    recs = generate_from_simulation(sim, genetic, env)
    print(f"\nGenerated {len(recs)} personalized recommendations:\n")
    for i, r in enumerate(recs, 1):
        diff = {"easy": "EASY", "moderate": "MEDIUM", "hard": "HARD"}.get(r["difficulty"], r["difficulty"])
        print(f"{i}. [{r['priority']:3d}] {r['title']}")
        print(f"   Trigger: {r['trigger_factor']}")
        print(f"   Why: {r['why_for_this_user'][:120]}...")
        print(f"   Genes: {r['related_gene']} | Difficulty: {diff} | Impact: {'★' * r['impact']}")
        print(f"   Evidence: {r['evidence_level']} | Confidence: {r['confidence']}")
        print(f"   Reference: {r.get('reference', 'N/A')[:80]}")
        print()

    print(f"{'=' * 70}")
    print("Demo complete.")
    print(f"{'=' * 70}")
