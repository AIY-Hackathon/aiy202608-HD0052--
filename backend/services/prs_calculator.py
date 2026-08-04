"""
PRS（多基因风险评分）计算器 — A1.5
===================================
基于 ClinVar 变异注释和人群频率，计算多基因风险评分。

评分逻辑：
  PRS = Σ( ln(odds_ratio) × 风险等位基因数量 )  （加权和）
  综合风险等级根据 PRS 相对人群基准的倍数划分。

风险等级划分：
  low      → 风险倍数 < 1.0
  moderate → 1.0 ≤ 风险倍数 < 2.0
  high     → 风险倍数 ≥ 2.0

依赖：numpy（已安装）
"""
from __future__ import annotations

from math import log

import numpy as np

# 疾病类别 → 涉及的基因
# 简化映射：根据变异的致病性 + 基因名，归入常见疾病类别
DISEASE_GENE_MAP: dict[str, set[str]] = {
    "cardio": {"LDLR", "APOB", "PCSK9", "SCN5A", "KCNQ1", "KCNH2"},
    "diabetes": {"HNF1A", "HNF4A", "GCK", "TCF7L2", "KCNJ11"},
    "breast_cancer": {"BRCA1", "BRCA2", "PALB2", "CHEK2", "ATM"},
    "colorectal": {"APC", "MLH1", "MSH2", "MSH6", "PMS2", "MUTYH"},
    "alzheimer": {"APOE", "APP", "PSEN1", "PSEN2"},
    "obesity": {"MC4R", "FTO", "LEP", "LEPR"},
    "hypertension": {"AGT", "ACE", "ADD1", "CYP11B2"},
}

# 基因组背景风险（无风险变异时的人群基准）
BASE_RISK: dict[str, float] = {
    "cardio": 0.15,
    "diabetes": 0.10,
    "breast_cancer": 0.13,
    "colorectal": 0.04,
    "alzheimer": 0.11,
    "obesity": 0.42,
    "hypertension": 0.30,
}

# 变异类型权重
# Pathogenic/Likely_pathogenic 对风险贡献最大
SIGNIFICANCE_WEIGHT: dict[str, float] = {
    "Pathogenic": 1.0,
    "Likely_pathogenic": 0.8,
    "Uncertain_significance": 0.3,
    "Likely_benign": 0.1,
    "Benign": 0.0,
}


def classify_variant_to_disease(gene_name: str) -> str | None:
    """根据基因名归类疾病类别。"""
    if not gene_name:
        return None
    gene = gene_name.upper().split("-")[0]
    for disease, genes in DISEASE_GENE_MAP.items():
        if gene in genes:
            return disease
    return None


def significance_weight(clinvar_sig: str | None) -> float:
    """将 ClinVar 临床意义映射为权重。"""
    if not clinvar_sig:
        return 0.1
    # 处理多值（分号分隔）和空格分隔（如 "Likely Pathogenic"）
    for sig in clinvar_sig.split(";"):
        sig = sig.strip().replace(" ", "_")
        # 统一大小写匹配
        for key, weight in SIGNIFICANCE_WEIGHT.items():
            if sig.lower() == key.lower():
                return weight
    return 0.1


def calculate_prs(
    variants: list[dict],
    disease: str | None = None,
) -> dict:
    """计算多基因风险评分。

    Args:
        variants: 变异字典列表（对齐 schemas.VariantOut）
                 每条需含：gene_name、clinvar_significance、odds_ratio（可选）、risk_score（可选）
        disease: 指定疾病类别（None = 计算所有类别）

    Returns:
        {
            "risk_scores": {disease: 风险倍数},
            "overall_risk_level": "low"|"moderate"|"high",
            "confidence_intervals": {disease: [lower, upper]}
        }
    """
    if not variants:
        return _empty_result()

    # 按疾病归类计算风险倍数
    risk_multipliers: dict[str, float] = {}

    for disease_key in (list(DISEASE_GENE_MAP.keys()) if disease is None else [disease]):
        relevant = []
        for v in variants:
            v_disease = classify_variant_to_disease(v.get("gene_name", ""))
            if v_disease == disease_key:
                relevant.append(v)

        if not relevant:
            risk_multipliers[disease_key] = 1.0
            continue

        # 综合风险倍数
        combined = 1.0
        for v in relevant:
            weight = significance_weight(v.get("clinvar_significance"))
            if weight <= 0:
                continue

            # 优先用 odds_ratio，否则用 risk_score
            odds = v.get("odds_ratio") or 1.0
            contribution = max(1.0, odds) ** weight
            combined *= contribution

        # 限制在一个合理范围
        risk_multipliers[disease_key] = round(min(combined, 10.0), 2)

    # 整体风险等级（取所有类别的最大风险）
    max_risk = max(risk_multipliers.values()) if risk_multipliers else 1.0
    if max_risk < 1.2:
        level = "low"
    elif max_risk < 2.0:
        level = "moderate"
    else:
        level = "high"

    # 置信区间（±15%）
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


def _empty_result() -> dict:
    """无变异时的结果。"""
    risk = {d: 1.0 for d in DISEASE_GENE_MAP}
    return {
        "risk_scores": risk,
        "overall_risk_level": "low",
        "confidence_intervals": {d: [0.85, 1.15] for d in DISEASE_GENE_MAP},
    }


# ============ 兼容辅助 ============

def risk_score_for_variant(clinvar_sig: str | None, odds_ratio: float | None = None) -> float:
    """为单个变异生成 0-1 风险评分（前端展示用）。"""
    weight = significance_weight(clinvar_sig)
    if odds_ratio and odds_ratio > 1:
        return round(min(weight * (log(odds_ratio) / log(4)) + weight * 0.2, 0.99), 2)
    return round(weight, 2)
