"""
PRS 计算器单元测试 — A1.5
==========================
验证多基因风险评分的计算逻辑。

运行方式：
    pytest backend/tests/test_prs.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.prs_calculator import (  # noqa: E402
    classify_variant_to_disease,
    risk_score_for_variant,
    significance_weight,
)


# ============ 基因归类 ============

def test_classify_brca1_breast():
    assert classify_variant_to_disease("BRCA1") == "breast_cancer"
    assert classify_variant_to_disease("BRCA2") == "breast_cancer"


def test_classify_cftr_none():
    assert classify_variant_to_disease("CFTR") is None


def test_classify_lowcase_insensitive():
    assert classify_variant_to_disease("brca1") == "breast_cancer"


def test_classify_empty():
    assert classify_variant_to_disease("") is None
    assert classify_variant_to_disease(None) is None


# ============ 显著性权重 ============

def test_significance_weights():
    assert significance_weight("Pathogenic") == 1.0
    assert significance_weight("Likely_pathogenic") == 0.8
    assert significance_weight("Uncertain_significance") == 0.3
    assert significance_weight("Benign") == 0.0
    assert significance_weight(None) == 0.1


def test_significance_multiple_values():
    """分号分隔的多值取最高权重。"""
    assert significance_weight("Pathogenic;Likely_benign") == 1.0


def test_significance_space_separated():
    assert significance_weight("Likely Pathogenic") == 0.8


# ============ PRS 计算 ============

def test_empty_variants():
    from backend.services.prs_calculator import calculate_prs
    result = calculate_prs([])
    assert result["overall_risk_level"] == "low"
    assert all(v == 1.0 for v in result["risk_scores"].values())


def test_single_high_risk_variant():
    """单个高致病性变异应显著提升对应疾病风险。"""
    from backend.services.prs_calculator import calculate_prs
    variants = [
        {
            "gene_name": "BRCA1",
            "clinvar_significance": "Pathogenic",
            "odds_ratio": 4.0,
        }
    ]
    result = calculate_prs(variants, disease="breast_cancer")
    assert result["risk_scores"]["breast_cancer"] > 1.0
    assert result["overall_risk_level"] == "high"


def test_benign_variant_no_risk():
    """良性变异不应提升风险。"""
    from backend.services.prs_calculator import calculate_prs
    variants = [
        {
            "gene_name": "BRCA1",
            "clinvar_significance": "Benign",
            "odds_ratio": 1.0,
        }
    ]
    result = calculate_prs(variants, disease="breast_cancer")
    assert result["risk_scores"]["breast_cancer"] <= 1.0
    assert result["overall_risk_level"] == "low"


def test_disease_isolation():
    """不同疾病的变异不应互相影响。"""
    from backend.services.prs_calculator import calculate_prs
    variants = [
        {"gene_name": "BRCA1", "clinvar_significance": "Pathogenic", "odds_ratio": 4.0},
        {"gene_name": "LDLR", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0},
    ]
    result = calculate_prs(variants)
    assert result["risk_scores"]["breast_cancer"] > 1.5
    assert result["risk_scores"]["cardio"] > 1.5
    # 不相关疾病保持 1.0
    assert result["risk_scores"]["alzheimer"] == 1.0


def test_confidence_intervals():
    """置信区间应围绕风险倍数对称。"""
    from backend.services.prs_calculator import calculate_prs
    variants = [
        {"gene_name": "APOE", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0}
    ]
    result = calculate_prs(variants, disease="alzheimer")
    ci = result["confidence_intervals"]["alzheimer"]
    risk = result["risk_scores"]["alzheimer"]
    assert ci[0] < risk < ci[1]


def test_monotonic_increasing():
    """变异越多风险越高（单调性）。"""
    from backend.services.prs_calculator import calculate_prs
    one = calculate_prs(
        [{"gene_name": "BRCA1", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0}],
        disease="breast_cancer",
    )
    two = calculate_prs(
        [
            {"gene_name": "BRCA1", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0},
            {"gene_name": "BRCA2", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0},
        ],
        disease="breast_cancer",
    )
    assert two["risk_scores"]["breast_cancer"] > one["risk_scores"]["breast_cancer"]


# ============ 风险评分辅助 ============

def test_risk_score_for_variant():
    score = risk_score_for_variant("Pathogenic", 4.0)
    assert 0 < score <= 0.99
    benign = risk_score_for_variant("Benign")
    assert benign == 0.0
    vus = risk_score_for_variant("Uncertain_significance")
    assert vus == 0.3
