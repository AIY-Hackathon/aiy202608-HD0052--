# =============================================================================
# engine/counterfactual.py — Counterfactual Health Simulation
# =============================================================================
#
# 核心功能：
#   "What if I changed my lifestyle?" — 保持相同遗传背景，
#   只改变一个环境因素，重新模拟 HTI 变化。
#
# 设计理念：
#   基因提供潜在倾向，环境因素决定可改变空间。
#   Genes are not destiny.
#
# 主入口：
#   simulate_counterfactual()         — 单因素反事实模拟
#   compare_scenarios()               — 多场景对比（比赛核心 Demo）
#   explore_what_if_all_factors()     — 探索所有可改变因素的影响
# =============================================================================
from __future__ import annotations

from typing import Any

from engine.config import (
    COUNTERFACTUAL_CONFIG,
    ENVIRONMENT_RANGES,
)
from engine.gxe_model import simulate_health_trajectory


# =============================================================================
# 1. 单因素反事实模拟
# =============================================================================

def simulate_counterfactual(
    genetic_profile: dict[str, float],
    current_environment: dict[str, float],
    changed_factor: str,
    new_value: float,
) -> dict[str, Any]:
    """What-if 模拟：只改变一个环境因素，重新计算 HTI。

    参数:
        genetic_profile: 基因 sensitivity 值
        current_environment: 当前环境因素
        changed_factor: 要改变的环境因素 (exercise/sleep/diet/stress)
        new_value: 该因素的新值 (0-10)

    返回:
        {
            "changed_factor": "exercise",
            "baseline_hti": 47,      # 当前 HTI
            "new_hti": 63,            # 改变后的 HTI
            "change": +16,            # HTI 变化量
            "direction": "improved",  # improved / declined / unchanged
            "baseline_trajectory": [...],
            "new_trajectory": [...],
            "explanation": "...",
        }
    """
    # 校验
    if changed_factor not in COUNTERFACTUAL_CONFIG["changeable_factors"]:
        return {
            "error": f"Factor '{changed_factor}' is not changeable. "
                     f"Changeable factors: {COUNTERFACTUAL_CONFIG['changeable_factors']}"
        }

    ranges = ENVIRONMENT_RANGES.get(changed_factor, {})
    if not ranges:
        return {"error": f"Unknown factor: {changed_factor}"}

    clamped = max(ranges["min"], min(ranges["max"], float(new_value)))

    # ── 当前场景 ──
    baseline_result = simulate_health_trajectory(genetic_profile, current_environment)

    # ── 反事实场景（只改一个因素） ──
    new_environment = dict(current_environment)
    new_environment[changed_factor] = clamped
    new_result = simulate_health_trajectory(genetic_profile, new_environment)

    hti_current = baseline_result["baseline_hti"]
    hti_new = new_result["baseline_hti"]
    change = hti_new - hti_current

    # 方向判断
    if change > COUNTERFACTUAL_CONFIG["min_meaningful_change"]:
        direction = "improved"
    elif change < -COUNTERFACTUAL_CONFIG["min_meaningful_change"]:
        direction = "declined"
    else:
        direction = "unchanged"

    # 构造解释
    explanation = _build_counterfactual_explanation(
        changed_factor, current_environment, clamped, change, hti_current, hti_new,
        baseline_result["summary"], new_result["summary"]
    )

    return {
        "changed_factor": changed_factor,
        "baseline_hti": hti_current,
        "new_hti": hti_new,
        "change": change,
        "direction": direction,
        "baseline_trajectory": [
            {"year": t["year"], "hti": t["hti"], "trend": t["trend"]}
            for t in baseline_result["trajectory"]
        ],
        "new_trajectory": [
            {"year": t["year"], "hti": t["hti"], "trend": t["trend"]}
            for t in new_result["trajectory"]
        ],
        "explanation": explanation,
        "baseline_summary": baseline_result["summary"],
        "new_summary": new_result["summary"],
    }


# =============================================================================
# 2. 场景对比（比赛核心 Demo）
# =============================================================================

