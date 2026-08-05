# =============================================================================
# engine/config.py — G×E Health Trajectory Simulation Engine Configuration
# =============================================================================
#
# Health Trajectory Index (HTI) — Educational Simulation Framework
# ─────────────────────────────────────────────────────────────────
# HTI 是一个教育性模拟指标 (pedagogical simulation index)，用于展示：
#   Genetic Predisposition + Lifestyle Environment + G×E Interaction
#   之间的关系。
#
# This system:
#   ✗ Does NOT predict disease
#   ✗ Does NOT provide clinical diagnosis
#   ✗ Does NOT output individual health risk
#   ✗ Does NOT claim genes determine health outcomes
#
# This system:
#   ✓ Demonstrates gene-environment interaction concepts
#   ✓ Uses population-level statistical associations
#   ✓ Emphasizes modifiable environmental factors
#   ✓ Shows genes influence susceptibility, not destiny
#
# All numerical parameters are model-internal relative weights —
# NOT clinical effect sizes, NOT disease risk percentages.
# =============================================================================
from __future__ import annotations

from typing import Any, Dict, List, Tuple, TypedDict, Union

# =============================================================================
# 0. Model Constants — 模型数学边界
# =============================================================================
# These define the guardrails within which the simulation operates.
# They are pedagogical design parameters, NOT empirically derived limits.

HTI_MODEL_CONSTANTS = {
    "hti_range": (0, 100),          # HTI scale bounds (full possible range)
    "hti_typical_range": (20, 95),  # Typical simulation output range
    "weight_range": (0.0, 1.0),     # Per-dimension weight bounds
    "interaction_range": (-0.15, 0.15),  # Constrained interaction term
    "time_horizon_years": [5, 10, 20],   # Simulation time points
    "base_decay_rate": 0.5,              # HTI pts/year in simulation
    "confidence_interval_width": 0.08,   # Model-internal uncertainty band
}

# ---------------------------------------------------------------------------
# Design rationale for the gene:environment relative weighting (40:60)
# ────────────────────────────────────────────────────────────────────
# gene_relative_weight_ceiling  = 0.40
# environment_relative_weight_ceiling = 0.60
#
# This asymmetric weighting is a PEDAGOGICAL CHOICE within this
# simulation model. It is NOT a biological variance decomposition,
# heritability estimate, or population-level contribution estimate.
# It intentionally gives environment a larger share of the simulated
# HTI to reinforce the educational message that lifestyle factors
# are potent modulators.
#
# Real heritability estimates differ by trait (e.g., BMI ~40-70%,
# Alzheimer's ~60-80%), and G×E interactions further complicate
# additive partitioning. The 40:60 split serves the educational
# purpose of the model — it does not represent any specific
# population estimate or claim that genes and environment each
# contribute fixed percentages to health outcomes.
#
# Interaction terms are constrained to ±0.15 because published G×E
# effects are typically modest and require large sample sizes to
# detect. Wide interaction ranges would falsely imply strong,
# predictable gene×environment synergy. These are small educational
# interaction parameters, not strong biological synergy effects.
# ---------------------------------------------------------------------------


# =============================================================================
# 1. Model Metadata — 模型身份声明
# =============================================================================
MODEL_METADATA: dict[str, object] = {
    "model_type": "educational simulation",
    "purpose": "illustrate gene-environment interaction concepts",
    "clinical_use": False,
    "prediction_scope": (
        "not a disease prediction model — simulates health trajectory "
        "trends for educational demonstration"
    ),
    "evidence_basis": (
        "GWAS Catalog and peer-reviewed genome-wide association studies; "
        "population-based cohort studies; lifestyle intervention research; "
        "meta-analyses of gene-environment interaction"
    ),
    "intended_audience": "researchers, educators, and health science communicators",
    "output_interpretation": (
        "Simulated Health Trajectory Index (HTI) values represent educational "
        "scenario outcomes, not individual health forecasts. All scores are "
        "relative model weights, not clinical effect sizes or risk percentages."
    ),
    "version": "2.0.0",
}


# =============================================================================
# 2. Typed Definitions — 类型安全配置
# =============================================================================


class GeneWeightEntry(TypedDict, total=False):
    """Per-gene dimension weights + metadata within GENE_WEIGHTS."""

    cognitive: float
    cardiovascular: float
    metabolic: float
    athletic: float
    sleep: float
    overall_health: float
    base_effect: float
    time_multiplier: float
    description: str
    reference: str
    parameter_type: str
    evidence_confidence: dict[str, str]
    uncertainty_note: str


class EnvironmentWeightEntry(TypedDict, total=False):
    """Per-factor dimension weights + metadata within ENVIRONMENT_WEIGHTS."""

    metabolic: float
    cognitive: float
    cardiovascular: float
    athletic: float
    sleep: float
    overall_health: float
    description: str
    reference: str
    parameter_type: str
    uncertainty_note: str


