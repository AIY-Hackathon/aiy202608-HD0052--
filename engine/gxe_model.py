# =============================================================================
# engine/gxe_model.py — G×E Health Trajectory Index (HTI) 模拟引擎
# =============================================================================
#
# 核心概念：Health Trajectory Index (HTI)
#   HTI 是一个教育性模拟指标，展示：
#     Genetic Background + Lifestyle Environment + G×E Interaction
#     如何共同影响长期健康趋势。
#
#   本系统不预测疾病，不提供临床诊断。
#   Genes are not destiny.
#
# 主入口：simulate_health_trajectory()
# 协作接口：calculate_gxe()
#
# 模型原理（四因子）：
#   HTI = Baseline + Gene_Effect + Environment_Effect + G×E_Interaction
#   轨迹 = HTI - Time_Decay(基因时间风险 × 环境放大 × 年数)
# =============================================================================
from __future__ import annotations

import math
from typing import Any

from engine.config import (
    COUNTERFACTUAL_CONFIG,
    DIMENSION_CONFIG,
    ENVIRONMENT_RANGES,
    ENVIRONMENT_WEIGHTS,
    GENE_WEIGHTS,
    INTERACTION_COEFFICIENTS,
    SIMULATION_CONFIG,
    TREND_LEVEL_THRESHOLDS,
)


# =============================================================================
# 1. 核心模拟函数
# =============================================================================

def simulate_health_trajectory(
    genetic_profile: dict[str, float],
    environment: dict[str, float],
    time_horizons: list[int] | None = None,
) -> dict[str, Any]:
    """模拟 G×E 健康趋势轨迹（HTI） —— Part C 主入口。

    参数:
        genetic_profile: 基因变异的 sensitivity 值字典
            例：{"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}
            范围 0-1：0=低 sensitivity，1=高 sensitivity
        environment: 环境因素字典
            例：{"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 0}
        time_horizons: 模拟时间点（年），默认 [5, 10, 20]

    返回:
        {
            "baseline_hti": int,              # 当前 HTI (0-100)
            "trajectory": [                   # 时间轨迹
                {"year": 5, "hti": 43, "trend": "moderate", "confidence": [lo, hi]},
                ...
            ],
            "dimension_scores": {...},        # 5 维度评分
            "factor_analysis": [...],         # 因素贡献分解（可解释性）
            "summary": {                      # 效应汇总
                "gene_effect": float,
                "environment_effect": float,
                "interaction_effect": float,
            },
        }
    """
    # ── 0. 输入校验与标准化 ──
    genetic_profile = _validate_genetic_profile(genetic_profile)
    environment = _validate_environment(environment)
    if time_horizons is None:
        time_horizons = SIMULATION_CONFIG["time_horizons"]

    # ── 1. 基因主效应 ──
    gene_effects = _compute_gene_effects(genetic_profile)
    gene_total = sum(gene_effects.values())

    # ── 2. 环境主效应 ──
    env_effects = _compute_environment_effects(environment)
    env_total = sum(env_effects.values())

    # ── 3. G×E 交互效应 ──
    interaction_effects = _compute_interaction_effects(genetic_profile, environment)
    interaction_total = sum(interaction_effects.values())

    # ── 4. 综合 HTI ──
    baseline_hti = _compute_baseline_hti(gene_total, env_total, interaction_total)

    # ── 5. 时间轨迹 ──
    trajectory = _compute_trajectory(
        genetic_profile, environment, baseline_hti, time_horizons
    )

    # ── 6. 维度评分 ──
    dimension_scores = _compute_dimension_scores(genetic_profile, environment)

    # ── 7. 因素分析（可解释性） ──
    factor_analysis_list = _generate_factor_analysis(
        genetic_profile, environment, gene_effects, env_effects, interaction_effects
    )

    return {
        "baseline_hti": baseline_hti,
        "trajectory": trajectory,
        "dimension_scores": dimension_scores,
        "factor_analysis": factor_analysis_list,
        "summary": {
            "gene_effect": round(gene_total, 2),
            "environment_effect": round(env_total, 2),
            "interaction_effect": round(interaction_total, 2),
        },
    }