def compare_scenarios(
    genetic_profile: dict[str, float],
    scenario_a: dict[str, float],
    scenario_b: dict[str, float],
    label_a: str = "Current Lifestyle",
    label_b: str = "Improved Lifestyle",
) -> dict[str, Any]:
    """比较两个完整环境场景的 HTI 轨迹。

    核心卖点：
      同样的基因背景，不同的环境选择 → 不同的健康趋势。
      Genes are not destiny.

    返回:
        {
            "genetic_profile": {...},
            "scenario_a": {"label": "Current Lifestyle", "baseline_hti": 47, "trajectory": [...]},
            "scenario_b": {"label": "Improved Lifestyle", "baseline_hti": 63, "trajectory": [...]},
            "comparison": {
                "hti_difference": +16,
                "trajectory_divergence": [...],  # 每个时间点的 HTI 差异
                "key_insight": "...",
            },
        }
    """
    result_a = simulate_health_trajectory(genetic_profile, scenario_a)
    result_b = simulate_health_trajectory(genetic_profile, scenario_b)

    hti_diff = result_b["baseline_hti"] - result_a["baseline_hti"]

    # 轨迹差异
    traj_divergence = []
    for ta, tb in zip(result_a["trajectory"], result_b["trajectory"]):
        traj_divergence.append({
            "year": ta["year"],
            "scenario_a_hti": ta["hti"],
            "scenario_b_hti": tb["hti"],
            "difference": tb["hti"] - ta["hti"],
        })

    # 解释
    if hti_diff > COUNTERFACTUAL_CONFIG["significant_change_threshold"]:
        insight = (
            f"Switching from '{label_a}' to '{label_b}' shows a significant HTI improvement "
            f"of +{hti_diff} points. With the same genetic profile, the improved lifestyle "
            f"reshapes the health trajectory — environmental choices matter."
        )
    elif hti_diff > COUNTERFACTUAL_CONFIG["min_meaningful_change"]:
        insight = (
            f"The lifestyle change from '{label_a}' to '{label_b}' produces a measurable "
            f"HTI shift of +{hti_diff} points. Even moderate changes compound over time."
        )
    elif hti_diff < 0:
        insight = (
            f"The scenario '{label_b}' shows a lower HTI than '{label_a}'. "
            f"This demonstrates that not all changes are beneficial — "
            f"some lifestyle shifts may negatively affect the simulated trajectory."
        )
    else:
        insight = (
            f"The two scenarios produce similar HTI estimates. "
            f"This could mean the lifestyle differences are too subtle to differentiate, "
            f"or the genetic profile is relatively robust to these specific changes."
        )

    return {
        "genetic_profile": genetic_profile,
        "scenario_a": {
            "label": label_a,
            "baseline_hti": result_a["baseline_hti"],
            "trajectory": [
                {"year": t["year"], "hti": t["hti"], "trend": t["trend"]}
                for t in result_a["trajectory"]
            ],
            "summary": result_a["summary"],
        },
        "scenario_b": {
            "label": label_b,
            "baseline_hti": result_b["baseline_hti"],
            "trajectory": [
                {"year": t["year"], "hti": t["hti"], "trend": t["trend"]}
                for t in result_b["trajectory"]
            ],
            "summary": result_b["summary"],
        },
        "comparison": {
            "hti_difference": hti_diff,
            "trajectory_divergence": traj_divergence,
            "key_insight": insight,
        },
    }


# =============================================================================
# 3. 探索所有可改变因素
# =============================================================================

def explore_what_if_all_factors(
    genetic_profile: dict[str, float],
    current_environment: dict[str, float],
    target_value: float = 8.0,
) -> list[dict[str, Any]]:
    """对每个可改变因素分别做反事实模拟，找出最具影响力的因素。

    返回: 按 HTI 改善幅度降序排列的模拟结果列表
    """
    results = []
    for factor in COUNTERFACTUAL_CONFIG["changeable_factors"]:
        sim = simulate_counterfactual(
            genetic_profile, current_environment, factor, target_value
        )
        if "error" not in sim:
            results.append(sim)

    results.sort(key=lambda r: r["change"], reverse=True)
    return results


# =============================================================================
# 4. 解释生成
# =============================================================================

