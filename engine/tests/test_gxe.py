# =============================================================================
# 引擎单元测试 — 新生儿儿科版 (HTI + Counterfactual + AI + Recommendations)
# =============================================================================
"""Part C 引擎测试（儿科版）。运行：python -m pytest engine/tests/test_gxe.py -v"""

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

SAMPLE_GENETIC = {
    "PAH": 0.4, "G6PD": 0.3, "CYP21A2": 0.4,
    "SMN1": 0.5, "GJB2": 0.35, "SLC26A4": 0.3,
    "CHD7": 0.35, "IL2RG": 0.5, "CFTR": 0.35,
    "HBB": 0.4, "SCN1A": 0.4, "FMR1": 0.4,
}

ENV_DEFAULT = {"nutrition_type": 6, "sleep_quality": 6, "development_stimulation": 5, "medical_adherence": 7, "environmental_safety": 6}
ENV_GOOD = {"nutrition_type": 8, "sleep_quality": 9, "development_stimulation": 8, "medical_adherence": 10, "environmental_safety": 9}
ENV_BAD = {"nutrition_type": 3, "sleep_quality": 4, "development_stimulation": 2, "medical_adherence": 3, "environmental_safety": 3}
ENV_MEDIUM_LOW = {"nutrition_type": 5, "sleep_quality": 5, "development_stimulation": 4, "medical_adherence": 6, "environmental_safety": 5}


# =============================================================================
# G×E 模型测试
# =============================================================================


class TestGxEModel:
    """G×E HTI 模拟引擎（儿科版）。"""

    def test_baseline_hti_range(self):
        result = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        assert 20 <= result["baseline_hti"] <= 95

    def test_environment_effect_direction(self):
        r_good = simulate_health_trajectory(SAMPLE_GENETIC, ENV_GOOD)
        r_bad = simulate_health_trajectory(SAMPLE_GENETIC, ENV_BAD)
        assert r_good["baseline_hti"] > r_bad["baseline_hti"]

    def test_trajectory_has_all_time_points(self):
        result = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        years = [t["year"] for t in result["trajectory"]]
        assert years == [5, 10, 20]

    def test_trajectory_monotonic_decay_in_bad_env(self):
        result = simulate_health_trajectory(SAMPLE_GENETIC, ENV_BAD)
        hti_values = [t["hti"] for t in result["trajectory"]]
        for i in range(1, len(hti_values)):
            assert hti_values[i] <= hti_values[i - 1] + 5

    def test_different_environments_change_factor_analysis(self):
        r1 = simulate_health_trajectory(SAMPLE_GENETIC, ENV_GOOD)
        r2 = simulate_health_trajectory(SAMPLE_GENETIC, ENV_BAD)
        assert r1["summary"]["environment_effect"] > r2["summary"]["environment_effect"]

    def test_empty_genetic_profile(self):
        result = simulate_health_trajectory({}, ENV_DEFAULT)
        assert 20 <= result["baseline_hti"] <= 95

    def test_out_of_range_environment_clamping(self):
        env = {"nutrition_type": 99, "sleep_quality": -5, "development_stimulation": 5, "medical_adherence": 5, "environmental_safety": 0}
        result = simulate_health_trajectory(SAMPLE_GENETIC, env)
        assert 20 <= result["baseline_hti"] <= 95

    def test_factor_analysis_completeness(self):
        result = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        categories = {fa["category"] for fa in result["factor_analysis"]}
        assert "gene" in categories
        assert "environment" in categories

    def test_calculate_gxe_collaboration_interface(self):
        result = calculate_gxe(SAMPLE_GENETIC, ENV_DEFAULT)
        assert "trajectory" in result
        assert "confidence" in result
        assert "baseline_hti" in result
        assert "dimension_scores" in result
        assert "factor_analysis" in result
        assert "summary" in result

    def test_hti_naming_consistency(self):
        """验证所有输出使用 HTI 命名而非 Health Score。"""
        result = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        assert "baseline_hti" in result
        assert "hti" in result["trajectory"][0]
        assert "trend" in result["trajectory"][0]


# =============================================================================
# 反事实模拟测试
# =============================================================================


class TestCounterfactual:
    """反事实 What-If 模拟（儿科版）。"""

    def test_single_factor_counterfactual(self):
        result = simulate_counterfactual(SAMPLE_GENETIC, ENV_MEDIUM_LOW, "nutrition_type", 9)
        assert "error" not in result
        assert result["changed_factor"] == "nutrition_type"
        assert result["change"] > 0
        assert "baseline_hti" in result
        assert "new_hti" in result

    def test_counterfactual_direction_improved(self):
        result = simulate_counterfactual(SAMPLE_GENETIC, ENV_MEDIUM_LOW, "nutrition_type", 9)
        assert result["direction"] == "improved"

    def test_counterfactual_unchanged(self):
        result = simulate_counterfactual(SAMPLE_GENETIC, ENV_GOOD, "sleep_quality", 9)
        assert result["direction"] in ("improved", "unchanged")

    def test_counterfactual_all_changeable_factors(self):
        env = ENV_MEDIUM_LOW.copy()
        for factor in ["nutrition_type", "sleep_quality", "development_stimulation", "medical_adherence", "environmental_safety"]:
            result = simulate_counterfactual(SAMPLE_GENETIC, env, factor, 8)
            assert "error" not in result, f"Factor {factor} failed: {result.get('error')}"

    def test_counterfactual_rejects_unchanged_factor(self):
        result = simulate_counterfactual(SAMPLE_GENETIC, ENV_MEDIUM_LOW, "nonexistent", 8)
        assert "error" in result

    def test_scenario_comparison(self):
        result = compare_scenarios(SAMPLE_GENETIC, ENV_MEDIUM_LOW, ENV_GOOD)
        assert result["scenario_a"]["baseline_hti"] <= result["scenario_b"]["baseline_hti"]
        assert "comparison" in result
        assert "key_insight" in result["comparison"]
        assert "trajectory_divergence" in result["comparison"]

    def test_explore_all_factors(self):
        results = explore_what_if_all_factors(SAMPLE_GENETIC, ENV_MEDIUM_LOW)
        assert len(results) > 0
        # 第一个应该改善最大
        assert results[0]["change"] >= results[-1]["change"]