class InteractionEntry(TypedDict, total=False):
    """Per-gene G×E coefficients + metadata within INTERACTION_COEFFICIENTS."""

    exercise: float
    sleep: float
    diet: float
    stress: float
    smoking: float
    description: str
    parameter_type: str
    uncertainty_note: str


class DimensionEntry(TypedDict, total=False):
    """Per-dimension display config within DIMENSION_CONFIG."""

    label: str
    icon: str
    baseline: int
    description: str
    time_sensitivity: float


class EnvironmentRangeEntry(TypedDict, total=False):
    """Per-factor range config within ENVIRONMENT_RANGES."""

    min: int
    max: int
    optimal: int
    unit: str
    label: str
    note: str


# =============================================================================
# 3. Genetic Predisposition Weights — 遗传倾向贡献
# =============================================================================
#
# IMPORTANT — Please read before interpreting:
# ─────────────────────────────────────────────
# • These are model-internal relative weights designed for educational
#   simulation, NOT estimates of clinical effect size.
# • A weight of 0.45 does NOT mean "gene increases risk by 45%".
#   It assigns relative importance across health dimensions within
#   the simulation engine.
# • Weights are based on GWAS and population-level associations,
#   which reflect statistical patterns across thousands of individuals,
#   NOT causal effects on a single person.
# • Genetic predisposition reflects susceptibility tendencies at the
#   population level. Individual outcomes depend heavily on environment,
#   behavior, and chance.
#
# Parameter type: educational_relative_weight
# Interpretation: simulation coefficient, not biological effect size
# =============================================================================