# =============================================================================
# 2. 基因主效应
# =============================================================================

def _compute_gene_effects(profile: dict[str, float]) -> dict[str, float]:
    """计算每个基因的 HTI 贡献。

    效应 = sensitivity × 维度平均权重 × 基础效应量 × 100
    """
    effects: dict[str, float] = {}
    for gene, sensitivity in profile.items():
        gw = GENE_WEIGHTS.get(gene)
        if gw is None:
            continue
        dim_weights = [
            gw.get("cognitive", 0),
            gw.get("metabolic", 0),
            gw.get("cardiovascular", 0),
            gw.get("athletic", 0),
            gw.get("sleep", 0),
        ]
        active_dims = [w for w in dim_weights if w > 0]
        avg_dim_weight = sum(active_dims) / max(1, len(active_dims))
        base = gw.get("base_effect", 0.20)
        effect = sensitivity * avg_dim_weight * base * 100
        effects[gene] = round(effect, 2)
    return effects


# =============================================================================
# 3. 环境主效应
# =============================================================================

def _compute_environment_effects(environment: dict[str, float]) -> dict[str, float]:
    """计算每个环境因素对 HTI 的贡献。

    正向因素（运动、睡眠、饮食）：值越高 → 贡献越正
    反向因素（压力、吸烟）：用差值模型，值越高 → 贡献越负
    """
    effects: dict[str, float] = {}
    for factor, value in environment.items():
        ew = ENVIRONMENT_WEIGHTS.get(factor)
        ranges = ENVIRONMENT_RANGES.get(factor)
        if ew is None or ranges is None:
            continue
        optimal = ranges["optimal"]
        if factor in ("stress", "smoking"):
            deviation = (optimal - value) / max(ranges["max"] - ranges["min"], 1)
        else:
            deviation = (value - optimal) / max(ranges["max"] - ranges["min"], 1)
        overall_w = ew.get("overall_health", 0.20)
        effect = deviation * overall_w * 100
        effects[factor] = round(effect, 2)
    return effects


# =============================================================================
# 4. G×E 交互效应
# =============================================================================

def _compute_interaction_effects(
    genetic_profile: dict[str, float],
    environment: dict[str, float],
) -> dict[str, float]:
    """计算基因×环境交互效应。

    交互效应 = sensitivity × 环境偏离程度 × 交互系数 × 50
    """
    effects: dict[str, float] = {}
    for gene, sensitivity in genetic_profile.items():
        ic = INTERACTION_COEFFICIENTS.get(gene)
        if ic is None:
            continue
        for env_factor, env_value in environment.items():
            coef = ic.get(env_factor, 0)
            if abs(coef) < 0.001:
                continue
            ranges = ENVIRONMENT_RANGES.get(env_factor)
            if ranges is None:
                continue
            optimal = ranges["optimal"]
            env_deviation = (env_value - optimal) / max(ranges["max"] - ranges["min"], 1)
            interaction = sensitivity * env_deviation * coef * 50
            effects[f"{gene}×{env_factor}"] = round(interaction, 2)
    return effects


# =============================================================================
# 5. HTI 计算
# =============================================================================

def _compute_baseline_hti(gene_total: float, env_total: float, interaction_total: float) -> int:
    """综合基因、环境、交互效应计算 HTI。

    HTI = 基线值 + 基因效应(≤±40) + 环境效应(≤±60) + 交互效应(±15)
    """
    base = SIMULATION_CONFIG["baseline_hti"]
    gene_ceil = SIMULATION_CONFIG["gene_relative_weight_ceiling"]
    env_ceil = SIMULATION_CONFIG["environment_relative_weight_ceiling"]
    inter_min, inter_max = SIMULATION_CONFIG["interaction_contribution_range"]

    gene_clipped = max(-gene_ceil * 100, min(gene_ceil * 100, gene_total))
    env_clipped = max(-env_ceil * 100, min(env_ceil * 100, env_total))
    inter_clipped = max(inter_min * 100, min(inter_max * 100, interaction_total))

    score = base + gene_clipped + env_clipped + inter_clipped
    return max(SIMULATION_CONFIG["min_hti"], min(SIMULATION_CONFIG["max_hti"], int(round(score))))


