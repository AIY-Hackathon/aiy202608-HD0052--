# =============================================================================
# engine/ai_interpreter.py — Explainable AI Interpretation Module
# =============================================================================
#
# 双模型设计（预留）：
#   - DeepSeek：结构化分析（提取关键事实、趋势分类、证据评级）
#   - Claude：自然语言解释（面向用户的科普叙述）
#
# 当前实现：Mock 模式（基于知识库 + 模拟结果 + 规则引擎）
#
# 核心理念：
#   我们不预测疾病，我们模拟不同生活方式选择如何影响未来健康趋势。
#   Genes are not destiny.
#
# 输出格式（升级版）：
#   {
#     "genetic_story":       "基因背景叙述",
#     "main_driver":          "主导因素（基因/环境/交互）",
#     "modifiable_factor":    "最可改变的因素",
#     "simulation_message":   "模拟洞察",
#     "scientific_note":      "科学依据说明",
#     "disclaimer":           "免责声明",
#   }
# =============================================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
_gene_db: dict | None = None
_api_config: dict | None = None


def _load_gene_db() -> dict:
    global _gene_db
    if _gene_db is not None:
        return _gene_db
    db_path = _KNOWLEDGE_DIR / "gene_database.json"
    if db_path.exists():
        _gene_db = json.loads(db_path.read_text(encoding="utf-8"))
    else:
        _gene_db = {"genes": [], "health_dimensions": {}}
    return _gene_db


def _load_api_config() -> dict:
    global _api_config
    if _api_config is not None:
        return _api_config
    _api_config = {
        "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "deepseek_base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "use_mock": os.getenv("AI_USE_MOCK", "true").lower() in ("true", "1", "yes"),
    }
    return _api_config


# =============================================================================
# 1. 主入口 — 单基因解释
# =============================================================================

def interpret_gene_info(
    gene_symbol: str,
    genotype_info: str | None = None,
    trend_level: str | None = None,
) -> dict[str, Any]:
    """解释单个基因的健康信息（mock 模式）。

    返回 6 字段结构化输出。
    """
    gene_db = _load_gene_db()
    gene_meta = {}
    for g in gene_db.get("genes", []):
        if g["symbol"].upper() == gene_symbol.upper():
            gene_meta = g
            break

    if not gene_meta:
        gene_meta = {
            "symbol": gene_symbol, "name": gene_symbol,
            "function": "information not yet available",
            "health_domain": "information not yet available",
            "evidence_level": "preliminary",
            "summary_for_display": f"{gene_symbol} gene information has not yet been added to the knowledge base.",
            "environment_interaction": [],
        }

    return {
        "genetic_story": _build_genetic_story(gene_meta, genotype_info, trend_level),
        "main_driver": _build_main_driver(gene_meta),
        "modifiable_factor": _build_modifiable_factor(gene_meta),
        "simulation_message": _build_gene_simulation_message(gene_meta, trend_level),
        "scientific_note": _build_scientific_note(gene_meta),
        "disclaimer": _build_disclaimer(),
        "mode": "mock",
        "gene_info": {
            "symbol": gene_meta.get("symbol", gene_symbol),
            "name": gene_meta.get("name", ""),
            "health_domain": gene_meta.get("health_domain", ""),
            "evidence_level": gene_meta.get("evidence_level", "moderate"),
        },
        "confidence": {
            "genetic_evidence": gene_meta.get("evidence_level", "moderate"),
            "interaction_evidence": (
                gene_meta.get("environment_interaction", [{}])[0].get("evidence_strength", "moderate")
                if gene_meta.get("environment_interaction") else "preliminary"
            ),
            "lifestyle_evidence": "moderate",
        },
        "generated_at": _now_iso(),
    }


# =============================================================================
# 2. 主入口 — 模拟结果综合解读
# =============================================================================