# =============================================================================
# AI 解释器测试
# =============================================================================


class TestAIInterpreter:
    """AI 解释器（儿科版）。"""

    def test_updated_output_format(self):
        """验证新的 6 字段输出格式。"""
        result = interpret_gene_info("PAH", "pathogenic", "attention")
        required_fields = [
            "genetic_story", "main_driver", "modifiable_factor",
            "simulation_message", "scientific_note", "disclaimer"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_confidence_fields(self):
        result = interpret_gene_info("PAH")
        assert "confidence" in result
        confidence = result["confidence"]
        assert "genetic_evidence" in confidence
        assert "interaction_evidence" in confidence
        assert "lifestyle_evidence" in confidence

    def test_disclaimer_present(self):
        r1 = interpret_gene_info("PAH")
        assert "IMPORTANT DISCLAIMER" in r1["disclaimer"]

    def test_no_disease_language(self):
        """验证不包含疾病预测语言。"""
        result = interpret_gene_info("PAH", trend_level="significant")
        output = json.dumps(result, ensure_ascii=False).lower()
        forbidden = ["您患有", "确诊", "会导致", "一定会得"]
        for phrase in forbidden:
            assert phrase not in output, f"Found forbidden phrase: {phrase}"

    def test_simulation_interpretation(self):
        sim = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        cf = compare_scenarios(SAMPLE_GENETIC, ENV_DEFAULT, ENV_GOOD)
        result = interpret_simulation_result(sim, SAMPLE_GENETIC, ENV_DEFAULT, cf)
        assert result["simulation_message"]

    def test_genetic_story_mentions_genes(self):
        sim = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        result = interpret_simulation_result(sim, SAMPLE_GENETIC, {})
        assert any(g in result["genetic_story"] for g in ["PAH", "G6PD"])


# =============================================================================
# 建议引擎测试
# =============================================================================


class TestRecommendationEngine:
    """建议引擎（儿科版）。"""

    def test_generates_recommendations(self):
        profile = {
            "dimension_scores": {
                "metabolic": 50, "cardiovascular": 50, "neurodevelopmental": 50,
                "immunodeficiency": 50, "sensory": 50,
            },
            "risk_genes": ["PAH", "SMN1"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, ENV_DEFAULT)
        assert len(recs) > 0

    def test_each_recommendation_has_new_fields(self):
        profile = {
            "dimension_scores": {
                "metabolic": 50, "cardiovascular": 50, "neurodevelopmental": 50,
                "immunodeficiency": 50, "sensory": 50,
            },
            "risk_genes": ["PAH"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, ENV_DEFAULT)
        required = {"trigger_factor", "why_for_this_user", "related_gene", "confidence"}
        for rec in recs:
            missing = required - set(rec.keys())
            assert not missing, f"Missing: {missing}"

    def test_confidence_fields_in_recommendations(self):
        profile = {
            "dimension_scores": {
                "metabolic": 50, "cardiovascular": 50, "neurodevelopmental": 50,
                "immunodeficiency": 50, "sensory": 50,
            },
            "risk_genes": ["PAH"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, ENV_DEFAULT)
        for rec in recs:
            conf = rec.get("confidence", {})
            assert "genetic_evidence" in conf
            assert "interaction_evidence" in conf
            assert "lifestyle_evidence" in conf

    def test_not_generic_health_advice(self):
        """验证建议不是'通用健康建议'。"""
        profile = {
            "dimension_scores": {
                "metabolic": 50, "cardiovascular": 50, "neurodevelopmental": 50,
                "immunodeficiency": 50, "sensory": 50,
            },
            "risk_genes": ["PAH", "G6PD", "SMN1", "HBB"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, ENV_DEFAULT)
        for rec in recs:
            assert rec["why_for_this_user"] != ""

    def test_related_gene_not_empty(self):
        profile = {
            "dimension_scores": {
                "metabolic": 50, "cardiovascular": 50, "neurodevelopmental": 50,
                "immunodeficiency": 50, "sensory": 50,
            },
            "risk_genes": ["PAH", "SMN1"],
            "overall_level": "moderate",
        }
        recs = generate(profile, None, ENV_DEFAULT)
        for rec in recs:
            assert len(rec.get("related_gene", [])) > 0

    def test_generate_from_simulation(self):
        sim = simulate_health_trajectory(SAMPLE_GENETIC, ENV_DEFAULT)
        recs = generate_from_simulation(sim, SAMPLE_GENETIC, ENV_DEFAULT)
        assert len(recs) > 0


# =============================================================================
# 知识库测试
# =============================================================================


class TestGeneDatabase:
    """基因知识库（儿科版）。"""

    def test_database_loadable(self):
        db_path = Path(__file__).parent.parent / "knowledge" / "gene_database.json"
        assert db_path.exists()
        data = json.loads(db_path.read_text(encoding="utf-8"))
        assert len(data["genes"]) == 25

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
