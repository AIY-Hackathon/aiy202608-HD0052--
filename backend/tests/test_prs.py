"""
基因分析引擎单元测试 — A1.5 / A2
==================================
验证健康维度评分、基因卡片生成、健康评分、建议引擎。

运行方式：
    pytest backend/tests/test_prs.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.prs_calculator import (  # noqa: E402
    calculate_dimension_scores,
    calculate_dimension_scores_with_factors,
    calculate_health_score,
    calculate_prs,
    classify_gene_to_dimension,
    classify_gene_to_disease,
    generate_gene_cards,
    generate_recommendations,
    generate_thirty_day_plan,
    generate_trend_data,
    risk_level_from_significance,
    risk_score_for_variant,
    significance_weight,
)


# ============ 基因 → 维度归类 ============

def test_classify_gene_to_dimension():
    assert classify_gene_to_dimension("APOE") == "cognitive"
    assert classify_gene_to_dimension("FTO") == "metabolic"
    assert classify_gene_to_dimension("ACTN3") == "athletic"
    assert classify_gene_to_dimension("CLOCK") == "sleep"
    assert classify_gene_to_dimension("LDLR") == "cardiovascular"


def test_classify_gene_to_dimension_unknown():
    assert classify_gene_to_dimension("CFTR") is None
    assert classify_gene_to_dimension("") is None
    assert classify_gene_to_dimension(None) is None


def test_classify_gene_to_disease_retained():
    """原疾病风险映射保留。"""
    assert classify_gene_to_disease("BRCA1") == "breast_cancer"
    assert classify_gene_to_disease("LDLR") == "cardio"


# ============ 维度评分 ============

def test_dimension_scores_default():
    """无变异时所有维度 = 基线 50。"""
    scores = calculate_dimension_scores([])
    assert len(scores) == 5
    keys = {s["key"] for s in scores}
    assert keys == {"metabolic", "cognitive", "cardiovascular", "athletic", "sleep"}
    for s in scores:
        assert s["score"] == 50
        assert s["baseline"] == 50
        assert s["label"]


def test_dimension_scores_pathogenic_raises():
    """致病性变异应提高对应维度风险分。"""
    variants = [
        {"gene_name": "APOE", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0}
    ]
    scores = calculate_dimension_scores(variants)
    cognitive = next(s for s in scores if s["key"] == "cognitive")
    assert cognitive["score"] > 50


def test_dimension_scores_benign_unchanged():
    """良性变异不显著改变维度分。"""
    variants = [
        {"gene_name": "FTO", "clinvar_significance": "Benign", "odds_ratio": 1.0}
    ]
    scores = calculate_dimension_scores(variants)
    metabolic = next(s for s in scores if s["key"] == "metabolic")
    assert metabolic["score"] <= 50


def test_dimension_scores_clamped():
    """分数应限制在 5-95。"""
    many_variants = [
        {"gene_name": "APOE", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "TOMM40", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "APP", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "PSEN1", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "PSEN2", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "CLU", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
    ]
    scores = calculate_dimension_scores(many_variants)
    for s in scores:
        assert 5 <= s["score"] <= 95


# ============ 健康评分 ============

def test_health_score_baseline():
    """默认因素应接近遗传基线。"""
    score = calculate_health_score()
    assert 35 <= score <= 98
    # 默认因素 sleep=6 exercise=3 diet=5 stress=6 → 偏差≈0
    assert score == 72


def test_health_score_optimized_higher():
    """优化生活方式应提高健康分。"""
    base = calculate_health_score({})
    optimized = calculate_health_score({"sleep": 8, "exercise": 5, "diet": 8, "stress": 3})
    assert optimized > base


def test_health_score_clamped():
    """极端输入应被限制在 35-98。"""
    score = calculate_health_score({"sleep": 10, "exercise": 7, "diet": 10, "stress": 1})
    assert score <= 98
    score = calculate_health_score({"sleep": 3, "exercise": 0, "diet": 1, "stress": 10})
    assert score >= 35


# ============ 基因卡片 ============

def test_gene_cards_empty_variants():
    """无变异时返回默认卡片。"""
    cards = generate_gene_cards([])
    assert len(cards) <= 4
    symbols = {c["symbol"] for c in cards}
    assert symbols.issubset({"APOE", "FTO", "ACTN3", "CLOCK", "TOMM40", "LDLR", "MC4R", "PER3", "MSTN"})
    for c in cards:
        assert "id" in c and "symbol" in c and "name" in c
        assert "riskLevel" in c and "summary" in c
        assert "recommendations" in c


def test_gene_cards_with_variants():
    """变异应影响卡片风险等级。"""
    variants = [
        {"gene_name": "APOE", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0}
    ]
    cards = generate_gene_cards(variants)
    assert any(c["symbol"] == "APOE" for c in cards)
    apoe = next(c for c in cards if c["symbol"] == "APOE")
    assert apoe["riskLevel"] in {"elevated", "moderate"}
    assert apoe["clinvar_significance"] == "Pathogenic"


# ============ 风险等级映射 ============

def test_risk_level_mapping():
    assert risk_level_from_significance("Pathogenic") == "elevated"
    assert risk_level_from_significance("Benign") == "low"
    assert risk_level_from_significance("Uncertain_significance") == "moderate"
    assert risk_level_from_significance(None) == "moderate"


# ============ 建议引擎 ============

def test_recommendations_structure():
    """建议应含前端所需字段。"""
    recs = generate_recommendations({"sleep": 5, "exercise": 2, "diet": 3, "stress": 8})
    assert len(recs) >= 3
    for r in recs:
        assert "id" in r and "pillar" in r and "icon" in r
        assert "title" in r and "description" in r
        assert "difficulty" in r and "impact" in r and "time" in r


def test_recommendations_optimized_empty():
    """完全优化的生活方式应减少建议。"""
    recs = generate_recommendations({"sleep": 8, "exercise": 5, "diet": 8, "stress": 3})
    # 至少会有"正在养成良好习惯"一条
    assert len(recs) >= 1


# ============ 趋势数据 ============

def test_trend_data_structure():
    """趋势数据应含 current/optimized/year。"""
    trend = generate_trend_data([], {"sleep": 6, "exercise": 3, "diet": 5, "stress": 6})
    assert len(trend) == 7  # 0,1,3,5,10,15,20
    for t in trend:
        assert "year" in t and "current" in t and "optimized" in t


# ============ 30 天计划 ============

def test_thirty_day_plan_structure():
    plan = generate_thirty_day_plan()
    assert "goal" in plan
    assert len(plan["weeks"]) == 4
    for week in plan["weeks"]:
        assert "label" in week and "theme" in week and "tasks" in week
        assert len(week["tasks"]) == 3
        for task in week["tasks"]:
            assert "day" in task and "title" in task and "desc" in task


# ============ 原 PRS 能力保留 ============

def test_calculate_prs_retained():
    result = calculate_prs(
        [{"gene_name": "BRCA1", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0}],
        disease="breast_cancer",
    )
    assert result["risk_scores"]["breast_cancer"] > 1.0


def test_risk_score_for_variant_retained():
    score = risk_score_for_variant("Pathogenic", 4.0)
    assert 0 < score <= 0.99


def test_significance_weight_retained():
    assert significance_weight("Pathogenic") == 1.0
    assert significance_weight("Benign") == 0.0