def interpret_simulation_result(
    simulation_result: dict,
    genetic_profile: dict,
    environment: dict,
    counterfactual_result: dict | None = None,
) -> dict[str, Any]:
    """解读 G×E 模拟结果，生成 6 字段结构化解释。

    参数:
        simulation_result: simulate_health_trajectory() 返回
        genetic_profile: 基因档案
        environment: 当前环境
        counterfactual_result: 可选，compare_scenarios() 返回的场景对比

    返回: 6 字段结构
    """
    baseline_hti = simulation_result.get("baseline_hti", 72)
    trajectory = simulation_result.get("trajectory", [])
    summary = simulation_result.get("summary", {})
    gene_total = summary.get("gene_effect", 0)
    env_total = summary.get("environment_effect", 0)
    interaction_total = summary.get("interaction_effect", 0)

    # ── 1. genetic_story ──
    high_sensitivity_genes = [g for g, v in genetic_profile.items() if v > 0.5]
    low_sensitivity_genes = [g for g, v in genetic_profile.items() if v <= 0.5]
    genetic_story = _format_genetic_story(high_sensitivity_genes, low_sensitivity_genes, gene_total)

    # ── 2. main_driver ──
    main_driver = _determine_main_driver(gene_total, env_total, interaction_total)

    # ── 3. modifiable_factor ──
    modifiable_factor = _identify_most_modifiable_factor(environment, genetic_profile)

    # ── 4. simulation_message ──
    simulation_message = _build_simulation_narrative(
        baseline_hti, trajectory, main_driver, modifiable_factor, counterfactual_result
    )

    # ── 5. scientific_note ──
    scientific_note = _build_simulation_scientific_note(
        genetic_profile, baseline_hti, gene_total, env_total, interaction_total
    )

    # ── 6. disclaimer ──
    disclaimer = _build_disclaimer()

    return {
        "genetic_story": genetic_story,
        "main_driver": main_driver,
        "modifiable_factor": modifiable_factor,
        "simulation_message": simulation_message,
        "scientific_note": scientific_note,
        "disclaimer": disclaimer,
        "mode": "mock",
        "simulation_insights": {
            "baseline_hti": baseline_hti,
            "dominant_factor": main_driver["dominant_factor"],
            "gene_effect": gene_total,
            "environment_effect": env_total,
            "interaction_effect": interaction_total,
        },
        "generated_at": _now_iso(),
    }


# =============================================================================
# 3. 构建各输出字段
# =============================================================================

def _build_genetic_story(gene: dict, genotype: str | None, trend: str | None) -> str:
    """构建基因背景叙述。"""
    parts = [
        f"{gene.get('symbol', '')} ({gene.get('name', '')}) "
        f"{gene.get('function', '')}. "
        f"This gene is associated with {gene.get('health_domain', 'various health domains')}.",
    ]
    if genotype:
        parts.append(f" Detected genotype: {genotype}.")
    if trend:
        trend_map = {
            "advantage": "associated with a more favorable trend in related health dimensions",
            "favorable": "showing a generally favorable trend",
            "moderate": "showing a moderate trend pattern",
            "attention": "may benefit from additional attention to lifestyle factors",
            "significant": "may be significantly influenced by modifiable environmental factors",
        }
        parts.append(f" This variant is {trend_map.get(trend, trend)}.")

    interactions = gene.get("environment_interaction", [])
    if interactions:
        parts.append(
            f" Key environmental interactions: "
            + "; ".join(
                f"{i['factor']} ({i['interaction_type']})" for i in interactions[:2]
            )
            + "."
        )

    return "".join(parts)


def _build_main_driver(gene: dict) -> dict:
    """构建基因主导因素分析。"""
    interactions = gene.get("environment_interaction", [])
    return {
        "gene_role": (
            f"{gene.get('symbol', '')} plays a role in {gene.get('health_domain', 'health')}. "
            f"Evidence level: {gene.get('evidence_level', 'moderate')}."
        ),
        "key_interactions": [
            {
                "factor": i["factor"],
                "type": i.get("interaction_type", ""),
                "evidence": i.get("evidence_strength", "preliminary"),
            }
            for i in interactions[:3]
        ],
    }


def _build_modifiable_factor(gene: dict) -> dict:
    """识别该基因最可改变的影响因素。"""
    interactions = gene.get("environment_interaction", [])
    if not interactions:
        return {"factor": "lifestyle", "reason": "General lifestyle modifications may have a positive impact."}

    # 取证据最强的
    strongest = max(interactions, key=lambda i: {
        "strong": 3, "moderate": 2, "preliminary": 1
    }.get(i.get("evidence_strength", "preliminary"), 1))

    return {
        "factor": strongest.get("factor", "lifestyle"),
        "interaction_type": strongest.get("interaction_type", ""),
        "evidence_strength": strongest.get("evidence_strength", "moderate"),
        "reason": (
            f"{strongest.get('factor', 'Lifestyle')} shows a "
            f"{strongest.get('interaction_type', 'notable')} interaction with {gene.get('symbol', 'this gene')} "
            f"({strongest.get('evidence_strength', 'moderate')} evidence)."
        ),
    }