GENE_WEIGHTS: dict[str, GeneWeightEntry] = {
    "APOE": {
        "cognitive": 0.45,
        "cardiovascular": 0.25,
        "metabolic": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,
        "time_multiplier": 1.15,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "APOE variants are associated with differences in susceptibility "
            "related to cognitive and lipid metabolism traits at the population "
            "level. The ε4 allele shows allele-dose-dependent associations with "
            "cognitive health indicators in observational studies, but does NOT "
            "determine individual cognitive outcomes. APOE 参与脂蛋白代谢与神经保护。"
            "基因型差异反映人群统计层面的倾向差异，不决定个体结果。"
        ),
        "reference": (
            "Lambert et al. (2013) — Nature Genetics. "
            "Meta-analysis of 74,046 individuals identifies 11 new susceptibility "
            "loci for Alzheimer's disease. "
            "Bertram et al. (2007) — Alzgene meta-analysis. "
            "Systematic meta-analyses of Alzheimer disease genetic association studies."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate",
            "population_generalizability": "limited — strongest evidence in European-ancestry populations",
        },
        "uncertainty_note": (
            "APOE is the strongest common genetic association for cognitive traits "
            "in populations of European ancestry. However, (a) association is "
            "allele-dependent (ε4 risk, ε2 protective), not a single direction; "
            "(b) effect sizes differ across ancestry groups; (c) many ε4 carriers "
            "never develop cognitive impairment — environment modifies risk "
            "substantially."
        ),
    },
    "FTO": {
        "cognitive": 0.05,
        "cardiovascular": 0.15,
        "metabolic": 0.50,
        "athletic": 0.10,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "FTO variants show population-level associations with energy balance "
            "and body weight regulation. The FTO locus is one of the best-documented "
            "examples of G×E interaction: physical activity is consistently reported "
            "to attenuate FTO-BMI statistical association, but the magnitude of "
            "attenuation varies across studies. FTO 参与能量平衡与食欲调控。常见变异与"
            "体重管理在人群水平存在统计关联。个体体重受饮食、运动等环境因素广泛调节。"
        ),
        "reference": (
            "Frayling et al. (2007) — Science 316:889-894. "
            "A common variant in the FTO gene is associated with body mass index "
            "and predisposes to childhood and adult obesity. "
            "Speliotes et al. (2010) — Nature Genetics 42:937-948. "
            "Association analyses of 249,796 individuals reveal 18 new loci "
            "associated with body mass index."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate_to_high",
            "population_generalizability": "moderate — replicated in multiple ancestry groups, effect sizes vary",
        },
        "uncertainty_note": (
            "FTO is the most replicated obesity-associated locus. The individual "
            "per-allele effect on BMI is small (~0.25-0.35 kg/m²), explaining "
            "~1% of BMI variance. Exercise attenuation is the best-documented G×E "
            "interaction in complex trait genetics, but the magnitude of attenuation "
            "varies across cohorts, measurement methods, and populations."
        ),
    },
    "CLOCK": {
        "cognitive": 0.15,
        "metabolic": 0.10,
        "sleep": 0.50,
        "overall_health": 0.20,
        "base_effect": 0.25,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "CLOCK participates in circadian rhythm regulation networks. "
            "Common variants show small, population-level associations with sleep "
            "timing preferences (chronotype). Individual variant effects on sleep "
            "traits are weak and inconsistently detected in large GWAS (UK Biobank, "
            "23andMe). CLOCK 调控昼夜节律基因网络。常见变异与睡眠时型在人群水平存在"
            "微弱关联，个体效应通常较小。睡眠质量主要受环境和行为因素影响。"
        ),
        "reference": (
            "Jones et al. (2019) — Nature Communications 10:1585. "
            "Genome-wide association analyses of chronotype in 697,828 individuals "
            "provides insights into circadian rhythms."
        ),
        "evidence_confidence": {
            "genetic_association": "moderate",
            "gene_environment_interaction": "limited_to_moderate",
            "population_generalizability": "limited — strongest evidence from European-ancestry GWAS",
        },
        "uncertainty_note": (
            "CLOCK gene function in circadian biology is well-established at the "
            "molecular level (Nobel Prize in Physiology or Medicine 2017 for "
            "circadian mechanisms). However, common genetic variants in CLOCK do "
            "NOT reach genome-wide significance for sleep duration or chronotype "
            "in the largest GWAS. This illustrates a key concept: gene importance "
            "in biology ≠ variant effect size in populations. The G×E interaction "
            "evidence is biologically plausible (circadian-relevant environmental "
            "factors like light exposure and meal timing are hypothesized "
            "modulators) but quantitatively limited."
        ),
    },
    "ACTN3": {
        "athletic": 0.45,
        "metabolic": 0.10,
        "cardiovascular": 0.10,
        "overall_health": 0.15,
        "base_effect": 0.20,
        "time_multiplier": 1.05,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "ACTN3 encodes α-actinin-3 expressed in fast-twitch (type II) muscle "
            "fibers. The R577X variant affects muscle fiber composition at the "
            "biological level, but population-level effects on general strength "
            "traits are small and context-dependent. Athletic performance depends "
            "heavily on training and environment — genotype alone does NOT predict "
            "athletic ability. ACTN3 编码 α-辅肌动蛋白-3。基因型在生物学层面影响"
            "肌纤维组成，但运动表现高度依赖训练环境和后天努力。"
        ),
        "reference": (
            "El Ouali et al. (2024) — Sports Medicine Open. "
            "A systematic review and meta-analysis of the association between "
            "ACTN3 R577X genotypes and performance in endurance versus power "
            "athletes and non-athletes."
        ),
        "evidence_confidence": {
            "genetic_association": "high — at the protein/biological level",
            "gene_environment_interaction": "limited_to_moderate",
            "population_generalizability": "limited — strongest signal in elite athletes, not general population",
        },
        "uncertainty_note": (
            "ACTN3 R577X is a well-characterized functional variant: XX genotype "
            "produces no α-actinin-3 protein. Elite athlete case-control studies "
            "have reported modest associations between ACTN3 R577X genotype and "
            "power-oriented athletic performance, but the effect is context-"
            "dependent and does not predict individual athletic ability. "
            "Grip strength GWAS do NOT detect ACTN3 as significant in the general "
            "population. This gene is an excellent educational example of how "
            "genetic effects can be highly context-dependent (training type × "
            "genotype interaction)."
        ),
    },
}

# =============================================================================
# 4. Environment Factor Weights — 环境因素相对权重
# =============================================================================
#
# These are model-internal relative coefficients representing how each
# lifestyle factor contributes to each health dimension in the simulation.
# They do NOT represent individual-level effect sizes or clinical
# intervention effects.
#
# Environmental factors are deliberately weighted more heavily than
# genetic factors in this model to emphasize their modifiability —
# a pedagogical design choice.
# =============================================================================