def _build_counterfactual_explanation(
    factor: str,
    current_env: dict[str, float],
    new_value: float,
    change: int,
    hti_current: int,
    hti_new: int,
    current_summary: dict,
    new_summary: dict,
) -> str:
    """生成反事实模拟的英文解释。"""
    ranges = ENVIRONMENT_RANGES.get(factor, {})
    factor_label = ranges.get("label", factor)
    old_value = current_env.get(factor, 0)
    optimal = ranges.get("optimal", 7)

    env_effect_change = new_summary["environment_effect"] - current_summary["environment_effect"]

    if change > COUNTERFACTUAL_CONFIG["significant_change_threshold"]:
        return (
            f"Changing {factor_label} from {old_value} to {new_value} (optimal: {optimal}) "
            f"significantly shifts the simulated HTI from {hti_current} to {hti_new} (+{change}). "
            f"The environmental contribution improved by {env_effect_change:+.1f} points. "
            f"This suggests {factor_label.lower()} may be a high-impact modifiable factor "
            f"for this genetic profile."
        )
    elif change > COUNTERFACTUAL_CONFIG["min_meaningful_change"]:
        return (
            f"Improving {factor_label} from {old_value} to {new_value} "
            f"raises the simulated HTI from {hti_current} to {hti_new} (+{change}). "
            f"Environmental contribution changed by {env_effect_change:+.1f}. "
            f"This is a meaningful but moderate shift."
        )
    elif change < -COUNTERFACTUAL_CONFIG["min_meaningful_change"]:
        return (
            f"Changing {factor_label} from {old_value} to {new_value} "
            f"decreases the simulated HTI from {hti_current} to {hti_new} ({change}). "
            f"This may indicate that the new value is less optimal than the current one."
        )
    else:
        return (
            f"Changing {factor_label} from {old_value} to {new_value} "
            f"produces minimal change in the simulated HTI ({change:+}). "
            f"The current level may already be near-optimal for this profile, "
            f"or this factor has limited interaction with the genetic background."
        )


# =============================================================================
# 5. 运行示例
# =============================================================================

if __name__ == "__main__":
    genetic = {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}

    current_env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
    improved_env = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}

    print("=" * 70)
    print("Counterfactual Health Simulation — Demo")
    print("Genes are not destiny.")
    print("=" * 70)

    # ── Demo 1: 单因素反事实 ──
    print("\n1. Single-factor 'What-If': Exercise 2 → 8")
    result = simulate_counterfactual(genetic, current_env, "exercise", 8)
    print(f"   {result['changed_factor']}: HTI {result['baseline_hti']} → {result['new_hti']} "
          f"({result['change']:+d}, {result['direction']})")
    print(f"   {result['explanation']}")

    print("\n2. Single-factor 'What-If': Sleep 5 → 8")
    result = simulate_counterfactual(genetic, current_env, "sleep", 8)
    print(f"   {result['changed_factor']}: HTI {result['baseline_hti']} → {result['new_hti']} "
          f"({result['change']:+d}, {result['direction']})")

    print("\n3. Single-factor 'What-If': Diet 4 → 8")
    result = simulate_counterfactual(genetic, current_env, "diet", 8)
    print(f"   {result['changed_factor']}: HTI {result['baseline_hti']} → {result['new_hti']} "
          f"({result['change']:+d}, {result['direction']})")

    print("\n4. Single-factor 'What-If': Stress 7 → 2")
    result = simulate_counterfactual(genetic, current_env, "stress", 2)
    print(f"   {result['changed_factor']}: HTI {result['baseline_hti']} → {result['new_hti']} "
          f"({result['change']:+d}, {result['direction']})")

    # ── Demo 2: 场景对比（比赛核心 Demo） ──
    print(f"\n{'─' * 50}")
    print("\n5. Scenario Comparison: Current vs Improved Lifestyle")
    print("   (Same genetic profile, different environment choices)")
    comparison = compare_scenarios(genetic, current_env, improved_env)
    print(f"\n   {comparison['scenario_a']['label']}: baseline HTI={comparison['scenario_a']['baseline_hti']}")
    for t in comparison['scenario_a']['trajectory']:
        print(f"     Year {t['year']:2d}: HTI={t['hti']:3d} ({t['trend']})")
    print(f"\n   {comparison['scenario_b']['label']}: baseline HTI={comparison['scenario_b']['baseline_hti']}")
    for t in comparison['scenario_b']['trajectory']:
        print(f"     Year {t['year']:2d}: HTI={t['hti']:3d} ({t['trend']})")
    print(f"\n   HTI Difference: {comparison['comparison']['hti_difference']:+d}")
    print(f"   Trajectory Divergence:")
    for d in comparison['comparison']['trajectory_divergence']:
        print(f"     Year {d['year']:2d}: Δ={d['difference']:+d} HTI")
    print(f"\n   Key Insight: {comparison['comparison']['key_insight']}")

    # ── Demo 3: 探索所有因素 ──
    print(f"\n{'─' * 50}")
    print("\n6. Exploring all modifiable factors (→ target=8)")
    all_results = explore_what_if_all_factors(genetic, current_env)
    print("   Ranked by HTI impact:")
    for i, r in enumerate(all_results, 1):
        print(f"   {i}. {r['changed_factor']:10s}: {r['change']:+3d} HTI ({r['direction']})")

    print(f"\n{'=' * 70}")
    print("Demo complete.")
    print(f"{'=' * 70}")