# =============================================================================
# 6. 时间轨迹
# =============================================================================

def _compute_trajectory(
    genetic_profile: dict[str, float],
    environment: dict[str, float],
    baseline_hti: int,
    time_horizons: list[int],
) -> list[dict]:
    """计算未来时间点的 HTI 轨迹。

    轨迹 = 基线 HTI - 时间累积趋势变化

    衰减速率 = 自然趋势变化(0.5/年) × (1 + 基因累积趋势) × 环境放大系数
    环境越好 → buffer 越强 → 趋势衰减越慢
    """
    trajectory = []

    gene_time_risk = 0.0
    for gene, sensitivity in genetic_profile.items():
        gw = GENE_WEIGHTS.get(gene)
        if gw is None:
            continue
        gene_time_risk += sensitivity * (gw.get("time_multiplier", 1.0) - 1.0)

    env_buffer = _compute_environment_buffer(environment)
    env_amplifier = 1.0 + (1.0 - env_buffer) * 1.5

    base_annual_decay = SIMULATION_CONFIG["base_annual_decay"]
    ci_half = SIMULATION_CONFIG["confidence_interval_range"]
    min_s = SIMULATION_CONFIG["min_hti"]
    max_s = SIMULATION_CONFIG["max_hti"]

    for year in time_horizons:
        annual_decay_rate = base_annual_decay * (1.0 + gene_time_risk) * env_amplifier
        total_decay = annual_decay_rate * year
        recovery = env_buffer * total_decay * 0.25
        net_decay = total_decay - recovery

        hti = baseline_hti - net_decay
        hti_clamped = max(min_s, min(max_s, int(round(hti))))
        trend = _hti_to_trend_level(hti_clamped)

        year_ci = ci_half + year * 0.004
        trajectory.append({
            "year": year,
            "hti": hti_clamped,
            "trend": trend,
            "confidence": [
                round(max(min_s, hti_clamped - hti_clamped * year_ci), 1),
                round(min(max_s, hti_clamped + hti_clamped * year_ci), 1),
            ],
        })

    return trajectory


def _compute_environment_buffer(environment: dict[str, float]) -> float:
    """计算环境缓冲能力 [0, 1]。

    1 = 理想环境（最大缓冲，趋势衰减最慢）
    0 = 最差环境（无缓冲，趋势衰减最快）
    """
    total = 0.0
    count = 0
    for factor, value in environment.items():
        ranges = ENVIRONMENT_RANGES.get(factor)
        if ranges is None:
            continue
        if factor in ("stress", "smoking"):
            normalized = 1 - value / max(ranges["max"], 1)
        else:
            normalized = value / max(ranges["max"], 1)
        total += normalized
        count += 1
    return total / max(count, 1) if count > 0 else 0.5


# =============================================================================
# 7. 维度评分
# =============================================================================