ENVIRONMENT_WEIGHTS: dict[str, EnvironmentWeightEntry] = {
    "exercise": {
        "metabolic": 0.35,
        "cognitive": 0.20,
        "cardiovascular": 0.40,
        "athletic": 0.50,
        "sleep": 0.10,
        "overall_health": 0.30,
        "parameter_type": "educational_relative_weight",
        "description": (
            "Regular physical activity is consistently associated with favorable "
            "cardiovascular and metabolic health indicators in observational "
            "population studies. Exercise is one of the most modifiable "
            "environmental factors. 规律运动在人群研究中与心血管和代谢健康指标的"
            "改善相关。运动是最可改变的环境因素之一。"
        ),
        "reference": (
            "Evidence based on published physical activity guidelines "
            "and prospective cohort studies"
        ),
        "uncertainty_note": (
            "Observational associations between exercise and health outcomes "
            "are subject to confounding (healthy user bias) and reverse causation. "
            "Randomized trial evidence for specific exercise thresholds is more "
            "limited than observational data."
        ),
    },
    "sleep": {
        "metabolic": 0.20,
        "cognitive": 0.35,
        "cardiovascular": 0.15,
        "athletic": 0.10,
        "sleep": 0.50,
        "overall_health": 0.25,
        "parameter_type": "educational_relative_weight",
        "description": (
            "Adequate sleep duration and quality are associated with cognitive "
            "function and metabolic regulation in observational studies. "
            "充足睡眠与认知功能和代谢调节在观察性研究中存在一致关联。"
        ),
        "reference": (
            "Evidence based on published sleep research and population cohort studies"
        ),
        "uncertainty_note": (
            "Sleep-health relationships are bidirectional: poor health can disrupt "
            "sleep, and poor sleep can affect health. Optimal sleep duration varies "
            "between individuals. Causal evidence from long-term randomized trials "
            "is limited."
        ),
    },
    "diet": {
        "metabolic": 0.40,
        "cognitive": 0.15,
        "cardiovascular": 0.30,
        "athletic": 0.10,
        "sleep": 0.05,
        "overall_health": 0.25,
        "parameter_type": "educational_relative_weight",
        "description": (
            "Dietary patterns are associated with metabolic and cardiovascular "
            "health indicators in population research. 均衡饮食模式与代谢和心血管"
            "健康指标在人群研究中存在一致关联。"
        ),
        "reference": (
            "Evidence based on published dietary guidelines "
            "and nutritional epidemiology studies"
        ),
        "uncertainty_note": (
            "Nutritional epidemiology is challenged by measurement error in "
            "dietary assessment, confounding by other lifestyle factors, and "
            "the difficulty of isolating individual nutrient effects from "
            "overall dietary patterns."
        ),
    },
    "stress": {
        "metabolic": 0.15,
        "cognitive": 0.30,
        "cardiovascular": 0.25,
        "athletic": 0.05,
        "sleep": 0.30,
        "overall_health": 0.20,
        "parameter_type": "educational_relative_weight",
        "description": (
            "Chronic psychological stress is associated with alterations in "
            "multiple physiological systems in observational research. "
            "长期心理压力在观察性研究中与多个生理系统的适应性变化相关。"
        ),
        "reference": (
            "Evidence based on published psychoneuroimmunology "
            "and stress physiology research"
        ),
        "uncertainty_note": (
            "Stress measurement is inherently subjective. Causal pathways "
            "between stress and health outcomes are complex and multifactorial. "
            "Most evidence comes from observational studies; experimental "
            "stress-reduction trials show mixed results for hard health endpoints."
        ),
    },
    "smoking": {
        "metabolic": 0.10,
        "cognitive": 0.15,
        "cardiovascular": 0.45,
        "athletic": 0.15,
        "sleep": 0.10,
        "overall_health": 0.30,
        "parameter_type": "educational_relative_weight",
        "description": (
            "Tobacco exposure is one of the most well-documented modifiable "
            "factors associated with cardiovascular health indicators in "
            "epidemiological research. 烟草暴露是流行病学研究中与心血管健康"
            "相关的最为明确的可改变因素之一。"
        ),
        "reference": (
            "Evidence based on published tobacco control research "
            "and epidemiological studies"
        ),
        "uncertainty_note": (
            "The causal relationship between smoking and health outcomes is "
            "one of the strongest in epidemiology, supported by multiple lines "
            "of evidence. However, the quantitative impact on our simulation "
            "indices is a model parameter, not an individual risk estimate."
        ),
    },
}

# =============================================================================
# 5. Gene × Environment Interaction Coefficients — 基因×环境交互
# =============================================================================
#
# CRITICAL — These are MODEL PARAMETERS only:
# ─────────────────────────────────────────
# • These coefficients are pedagogical parameters within the simulation.
# • They do NOT represent validated biological interaction effect sizes.
# • Published G×E interaction effects are typically small, require large
#   sample sizes to detect, and vary substantially across populations
#   and environmental contexts.
#
# Sign convention in this model:
#   Positive: favourable environment may buffer genetic predisposition
#   Negative: unfavourable environment may amplify genetic susceptibility
#
# This sign convention is a model design choice. Real biological
# interactions can be more complex (non-linear, context-dependent,
# present in some populations but not others).
# =============================================================================

