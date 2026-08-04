# =============================================================================
# 引擎单元测试 — Part C v2.0 (HTI + Counterfactual + AI + Recommendations)
# =============================================================================
"""Part C 引擎测试。运行：python -m pytest engine/tests/test_gxe.py -v"""

from __future__ import annotations

import json
from pathlib import Path

import pytest as pytest

from engine.ai_interpreter import interpret_gene_info, interpret_simulation_result
from engine.counterfactual import (
    compare_scenarios,
    explore_what_if_all_factors,
    simulate_counterfactual,
)
from engine.gxe_model import calculate_gxe, simulate_health_trajectory
from engine.recommendation_engine import generate, generate_from_simulation

SAMPLE_GENETIC = {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}


# =============================================================================
# G×E 模型测试
# =============================================================================


class TestGxEModel:
    """G×E HTI 模拟引擎。"""

    def test_baseline_hti_range(self):
        env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        result = simulate_health_trajectory(SAMPLE_GENETIC, env)
        assert 20 <= result["baseline_hti"] <= 95

    def test_environment_effect_direction(self):
        env_good = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
        env_bad = {"exercise": 2, "sleep": 5, "diet": 3, "stress": 8, "smoking": 6}
        r_good = simulate_health_trajectory(SAMPLE_GENETIC, env_good)
        r_bad = simulate_health_trajectory(SAMPLE_GENETIC, env_bad)
        assert r_good["baseline_hti"] > r_bad["baseline_hti"]

    def test_trajectory_has_all_time_points(self):
        result = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        years = [t["year"] for t in result["trajectory"]]
        assert years == [5, 10, 20]

    def test_trajectory_monotonic_decay_in_bad_env(self):
        env_bad = {"exercise": 2, "sleep": 5, "diet": 3, "stress": 8, "smoking": 6}
        result = simulate_health_trajectory(SAMPLE_GENETIC, env_bad)
        hti_values = [t["hti"] for t in result["trajectory"]]
        for i in range(1, len(hti_values)):
            assert hti_values[i] <= hti_values[i - 1] + 5

    def test_different_environments_change_factor_analysis(self):
        env1 = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
        env2 = {"exercise": 2, "sleep": 5, "diet": 3, "stress": 8, "smoking": 6}
        r1 = simulate_health_trajectory(SAMPLE_GENETIC, env1)
        r2 = simulate_health_trajectory(SAMPLE_GENETIC, env2)
        assert r1["summary"]["environment_effect"] > r2["summary"]["environment_effect"]

    def test_empty_genetic_profile(self):
        result = simulate_health_trajectory(
            {}, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        assert 20 <= result["baseline_hti"] <= 95

    def test_out_of_range_environment_clamping(self):
        env = {"exercise": 99, "sleep": -5, "diet": 5, "stress": 5, "smoking": 0}
        result = simulate_health_trajectory(SAMPLE_GENETIC, env)
        assert 20 <= result["baseline_hti"] <= 95

    def test_factor_analysis_completeness(self):
        result = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        categories = {fa["category"] for fa in result["factor_analysis"]}
        assert "gene" in categories
        assert "environment" in categories

    def test_calculate_gxe_collaboration_interface(self):
        result = calculate_gxe(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        assert "trajectory" in result
        assert "confidence" in result
        assert "baseline_hti" in result
        assert "dimension_scores" in result
        assert "factor_analysis" in result
        assert "summary" in result

    def test_hti_naming_consistency(self):
        """验证所有输出使用 HTI 命名而非 Health Score。"""
        result = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        assert "baseline_hti" in result
        assert "hti" in result["trajectory"][0]
        assert "trend" in result["trajectory"][0]


# =============================================================================
# 反事实模拟测试
# =============================================================================


class TestCounterfactual:
    """反事实 What-If 模拟。"""

    def test_single_factor_counterfactual(self):
        env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        result = simulate_counterfactual(SAMPLE_GENETIC, env, "exercise", 8)
        assert "error" not in result
        assert result["changed_factor"] == "exercise"
        assert result["change"] > 0
        assert "baseline_hti" in result
        assert "new_hti" in result

    def test_counterfactual_direction_improved(self):
        env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        result = simulate_counterfactual(SAMPLE_GENETIC, env, "exercise", 8)
        assert result["direction"] == "improved"

    def test_counterfactual_unchanged(self):
        env = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
        result = simulate_counterfactual(SAMPLE_GENETIC, env, "sleep", 8)
        assert result["direction"] in ("improved", "unchanged")

    def test_counterfactual_all_changeable_factors(self):
        env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        for factor in ["exercise", "sleep", "diet", "stress"]:
            result = simulate_counterfactual(SAMPLE_GENETIC, env, factor, 8)
            assert "error" not in result, f"Factor {factor} failed: {result.get('error')}"

    def test_counterfactual_rejects_unchanged_factor(self):
        env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        result = simulate_counterfactual(SAMPLE_GENETIC, env, "nonexistent", 8)
        assert "error" in result

    def test_scenario_comparison(self):
        env_current = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        env_improved = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
        result = compare_scenarios(SAMPLE_GENETIC, env_current, env_improved)
        assert result["scenario_a"]["baseline_hti"] <= result["scenario_b"]["baseline_hti"]
        assert "comparison" in result
        assert "key_insight" in result["comparison"]
        assert "trajectory_divergence" in result["comparison"]

    def test_explore_all_factors(self):
        env = {"exercise": 2, "sleep": 5, "diet": 4, "stress": 7, "smoking": 4}
        results = explore_what_if_all_factors(SAMPLE_GENETIC, env)
        assert len(results) > 0
        # 第一个应该改善最大
        assert results[0]["change"] >= results[-1]["change"]


# =============================================================================
# AI 解释器测试
# =============================================================================


class TestAIInterpreter:
    """AI 解释器 v2.0。"""

    def test_updated_output_format(self):
        """验证新的 6 字段输出格式。"""
        result = interpret_gene_info("APOE", "ε3/ε4", "attention")
        required_fields = [
            "genetic_story", "main_driver", "modifiable_factor",
            "simulation_message", "scientific_note", "disclaimer"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_confidence_fields(self):
        result = interpret_gene_info("APOE")
        assert "confidence" in result
        confidence = result["confidence"]
        assert "genetic_evidence" in confidence
        assert "interaction_evidence" in confidence
        assert "lifestyle_evidence" in confidence

    def test_disclaimer_present(self):
        r1 = interpret_gene_info("APOE")
        assert "IMPORTANT DISCLAIMER" in r1["disclaimer"]

    def test_no_disease_language(self):
        """验证不包含疾病预测语言。"""
        result = interpret_gene_info("APOE", trend_level="significant")
        output = json.dumps(result, ensure_ascii=False).lower()
        forbidden = ["您患有", "确诊", "会导致", "一定会得"]
        for phrase in forbidden:
            assert phrase not in output, f"Found forbidden phrase: {phrase}"

    def test_simulation_interpretation(self):
        sim = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        env_current = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        env_improved = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}
        cf = compare_scenarios(SAMPLE_GENETIC, env_current, env_improved)
        result = interpret_simulation_result(sim, SAMPLE_GENETIC, env_current, cf)
        assert result["simulation_message"]

    def test_genetic_story_mentions_genes(self):
        sim = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        result = interpret_simulation_result(sim, SAMPLE_GENETIC, {})
        assert any(g in result["genetic_story"] for g in ["APOE", "FTO"])


# =============================================================================
# 建议引擎测试
# =============================================================================


class TestRecommendationEngine:
    """建议引擎 v2.0。"""

    def test_generates_recommendations(self):
        profile = {
            "dimension_scores": {"metabolic": 50, "cognitive": 50, "cardiovascular": 50, "athletic": 50, "sleep": 50},
            "risk_genes": ["APOE", "FTO"],
            "overall_level": "moderate",
        }
        env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        recs = generate(profile, None, env)
        assert len(recs) > 0

    def test_each_recommendation_has_new_fields(self):
        profile = {
            "dimension_scores": {"metabolic": 50, "cognitive": 50, "cardiovascular": 50, "athletic": 50, "sleep": 50},
            "risk_genes": ["APOE"],
            "overall_level": "moderate",
        }
        env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        recs = generate(profile, None, env)
        required = {"trigger_factor", "why_for_this_user", "related_gene", "confidence"}
        for rec in recs:
            missing = required - set(rec.keys())
            assert not missing, f"Missing: {missing}"

    def test_confidence_fields_in_recommendations(self):
        profile = {
            "dimension_scores": {"metabolic": 50, "cognitive": 50, "cardiovascular": 50, "athletic": 50, "sleep": 50},
            "risk_genes": ["APOE"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2})
        for rec in recs:
            conf = rec.get("confidence", {})
            assert "genetic_evidence" in conf
            assert "interaction_evidence" in conf
            assert "lifestyle_evidence" in conf

    def test_not_generic_health_advice(self):
        """验证建议不是'通用健康建议'。"""
        profile = {
            "dimension_scores": {"metabolic": 50, "cognitive": 50, "cardiovascular": 50, "athletic": 50, "sleep": 50},
            "risk_genes": ["APOE", "FTO", "CLOCK", "ACTN3"],
            "overall_level": "moderate",
        }
        env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        recs = generate(profile, None, env)
        for rec in recs:
            assert rec["why_for_this_user"] != ""

    def test_related_gene_not_empty(self):
        profile = {
            "dimension_scores": {"metabolic": 50, "cognitive": 50, "cardiovascular": 50, "athletic": 50, "sleep": 50},
            "risk_genes": ["APOE", "FTO"],
            "overall_level": "moderate",
        }
        env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        recs = generate(profile, None, env)
        for rec in recs:
            assert len(rec.get("related_gene", [])) > 0

    def test_generate_from_simulation(self):
        sim = simulate_health_trajectory(
            SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        recs = generate_from_simulation(
            sim, SAMPLE_GENETIC, {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
        )
        assert len(recs) > 0


# =============================================================================
# 知识库测试
# =============================================================================


class TestGeneDatabase:
    """基因知识库。"""

    def test_database_loadable(self):
        db_path = Path(__file__).parent.parent / "knowledge" / "gene_database.json"
        assert db_path.exists()
        data = json.loads(db_path.read_text(encoding="utf-8"))
        assert len(data["genes"]) == 4

    def test_each_gene_has_confidence(self):
        db_path = Path(__file__).parent.parent / "knowledge" / "gene_database.json"
        data = json.loads(db_path.read_text(encoding="utf-8"))
        for gene in data["genes"]:
            assert "confidence" in gene, f"Gene {gene.get('symbol')} missing confidence"
            assert "gene" in gene["confidence"]
            assert "interaction" in gene["confidence"]

    def test_no_disease_prediction_language(self):
        db_path = Path(__file__).parent.parent / "knowledge" / "gene_database.json"
        text = db_path.read_text(encoding="utf-8").lower()
        forbidden = ["导致疾病", "致病", "确诊", "患有", "一定会"]
        for phrase in forbidden:
            assert phrase not in text, f"Forbidden: {phrase}"