def _build_gene_simulation_message(gene: dict, trend: str | None) -> str:
    """生成面向用户的教育性模拟信息。"""
    symbol = gene.get("symbol", "this gene")

    if trend == "significant" or trend == "attention":
        return (
            f"Your simulated profile for {symbol} suggests this gene contributes to "
            f"a trend that may benefit from lifestyle attention. However, this is not a prediction — "
            f"it reflects how genetic background and current environmental factors interact in the simulation. "
            f"Lifestyle modifications can shift the simulated trajectory."
        )
    elif trend == "advantage":
        return (
            f"Your simulated profile for {symbol} shows a generally favorable trend pattern. "
            f"This does not mean 'no risk' — rather, it suggests that with continued healthy choices, "
            f"the simulated trajectory remains positive. Maintaining lifestyle habits is still important."
        )
    else:
        return (
            f"Your {symbol} profile shows a moderate trend pattern. "
            f"Remember: genetic variants provide tendencies, not certainties. "
            f"Environmental factors and lifestyle choices play a major role in shaping actual outcomes."
        )


def _build_scientific_note(gene: dict) -> str:
    """构建科学依据说明。"""
    interactions = gene.get("environment_interaction", [])
    refs = []
    for i in interactions:
        ref = i.get("reference", "")
        strength = i.get("evidence_strength", "")
        if ref:
            refs.append(f"- [{strength}] {ref}")

    ref_text = "\n".join(refs) if refs else "No detailed references available in current knowledge base."

    return (
        f"Gene function description source: {gene.get('reference', 'NCBI Gene / GWAS Catalog')}. "
        f"Evidence level: {gene.get('evidence_level', 'moderate')} "
        f"(based on multi-population GWAS and functional studies).\n\n"
        f"Environmental interaction evidence:\n{ref_text}\n\n"
        f"Evidence interpretation: "
        f"'strong' = consistent support from multiple meta-analyses; "
        f"'moderate' = multiple studies support with some inconsistency; "
        f"'preliminary' = early-stage research, further validation needed."
    )