INTERACTION_COEFFICIENTS: dict[str, InteractionEntry] = {
    "APOE": {
        "exercise": 0.15,
        "sleep": 0.12,
        "diet": 0.15,
        "stress": 0.10,
        "smoking": -0.05,
        "parameter_type": "model_parameter",
        "description": (
            "Observational studies report that physical activity and "
            "Mediterranean-type dietary patterns are associated with more "
            "favourable cognitive health trajectories, potentially buffering "
            "some APOE-related genetic predisposition. These are statistical "
            "associations, not established causal interactions. "
            "APOE 与生活方式在观察性研究中存在交互信号：规律运动和地中海饮食"
            "模式与更有利的认知健康轨迹相关。"
        ),
        "uncertainty_note": (
            "APOE-related G×E interaction evidence is predominantly from "
            "observational studies with inherent confounding risks. "
            "Randomized trial evidence is sparse. Interaction magnitudes "
            "are not precisely quantified and likely differ by ancestry."
        ),
    },
    "FTO": {
        "exercise": 0.15,
        "diet": 0.15,
        "sleep": 0.10,
        "stress": 0.08,
        "smoking": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "Physical activity is consistently reported to attenuate the "
            "population-level association between FTO variants and body weight "
            "in observational studies. Attenuation magnitude varies across "
            "cohorts and measurement methods — a model G×E interaction example. "
            "FTO 是 G×E 交互研究中最常被报道的案例之一：体力活动在观察性研究中"
            "被反复报告与 FTO 变异-体重关联减弱相关。"
        ),
        "uncertainty_note": (
            "Exercise attenuation of FTO-BMI association is well-documented "
            "but the magnitude is cohort-dependent. Most studies use self-reported "
            "physical activity, which introduces measurement error. "
            "G×E estimates from specific cohorts may not generalize broadly."
        ),
    },
    "CLOCK": {
        "exercise": 0.10,
        "sleep": 0.15,
        "diet": 0.10,
        "stress": 0.12,
        "smoking": 0.08,
        "parameter_type": "model_parameter",
        "description": (
            "CLOCK variants show biological plausibility for circadian-relevant "
            "G×E interactions. Consistent sleep-wake timing, light exposure "
            "patterns, and meal timing are hypothesized environmental modulators. "
            "Quantitative evidence from large population studies is limited. "
            "CLOCK 基因与昼夜节律同步具有生物学上的交互合理性，但定量证据"
            "有限。"
        ),
        "uncertainty_note": (
            "G×E interaction evidence for CLOCK is biologically plausible "
            "but quantitatively weak. Individual CLOCK variants do not reach "
            "genome-wide significance in sleep/chronotype GWAS. Interaction "
            "hypotheses are largely based on mechanistic reasoning rather "
            "than robust epidemiological detection."
        ),
    },
    "ACTN3": {
        "exercise": 0.15,
        "sleep": 0.08,
        "diet": 0.10,
        "stress": 0.05,
        "smoking": 0.03,
        "parameter_type": "model_parameter",
        "description": (
            "ACTN3 genotype may influence training response — a model G×E "
            "interaction example where genetic predisposition is highly "
            "context-dependent. Training type and intensity, not genotype "
            "alone, determine athletic outcomes. ACTN3 基因型可能影响训练响应"
            "——G×E 交互的经典教学案例：遗传倾向高度依赖训练环境。"
        ),
        "uncertainty_note": (
            "ACTN3×training interaction is primarily documented in small-scale "
            "intervention studies and candidate-gene analyses. Large GWAS do "
            "not detect ACTN3 effects on general-population strength traits. "
            "The interaction is best understood as a sport-science case study "
            "rather than a broadly generalizable population effect."
        ),
    },
}

# =============================================================================
# 6. Evidence Confidence — 证据可信度等级
# =============================================================================
#
# Ratings reflect current scientific consensus (as of 2025-2026):
#   high      — Consistent evidence from multiple independent studies/meta-analyses
#   moderate  — Some evidence requiring further validation; effect sizes may be modest
#   limited   — Biologically plausible but quantitative evidence is sparse
#
# Each rating applies to the body of published literature, not to
# the model parameters themselves (which are pedagogical weights).
# =============================================================================