def _compute_dimension_scores(
    genetic_profile: dict[str, float],
    environment: dict[str, float],
) -> dict[str, dict]:
    """计算 5 个健康维度的 HTI 子评分。

    维度分 = 基线 + 基因贡献 + 环境贡献 + 交互修正
    """
    results = {}
    for dim_key, dim_config in DIMENSION_CONFIG.items():
        baseline = dim_config["baseline"]

        # 基因贡献
        gene_contrib = 0.0
        for gene, sensitivity in genetic_profile.items():
            gw = GENE_WEIGHTS.get(gene)
            if gw is None:
                continue
            dim_w = gw.get(dim_key, 0)
            gene_contrib += (sensitivity * 100 - 30) * dim_w

        # 环境贡献
        env_contrib = 0.0
        for factor, value in environment.items():
            ew = ENVIRONMENT_WEIGHTS.get(factor)
            ranges = ENVIRONMENT_RANGES.get(factor)
            if ew is None or ranges is None:
                continue
            dim_w = ew.get(dim_key, 0)
            if factor in ("stress", "smoking"):
                normalized = (ranges["optimal"] - value) / max(ranges["max"], 1)
            else:
                normalized = (value - ranges["optimal"]) / max(ranges["max"], 1)
            env_contrib += normalized * dim_w * 100

        # 交互修正
        interaction_contrib = 0.0
        for gene, sensitivity in genetic_profile.items():
            ic = INTERACTION_COEFFICIENTS.get(gene)
            if ic is None:
                continue
            for factor, value in environment.items():
                coef = ic.get(factor, 0)
                if abs(coef) < 0.001:
                    continue
                ranges = ENVIRONMENT_RANGES.get(factor)
                if ranges is None:
                    continue
                if factor in ("stress", "smoking"):
                    env_dev = (ranges["optimal"] - value) / max(ranges["max"], 1)
                else:
                    env_dev = (value - ranges["optimal"]) / max(ranges["max"], 1)
                interaction_contrib += sensitivity * env_dev * coef * 30

        score = int(round(baseline + gene_contrib + env_contrib + interaction_contrib))
        score = max(5, min(95, score))
        trend = _hti_to_trend_level(score)

        results[dim_key] = {
            "key": dim_key,
            "label": dim_config["label"],
            "icon": dim_config["icon"],
            "score": score,
            "trend": trend,
            "description": dim_config["description"],
            "gene_contribution": round(gene_contrib, 1),
            "environment_contribution": round(env_contrib, 1),
            "interaction_contribution": round(interaction_contrib, 1),
        }
    return results


# =============================================================================
# 8. 因素分析（可解释性）
# =============================================================================

def _generate_factor_analysis(
    genetic_profile: dict[str, float],
    environment: dict[str, float],
    gene_effects: dict[str, float],
    env_effects: dict[str, float],
    interaction_effects: dict[str, float],
) -> list[dict]:
    """生成因素贡献分解。

    每个条目:
      - factor: 因素名
      - category: gene / environment / interaction
      - contribution: HTI 贡献值（正=有利，负=需关注）
      - magnitude: small / medium / large
      - description: 中文解释
    """
    analysis = []

    for gene, effect in gene_effects.items():
        gw = GENE_WEIGHTS.get(gene, {})
        sensitivity = genetic_profile.get(gene, 0)
        magnitude = _effect_magnitude(abs(effect))
        direction = "higher sensitivity" if sensitivity > 0.5 else "moderate or lower sensitivity"
        analysis.append({
            "factor": f"Genetic: {gene}",
            "category": "gene",
            "contribution": round(effect, 2),
            "magnitude": magnitude,
            "description": (
                f"{gene} ({gw.get('description', 'no description')}) "
                f"shows {direction} (sensitivity={sensitivity:.1f}), "
                f"contributing {effect:+.1f} to HTI."
            ),
        })

    for factor, effect in env_effects.items():
        ew = ENVIRONMENT_WEIGHTS.get(factor, {})
        magnitude = _effect_magnitude(abs(effect))
        direction = "favorable" if effect > 0 else "needs attention"
        analysis.append({
            "factor": f"Environment: {factor}",
            "category": "environment",
            "contribution": round(effect, 2),
            "magnitude": magnitude,
            "description": (
                f"{factor} ({ew.get('description', 'no description')}) "
                f"is {direction} with contribution {effect:+.1f}."
            ),
        })

    for combo, effect in interaction_effects.items():
        if abs(effect) < 1.0:
            continue
        magnitude = _effect_magnitude(abs(effect))
        direction = "synergistic benefit" if effect > 0 else "amplified concern"
        analysis.append({
            "factor": f"G×E: {combo}",
            "category": "interaction",
            "contribution": round(effect, 2),
            "magnitude": magnitude,
            "description": f"Gene-environment pair {combo} shows {direction}, contributing {effect:+.1f}.",
        })

    return analysis