def _build_disclaimer() -> str:
    return (
        "IMPORTANT DISCLAIMER\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This interpretation is generated by an AI model based on publicly available "
        "scientific literature and is for EDUCATIONAL REFERENCE ONLY.\n\n"
        "- This system is NOT a medical device.\n"
        "- It does NOT provide clinical diagnosis or treatment recommendations.\n"
        "- HTI (Health Trajectory Index) is a simulated educational metric, NOT a health prediction.\n"
        "- Genetic variants provide tendencies, not certainties.\n"
        "- Consult qualified healthcare professionals for any health-related decisions.\n"
        "- Current genetic reference data is primarily based on East Asian and European population studies.\n\n"
        "AI Model Version: v2.0-mock | Generated: " + _now_iso() + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# =============================================================================
# 4. 模拟结果解释构建
# =============================================================================

def _format_genetic_story(
    high_sensitivity: list[str],
    low_sensitivity: list[str],
    gene_total: float,
) -> str:
    """构建基因背景故事。"""
    parts = []
    if high_sensitivity:
        genes_str = ", ".join(high_sensitivity)
        parts.append(
            f"Your genetic profile shows higher sensitivity variants in: {genes_str}. "
            f"These genes may influence how your body responds to environmental factors. "
        )
    if low_sensitivity:
        genes_str = ", ".join(low_sensitivity)
        parts.append(
            f"Other genes ({genes_str}) show moderate or lower sensitivity patterns. "
        )
    parts.append(
        f"The overall genetic contribution to your simulated HTI is {gene_total:+.1f} points. "
        f"This reflects how genetic background shapes the baseline — "
        f"but environmental factors and lifestyle choices determine the modifiable space."
    )
    return "".join(parts)


def _determine_main_driver(
    gene_total: float,
    env_total: float,
    interaction_total: float,
) -> dict:
    """确定当前模拟轨迹的主导驱动因素。"""
    abs_g = abs(gene_total)
    abs_e = abs(env_total)
    abs_i = abs(interaction_total)

    if abs_e > abs_g and abs_e > abs_i:
        dominant = "environment/lifestyle factors"
        detail = (
            "Your current simulated trajectory is primarily shaped by environmental "
            "and lifestyle factors rather than genetic background alone. "
            "This means lifestyle modifications could have a meaningful impact on your trajectory."
        )
    elif abs_g > abs_e and abs_g > abs_i:
        dominant = "genetic background"
        detail = (
            "Genetic background is the largest contributor to your current simulated trajectory. "
            "However, this does NOT mean the outcome is fixed — "
            "gene-environment interactions still allow for significant modulation through lifestyle."
        )
    else:
        dominant = "gene-environment interaction"
        detail = (
            "The interaction between your genetic profile and environment is the main driver. "
            "This highlights the importance of personalized lifestyle strategies — "
            "the same change may affect different genetic profiles differently."
        )

    return {
        "dominant_factor": dominant,
        "detail": detail,
        "gene_contribution": round(gene_total, 2),
        "environment_contribution": round(env_total, 2),
        "interaction_contribution": round(interaction_total, 2),
    }


def _identify_most_modifiable_factor(
    environment: dict[str, float],
    genetic_profile: dict[str, float],
) -> dict:
    """识别最具改善潜力的可调节因素。"""
    from engine.config import ENVIRONMENT_RANGES, INTERACTION_COEFFICIENTS

    candidates = []
    for factor, value in environment.items():
        if factor == "smoking":
            continue  # 吸烟不是"可调节"的教育重点
        ranges = ENVIRONMENT_RANGES.get(factor)
        if ranges is None:
            continue
        optimal = ranges["optimal"]
        gap = optimal - value if factor not in ("stress",) else value - optimal
        # gap > 0 表示还有改善空间
        if gap <= 0:
            continue

        # 计算该因素与基因的交互总量
        interaction_strength = 0.0
        for gene in genetic_profile:
            ic = INTERACTION_COEFFICIENTS.get(gene, {})
            interaction_strength += abs(ic.get(factor, 0))

        candidates.append({
            "factor": factor,
            "label": ranges.get("label", factor),
            "current": value,
            "optimal": optimal,
            "gap": gap,
            "interaction_strength": interaction_strength,
        })

    if not candidates:
        return {
            "factor": "lifestyle",
            "label": "Lifestyle",
            "reason": "Your lifestyle factors are near optimal. Continue maintaining healthy habits.",
        }

    # 排序：gap * (1 + interaction_strength) → 改变空间大+与基因交互强=优先级高
    candidates.sort(key=lambda c: c["gap"] * (1 + c["interaction_strength"]), reverse=True)
    best = candidates[0]

    return {
        "factor": best["factor"],
        "label": best["label"],
        "current_value": best["current"],
        "optimal_value": best["optimal"],
        "improvement_potential": round(best["gap"], 1),
        "reason": (
            f"{best['label']} (current: {best['current']}, optimal: ~{best['optimal']}) "
            f"shows the most room for improvement among modifiable factors. "
            f"Its interaction with your genetic profile suggests changes here could meaningfully "
            f"shift your simulated trajectory."
        ),
    }


def _build_simulation_narrative(
    baseline_hti: int,
    trajectory: list,
    main_driver: dict,
    modifiable_factor: dict,
    counterfactual: dict | None,
) -> str:
    """生成核心模拟洞察叙述。"""
    dominant = main_driver.get("dominant_factor", "multiple factors")

    # 轨迹描述
    if trajectory:
        start = trajectory[0]["hti"]
        end = trajectory[-1]["hti"]
        years = trajectory[-1]["year"]
        change = end - start

        if change < -5:
            trajectory_note = (
                f"Over the simulated {years}-year period, the HTI shows a declining trend "
                f"(from {baseline_hti} to {end}). This reflects how current lifestyle patterns "
                f"and genetic background interact over time in the simulation — "
                f"but this is not a fixed prediction."
            )
        elif change > 5:
            trajectory_note = (
                f"The simulated {years}-year trajectory shows a generally improving trend "
                f"(+{change} HTI). Continued positive lifestyle habits could help sustain "
                f"this favorable direction."
            )
        else:
            trajectory_note = (
                f"The simulated trajectory remains relatively stable over {years} years "
                f"({baseline_hti} → {end}). Further lifestyle improvements could shift "
                f"this trajectory upward."
            )
    else:
        trajectory_note = ""

    # 主要信息
    if dominant.startswith("environment"):
        core_message = (
            f"Your simulation results show that the current trajectory is primarily "
            f"influenced by environmental and lifestyle factors, not genetic background alone. "
            f"This is actually good news — it means there is significant room for improvement "
            f"through lifestyle modifications. "
        )
    elif dominant.startswith("genetic"):
        core_message = (
            f"Your simulation suggests that genetic background contributes substantially "
            f"to the current trajectory. However, this does NOT mean the outcome is predetermined. "
            f"Gene-environment interactions mean that lifestyle choices can still significantly "
            f"shift the trajectory — genes provide tendencies, not certainties. "
        )
    else:
        core_message = (
            f"Your simulation highlights the interaction between genes and environment as the "
            f"primary driver. This means personalized lifestyle strategies — tailored to your "
            f"specific genetic profile — may be particularly effective. "
        )

    # 反事实信息
    counterfactual_message = ""
    if counterfactual:
        diff = counterfactual.get("comparison", {}).get("hti_difference", 0)
        insight = counterfactual.get("comparison", {}).get("key_insight", "")
        if diff > 5:
            counterfactual_message = (
                f" The counterfactual simulation demonstrates this clearly: "
                f"switching to an improved lifestyle scenario shifts the HTI by +{diff} points. "
                f"Same genes, different choices, different trajectory. "
                f"Genes are not destiny."
            )

    # 可修改因素
    mod_message = (
        f" Based on your profile, {modifiable_factor.get('label', 'lifestyle')} "
        f"currently shows the most room for improvement among modifiable factors. "
    )

    return core_message + mod_message + trajectory_note + " " + counterfactual_message


def _build_simulation_scientific_note(
    genetic_profile: dict,
    baseline_hti: int,
    gene_total: float,
    env_total: float,
    interaction_total: float,
) -> str:
    """构建模拟的科学说明。"""
    return (
        f"This simulation is powered by the G×E Health Trajectory Index (HTI) model v2.0. "
        f"The HTI is an educational metric combining genetic background (effect: {gene_total:+.1f}), "
        f"lifestyle environment (effect: {env_total:+.1f}), and gene-environment interaction "
        f"(effect: {interaction_total:+.1f}). "
        f"Parameters are calibrated using GWAS meta-analyses, WHO Global Burden of Disease studies, "
        f"and published G×E interaction research. "
        f"Genes analyzed: {', '.join(genetic_profile.keys())}. "
        f"HTI does not predict disease — it simulates how different factors shape health trends. "
        f"Confidence intervals widen with projection time, reflecting increasing uncertainty."
    )


# =============================================================================
# 5. 工具函数
# =============================================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# =============================================================================
# 6. 独立运行示例
# =============================================================================

if __name__ == "__main__":
    from engine.gxe_model import simulate_health_trajectory
    from engine.counterfactual import compare_scenarios

    print("=" * 70)
    print("AI Interpreter v2.0 — Demo")
    print("=" * 70)

    genetic = {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}
    env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}

    # ── 单基因解释 ──
    print("\n1. Single Gene: APOE")
    r = interpret_gene_info("APOE", "ε3/ε4", "attention")
    print(f"   genetic_story: {r['genetic_story'][:120]}...")
    print(f"   simulation_message: {r['simulation_message'][:120]}...")
    print(f"   confidence: {r['confidence']}")

    # ── 模拟解读 ──
    print("\n2. Simulation Interpretation")
    sim = simulate_health_trajectory(genetic, env)
    improved_env = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
    cf = compare_scenarios(genetic, env, improved_env)
    interp = interpret_simulation_result(sim, genetic, env, cf)

    print(f"   genetic_story: {interp['genetic_story'][:150]}...")
    print(f"   main_driver: {interp['main_driver']['dominant_factor']}")
    print(f"   modifiable_factor: {interp['modifiable_factor']['factor']}")
    print(f"   simulation_message: {interp['simulation_message'][:200]}...")
    print(f"   disclaimer present: {'IMPORTANT' in interp['disclaimer']}")

    # ── 全基因覆盖 ──
    print("\n3. Full Gene Coverage:")
    for g in ["APOE", "FTO", "CLOCK", "ACTN3"]:
        r = interpret_gene_info(g)
        confidence = r.get("confidence", {})
        print(f"   {g}: evidence={confidence.get('genetic_evidence', '?')}, "
              f"domain={r.get('gene_info', {}).get('health_domain', '?')[:40]}")

    print(f"\n{'=' * 70}")
    print("Demo complete.")
    print(f"{'=' * 70}")