EVIDENCE_CONFIDENCE: dict[str, dict[str, Union[str, Dict[str, str]]]] = {
    "APOE": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate",
            "population_generalizability": "limited — strongest evidence in European-ancestry populations",
        },
        "note": (
            "APOE is the strongest common genetic association for cognitive traits "
            "in populations of European ancestry. The association is allele-"
            "dependent (ε4 increases susceptibility, ε2 is protective). Lifestyle "
            "modification shows consistent observational associations with "
            "cognitive health trajectories. However, G×E interaction magnitudes "
            "require further quantification, and effect sizes differ across "
            "ancestry groups."
        ),
    },
    "FTO": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate_to_high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate_to_high",
            "population_generalizability": "moderate — replicated across multiple ancestries, effect sizes vary",
        },
        "note": (
            "FTO represents one of the most documented G×E interactions in "
            "complex trait genetics. Physical activity is consistently reported "
            "to attenuate FTO-BMI association across multiple independent "
            "meta-analyses. However, attenuation magnitude varies and requires "
            "further quantification across diverse populations and measurement "
            "methods."
        ),
    },
    "CLOCK": {
        "genetic_evidence": "moderate",
        "interaction_evidence": "limited_to_moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "moderate",
            "gene_environment_interaction": "limited_to_moderate",
            "population_generalizability": "limited — evidence predominantly from candidate gene studies and European GWAS",
        },
        "note": (
            "CLOCK gene function in circadian biology is well-established at the "
            "molecular level. However, common CLOCK variants have small effects "
            "on sleep traits and do NOT reach genome-wide significance in the "
            "largest chronotype GWAS (N~700,000). This illustrates that gene "
            "importance in molecular biology does not equal common-variant effect "
            "size in populations. G×E interaction hypotheses are biologically "
            "plausible but quantitatively limited."
        ),
    },
    "ACTN3": {
        "genetic_evidence": "high",
        "interaction_evidence": "limited_to_moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high — at the protein/biological level; weak at the population trait level",
            "gene_environment_interaction": "limited_to_moderate",
            "population_generalizability": "limited — effects detected in elite athlete comparisons, not general population",
        },
        "note": (
            "ACTN3 R577X is a well-characterized functional variant with clear "
            "molecular consequences (loss of α-actinin-3 protein in XX genotype). "
            "Elite athlete case-control studies have reported modest associations "
            "between ACTN3 R577X genotype and power-oriented athletic performance, "
            "but the effect is context-dependent and does not predict individual "
            "athletic ability. Effects on general-population strength traits are "
            "NOT detected in large GWAS. Training response interaction is "
            "biologically plausible but quantitative evidence from large "
            "population studies is limited."
        ),
    },
}


# =============================================================================
# 7. Health Dimension Configuration — 健康维度
# =============================================================================
#
# Five dimensions form the multi-dimensional simulation output.
# baseline: model-internal reference starting value (not a clinical norm).
# time_sensitivity: relative rate of simulated change over model time scale.
# =============================================================================

DIMENSION_CONFIG: dict[str, DimensionEntry] = {
    "metabolic": {
        "label": "代谢健康",
        "icon": "⚡",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting metabolic regulation capacity "
            "in the model — not a clinical measurement of metabolic health. "
            "反映模型中代谢调节能力的模拟指标。不代表个体的代谢健康测量值。"
        ),
        "time_sensitivity": 1.2,
    },
    "cognitive": {
        "label": "认知健康",
        "icon": "🧠",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting cognitive function and "
            "neuroprotective potential in the model. Not a prediction "
            "of cognitive decline or dementia. "
            "反映模型中认知功能的模拟指标。不构成认知衰退预测。"
        ),
        "time_sensitivity": 1.3,
    },
    "cardiovascular": {
        "label": "心血管健康",
        "icon": "❤️",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting cardiovascular function in "
            "the model. Not a clinical cardiovascular risk assessment. "
            "反映模型中心血管系统功能的模拟指标。不构成心血管事件预测。"
        ),
        "time_sensitivity": 1.25,
    },
    "athletic": {
        "label": "运动潜能",
        "icon": "💪",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting muscle function and physical "
            "performance potential in the model. Athletic performance "
            "depends heavily on training and environment. "
            "反映模型中肌肉功能和体能潜力的模拟指标。运动表现高度依赖"
            "训练环境和后天努力。"
        ),
        "time_sensitivity": 1.1,
    },
    "sleep": {
        "label": "睡眠质量",
        "icon": "🌙",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting circadian rhythm regulation "
            "and sleep quality in the model. Not a clinical sleep "
            "disorder assessment. "
            "反映模型中昼夜节律调节能力和睡眠质量的模拟指标。"
        ),
        "time_sensitivity": 1.15,
    },
}


# =============================================================================
# 8. Simulation Parameters — 模拟运行参数
# =============================================================================
#
# HTI (Health Trajectory Index) is an internally-defined educational
# simulation index. It does NOT correspond to any real clinical score,
# population health metric, or validated risk assessment.
#
# baseline_hti = 72 is a model reference point chosen for pedagogical
# convenience — it places the simulation starting point near the upper
# middle of the 0-100 scale, leaving room to show both improvement
# and decline in educational scenarios.
# =============================================================================