def _effect_magnitude(value: float) -> str:
    if abs(value) > 15:
        return "large"
    if abs(value) > 5:
        return "medium"
    return "small"


# =============================================================================
# 9. 校验函数
# =============================================================================

def _validate_genetic_profile(profile: dict[str, float]) -> dict[str, float]:
    validated = {}
    for gene in GENE_WEIGHTS:
        value = profile.get(gene, 0.3)
        validated[gene] = max(0.0, min(1.0, float(value)))
    return validated


def _validate_environment(env: dict[str, float]) -> dict[str, float]:
    validated = {}
    for factor, ranges in ENVIRONMENT_RANGES.items():
        value = env.get(factor, ranges["optimal"])
        validated[factor] = max(ranges["min"], min(ranges["max"], float(value)))
    return validated


def _hti_to_trend_level(hti: float) -> str:
    # HTI 越高 = 越有利，所以用 100 - hti 映射到阈值
    inverse = 100 - hti
    for level, (lo, hi) in TREND_LEVEL_THRESHOLDS.items():
        if lo <= inverse < hi:
            return level
    return "moderate"


# =============================================================================
# 10. 协作接口
# =============================================================================

def calculate_gxe(
    genetic_profile: dict[str, float],
    environmental_factors: dict[str, float],
) -> dict:
    """协作接口（对齐 design.md §7.3），供 backend/api/simulate.py 调用。"""
    result = simulate_health_trajectory(genetic_profile, environmental_factors)

    return {
        "trajectory": [
            {"year": t["year"], "hti": t["hti"], "trend": t["trend"]}
            for t in result["trajectory"]
        ],
        "confidence": {
            f"year_{t['year']}": t["confidence"] for t in result["trajectory"]
        },
        "baseline_hti": result["baseline_hti"],
        "dimension_scores": result["dimension_scores"],
        "factor_analysis": result["factor_analysis"],
        "summary": result["summary"],
    }


# =============================================================================
# 11. 运行示例
# =============================================================================

if __name__ == "__main__":
    sample_genetic = {
        "APOE": 0.7,
        "FTO": 0.5,
        "CLOCK": 0.3,
        "ACTN3": 0.4,
    }

    scenarios = {
        "Ideal Lifestyle": {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0},
        "Average Lifestyle": {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2},
        "Poor Lifestyle": {"exercise": 2, "sleep": 5, "diet": 3, "stress": 8, "smoking": 6},
    }

    print("=" * 70)
    print("G×E Health Trajectory Index (HTI) Engine — Demo")
    print("=" * 70)

    for name, env in scenarios.items():
        result = simulate_health_trajectory(sample_genetic, env)
        print(f"\n{'─' * 50}")
        print(f"Scenario: {name}")
        print(f"{'─' * 50}")
        print(f"  Baseline HTI: {result['baseline_hti']}")
        print(f"  Gene Effect: {result['summary']['gene_effect']:+.1f}")
        print(f"  Environment Effect: {result['summary']['environment_effect']:+.1f}")
        print(f"  G×E Interaction: {result['summary']['interaction_effect']:+.1f}")
        print(f"  Trajectory:")
        for t in result["trajectory"]:
            print(f"    Year {t['year']:2d}: HTI={t['hti']:3d} ({t['trend']}), "
                  f"CI [{t['confidence'][0]:.0f}, {t['confidence'][1]:.0f}]")
        print(f"  Dimensions:")
        for key, dim in result["dimension_scores"].items():
            print(f"    {dim['icon']} {dim['label']}: {dim['score']} ({dim['trend']})")

    print(f"\n{'=' * 70}")
    print("Demo complete.")
    print(f"{'=' * 70}")