SIMULATION_CONFIG: dict = {
    "time_horizons": [5, 10, 20],
    "baseline_hti": 72,
    "min_hti": 20,
    "max_hti": 95,
    "gene_relative_weight_ceiling": 0.40,
    "environment_relative_weight_ceiling": 0.60,
    "interaction_contribution_range": (-0.15, 0.15),
    "confidence_interval_range": 0.08,
    "base_annual_decay": 0.5,
    # ── Detailed rationale ─────────────────────────────────────────
    "_parameter_notes": {
        "baseline_hti": (
            "Internally-defined educational index chosen for pedagogical "
            "convenience. NOT calibrated to any real population health "
            "distribution or clinical reference range."
        ),
        "gene_relative_weight_ceiling": (
            "Set lower than the environment ceiling (0.40 vs 0.60) as a "
            "PEDAGOGICAL design choice within this simulation model. "
            "It is NOT a biological variance decomposition, heritability "
            "estimate, or claim that genes contribute 40% and environment "
            "contributes 60% to health outcomes."
        ),
        "environment_relative_weight_ceiling": (
            "Set higher than the gene ceiling (0.60 vs 0.40) to reinforce "
            "the educational message that lifestyle factors are potent "
            "modulators in this simulation. NOT an empirical estimate of "
            "environmental variance contribution or population-level "
            "health outcome partitioning."
        ),
        "interaction_contribution_range": (
            "Constrained to ±0.15 because published G×E interaction effects "
            "are typically modest. A wider range would falsely imply strong, "
            "predictable gene×environment synergy. This narrow range "
            "reflects the scientific reality that documented G×E effects "
            "are subtle and context-dependent."
        ),
        "confidence_interval_range": (
            "Model-internal uncertainty estimate. Not a statistical "
            "confidence interval derived from data."
        ),
        "base_annual_decay": (
            "Model-internal trajectory parameter. Calibrated to produce "
            "visually meaningful changes over 5-20 year horizons for "
            "educational demonstration. NOT derived from longitudinal "
            "study data on specific health outcomes."
        ),
    },
}


# =============================================================================
# 9. Trend Level Classification — 趋势等级映射
# =============================================================================
#
# Maps simulated HTI change magnitudes to descriptive labels.
# These are model-internal classification boundaries for relative
# comparison between simulation scenarios — NOT clinical risk levels.
# =============================================================================

TREND_LEVEL_THRESHOLDS: dict[str, tuple[float, float]] = {
    "advantage": (0, 25),
    "favorable": (25, 40),
    "moderate": (40, 60),
    "attention": (60, 75),
    "significant": (75, 100),
}


# =============================================================================
# 10. Environment Factor Ranges — 环境因素标准化量表
# =============================================================================
#
# All factors use a standardized 0-10 input scale.
# "optimal" = model optimal point on this standardized scale —
# NOT a medical recommendation or clinical threshold.
# These are simulation input parameters for pedagogical demonstration.
# =============================================================================

ENVIRONMENT_RANGES: dict[str, EnvironmentRangeEntry] = {
    "exercise": {
        "min": 0, "max": 10, "optimal": 7,
        "unit": "运动频率（标准化模拟量表 0-10）",
        "label": "Exercise",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Not a medical recommendation or clinical threshold. "
            "Higher values reflect more regular physical activity in the simulation."
        ),
    },
    "sleep": {
        "min": 0, "max": 10, "optimal": 8,
        "unit": "睡眠时长与质量（标准化模拟量表 0-10）",
        "label": "Sleep",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Not a medical recommendation or clinical threshold. "
            "Higher values reflect more adequate sleep in the simulation."
        ),
    },
    "diet": {
        "min": 0, "max": 10, "optimal": 8,
        "unit": "饮食质量（标准化模拟量表 0-10）",
        "label": "Diet",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Not a medical recommendation or clinical threshold. "
            "Higher values reflect dietary patterns more aligned with "
            "published nutritional guidelines in the simulation."
        ),
    },
    "stress": {
        "min": 0, "max": 10, "optimal": 3,
        "unit": "压力水平（标准化模拟量表 0-10，低值更有利）",
        "label": "Stress",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Not a medical recommendation or clinical threshold. "
            "Lower values reflect lower chronic stress in the simulation; "
            "optimal at moderate-low, not zero."
        ),
    },
    "smoking": {
        "min": 0, "max": 10, "optimal": 0,
        "unit": "烟草暴露（标准化模拟量表 0-10，低值更有利）",
        "label": "Smoking",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Not a medical recommendation or clinical threshold. "
            "Zero represents no tobacco exposure; scale increases with "
            "exposure level in the simulation."
        ),
    },
}


# =============================================================================
# 11. Counterfactual Simulation — 反事实模拟参数
# =============================================================================
#
# Counterfactual ("what-if") simulations allow users to explore:
# "If I changed one lifestyle factor, how would the simulated trajectory differ?"
# This is an educational exercise — NOT a prediction of intervention effects.
# =============================================================================

COUNTERFACTUAL_CONFIG: dict = {
    "changeable_factors": ["exercise", "sleep", "diet", "stress"],
    "min_meaningful_change": 3,
    "significant_change_threshold": 10,
    "note": (
        "Counterfactual simulations illustrate potential trajectory "
        "differences under alternative scenarios for educational purposes. "
        "Results are model-generated scenarios, not predictions of individual "
        "intervention outcomes."
    ),
}


# =============================================================================
# 12. Model Limitations — 模型局限性声明
# =============================================================================
MODEL_LIMITATIONS = {
    "gwas_associations": (
        "GWAS associations are population-level statistical summaries. "
        "They do not represent individual-level causal effects. Effect "
        "sizes are context-dependent and may not transfer across "
        "ancestry groups or environmental contexts."
    ),
    "gxe_estimates": (
        "Published G×E interaction estimates are typically small in "
        "magnitude, vary substantially across cohorts and measurement "
        "methods, and are predominantly from observational studies. "
        "Causal G×E interactions are difficult to establish."
    ),
    "lifestyle_effects": (
        "Lifestyle-health associations in observational studies are "
        "subject to confounding, reverse causation, and measurement "
        "error. The model's environmental weights are pedagogical, not "
        "empirically validated effect estimates."
    ),
    "population_scope": (
        "Most GWAS data are from European-ancestry populations. Effect "
        "sizes, allele frequencies, and LD patterns differ across "
        "ancestry groups. The model's genetic parameters may not "
        "generalize to populations of non-European ancestry."
    ),
    "limited_snp_count": (
        "This model uses 7 SNPs across 4 genes. A clinical polygenic "
        "risk score would use hundreds to millions of variants. The "
        "small number of variants means only a tiny fraction of genetic "
        "variance is captured — intentional for educational demonstration, "
        "but invalid for risk prediction."
    ),
    "hti_validation": (
        "The Health Trajectory Index (HTI) has NOT been clinically "
        "validated. It does not correspond to any established health "
        "scoring system, diagnostic instrument, or risk assessment "
        "tool. HTI values are pedagogical outputs only."
    ),
    "not_a_diagnostic": (
        "This system is NOT a medical device. It must NOT be used for "
        "clinical decision-making, disease diagnosis, treatment "
        "guidance, or individual risk assessment."
    ),
}


# =============================================================================
# 13. Model Assumptions — 模型假设
# =============================================================================
MODEL_ASSUMPTIONS = {
    "environment_modifiable": (
        "The model assumes that environmental factors (exercise, sleep, "
        "diet, stress, smoking) are modifiable inputs that the user can "
        "adjust. In reality, structural, economic, and social determinants "
        "of health constrain individual choices."
    ),
    "genes_influence_not_determine": (
        "The model treats genetic variants as susceptibility modifiers, "
        "NOT deterministic causes. This reflects the current scientific "
        "consensus that common genetic variants are risk factors, not "
        "causes, of complex traits."
    ),
    "interaction_educational": (
        "G×E interaction coefficients represent educational scenarios "
        "for demonstrating the CONCEPT of gene-environment interaction. "
        "They are not empirical estimates of interaction effect sizes "
        "from specific studies."
    ),
    "linear_additivity": (
        "The model uses linear additive contributions for simplicity. "
        "Real biological relationships are often non-linear, involve "
        "threshold effects, feedback loops, and interactions beyond "
        "pairwise gene×environment terms."
    ),
    "snp_independence": (
        "Variants are treated as having additive effects within genes. "
        "The model does not account for epistasis (gene×gene interaction), "
        "structural variants, rare variants, or non-genetic heritable "
        "factors."
    ),
    "standardized_input_scale": (
        "Environmental inputs use a 0-10 standardized scale for "
        "simplicity. This abstracts away from real measurement units "
        "(MET-hours, dietary recall scores, etc.) and should not be "
        "confused with validated clinical instruments."
    ),
}


# =============================================================================
# 14. Validation Rules — 参数合法性检查
# =============================================================================
VALIDATION_RULES: dict[str, Any] = {
    "hti_range": (0, 100),
    "weight_range": (0.0, 1.0),
    "interaction_range": (-0.2, 0.2),
    "environment_input_range": (0, 10),
    "max_dimensions": 5,
    "max_genes": 4,
    "max_factors": 5,
}


# =============================================================================
# All public symbols exported for engine/gxe_model.py compatibility
# =============================================================================
__all__ = [
    "COUNTERFACTUAL_CONFIG",
    "DIMENSION_CONFIG",
    "ENVIRONMENT_RANGES",
    "ENVIRONMENT_WEIGHTS",
    "EVIDENCE_CONFIDENCE",
    "GENE_WEIGHTS",
    "HTI_MODEL_CONSTANTS",
    "INTERACTION_COEFFICIENTS",
    "MODEL_ASSUMPTIONS",
    "MODEL_LIMITATIONS",
    "MODEL_METADATA",
    "SIMULATION_CONFIG",
    "TREND_LEVEL_THRESHOLDS",
    "VALIDATION_RULES",
]
