# =============================================================================
# engine/config.py — G×E Health Trajectory Simulation Engine Configuration
# =============================================================================
#
# Health Trajectory Index (HTI) — Pediatric Genetic Risk Educational Framework
# ─────────────────────────────────────────────────────────────────────────
# HTI 是一个教育性模拟指标 (pedagogical simulation index)，用于展示：
#   Genetic Predisposition + Early Growth Environment + G×E Interaction
#   在婴儿/儿童早期发育阶段的关系。
#
# 适用场景：新生儿 VCF 基因风险评估（面向非医疗消费者）
# 目标用户：婴儿父母/监护人，了解基因筛查结果与早期干预的重要性
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
#   ✓ Emphasizes modifiable early-growth environmental factors
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

HTI_MODEL_CONSTANTS = {
    "hti_range": (0, 100),
    "hti_typical_range": (20, 95),
    "weight_range": (0.0, 1.0),
    "interaction_range": (-0.15, 0.15),
    "time_horizon_years": [5, 10, 20],
    "base_decay_rate": 0.5,
    "confidence_interval_width": 0.08,
}

# ---------------------------------------------------------------------------
# Design rationale for the gene:environment relative weighting (40:60)
# ────────────────────────────────────────────────────────────────────
# Same pedagogical weighting as adult model — environment is given a larger
# share to emphasize that early intervention and care can significantly
# modulate genetic predisposition in infant development.
# ---------------------------------------------------------------------------


# =============================================================================
# 1. Model Metadata — 模型身份声明
# =============================================================================
MODEL_METADATA: dict[str, object] = {
    "model_type": "educational simulation — pediatric genetic risk awareness",
    "purpose": (
        "illustrate gene-environment interaction concepts in early childhood "
        "development, using newborn genetic screening genes"
    ),
    "clinical_use": False,
    "prediction_scope": (
        "not a disease prediction model — simulates health trajectory "
        "trends for educational demonstration of genetic risk awareness"
    ),
    "evidence_basis": (
        "ACMG SF v3.2 gene list; newborn screening programs (U.S. RUSP, "
        "EU, China); ClinVar pathogenic assertions; published gene-disease "
        "relationships; early intervention outcome studies"
    ),
    "intended_audience": (
        "parents and guardians of newborns, genetic counsellors, "
        "pediatric health educators"
    ),
    "output_interpretation": (
        "Simulated Health Trajectory Index (HTI) values represent educational "
        "scenario outcomes, not individual health forecasts. All scores are "
        "relative model weights, not clinical effect sizes or risk percentages."
    ),
    "version": "3.0.0-pediatric",
}


# =============================================================================
# 2. Typed Definitions — 类型安全配置
# =============================================================================

class GeneWeightEntry(TypedDict, total=False):
    """Per-gene dimension weights + metadata within GENE_WEIGHTS."""

    metabolic: float
    cardiovascular: float
    neurodevelopmental: float
    immunodeficiency: float
    sensory: float
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
    cardiovascular: float
    neurodevelopmental: float
    immunodeficiency: float
    sensory: float
    overall_health: float
    description: str
    reference: str
    parameter_type: str
    uncertainty_note: str


class InteractionEntry(TypedDict, total=False):
    """Per-gene G×E coefficients + metadata within INTERACTION_COEFFICIENTS."""

    nutrition_type: float
    sleep_quality: float
    development_stimulation: float
    medical_adherence: float
    environmental_safety: float
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
# 3. Genetic Predisposition Weights — 遗传倾向贡献 (Pediatric Panel)
# =============================================================================
#
# 25 个儿科/新生儿核心基因，涵盖 ACMG SF v3.2 推荐基因 + 新生儿筛查核心基因。
# 5 个健康维度：metabolic / cardiovascular / neurodevelopmental /
#                immunodeficiency / sensory
#
# IMPORTANT — Please read before interpreting:
# ─────────────────────────────────────────────
# • These are model-internal relative weights designed for educational
#   simulation, NOT estimates of clinical effect size.
# • Weights reflect gene-disease association strength and the breadth of
#   organ system impact, NOT individual risk magnitude.
# • Pathogenic variants in these genes have well-established disease
#   relationships, but penetrance varies and not all variants are pathogenic.
#
# Parameter type: educational_relative_weight
# =============================================================================

GENE_WEIGHTS: dict[str, GeneWeightEntry] = {
    # ═══ 代谢与内分泌 (Metabolic) ═══
    "PAH": {
        "metabolic": 0.55,
        "neurodevelopmental": 0.20,
        "overall_health": 0.35,
        "base_effect": 0.40,
        "time_multiplier": 1.20,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "PAH 编码苯丙氨酸羟化酶，其致病性变异导致苯丙酮尿症(PKU)——"
            "一种可通过新生儿筛查发现并饮食控制的先天性代谢缺陷。"
            "未经治疗的PKU导致严重智力障碍；早期饮食干预可完全预防神经系统损伤。"
            "PAH encodes phenylalanine hydroxylase; pathogenic variants cause PKU, "
            "a treatable inborn error of metabolism detectable by newborn screening."
        ),
        "reference": (
            "Blau et al. (2010) — Lancet 376:1417-1427. "
            "ACMG SF v3.2 — PAH listed as actionable gene."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — dietary management is established treatment",
        },
        "uncertainty_note": (
            "PKU is one of the best-understood G×E interactions: dietary phenylalanine "
            "restriction completely prevents neurological sequelae. Variant severity "
            "correlates with residual enzyme activity and dietary tolerance."
        ),
    },
    "G6PD": {
        "cardiovascular": 0.35,
        "metabolic": 0.25,
        "sensory": 0.10,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "G6PD 编码葡萄糖-6-磷酸脱氢酶，其缺陷是最常见的遗传性酶缺乏症。"
            "G6PD缺乏症患儿接触氧化性药物、蚕豆或感染时可诱发急性溶血性贫血。"
            "避免已知触发因素是核心管理策略——典型的G×E交互案例。"
            "G6PD deficiency is the most common enzymopathy worldwide; "
            "avoidance of oxidative triggers prevents hemolytic crises."
        ),
        "reference": (
            "Luzzatto & Arese (2018) — NEJM 378:60-71. "
            "WHO G6PD Deficiency Guidelines."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — trigger avoidance is established management",
        },
        "uncertainty_note": (
            "Over 200 G6PD variants with varying enzyme activity levels. "
            "Severity depends on specific variant and exposure type/dose."
        ),
    },
    "CYP21A2": {
        "metabolic": 0.50,
        "cardiovascular": 0.15,
        "overall_health": 0.30,
        "base_effect": 0.40,
        "time_multiplier": 1.15,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "CYP21A2 编码21-羟化酶，其致病性变异导致先天性肾上腺皮质增生症(CAH)——"
            "一种可通过新生儿筛查发现的类固醇激素合成障碍。"
            "盐耗型危象可危及生命；早期诊断和激素替代治疗是核心干预措施。"
            "CYP21A2 pathogenic variants cause congenital adrenal hyperplasia; "
            "salt-wasting crises are preventable with early diagnosis and treatment."
        ),
        "reference": (
            "Speiser et al. (2018) — Journal of Clinical Endocrinology & Metabolism. "
            "CAH clinical practice guideline."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — medical adherence prevents crises",
        },
        "uncertainty_note": (
            "Genotype-phenotype correlation is strong but not perfect. "
            "Non-classical (late-onset) forms are milder."
        ),
    },
    "CFTR": {
        "metabolic": 0.45,
        "cardiovascular": 0.15,
        "immunodeficiency": 0.20,
        "sensory": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,
        "time_multiplier": 1.12,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "CFTR 编码囊性纤维化跨膜传导调节因子，致病性变异导致囊性纤维化(CF)——"
            "影响呼吸系统和消化系统的多系统疾病。新生儿筛查可尽早发现，"
            "早期营养支持和呼吸道管理显著改善预后。"
            "CFTR variants cause cystic fibrosis; newborn screening enables early "
            "nutritional and respiratory intervention that improves outcomes."
        ),
        "reference": (
            "Castellani et al. (2018) — Journal of Cystic Fibrosis. "
            "CFTR-related disorders consensus guideline."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early multidisciplinary care improves prognosis",
        },
        "uncertainty_note": (
            "CFTR modulator therapies (ivacaftor, etc.) are variant-specific. "
            "Over 2000 CFTR variants known; functional classification ongoing."
        ),
    },
    "DHCR7": {
        "metabolic": 0.50,
        "neurodevelopmental": 0.25,
        "sensory": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "DHCR7 编码7-脱氢胆固醇还原酶，致病性变异导致Smith-Lemli-Opitz综合征——"
            "一种胆固醇合成障碍疾病，表现为发育迟缓、小头畸形等多系统异常。"
            "胆固醇补充治疗可改善部分症状。"
            "DHCR7 pathogenic variants cause Smith-Lemli-Opitz syndrome, "
            "a cholesterol synthesis disorder; dietary cholesterol supplementation may help."
        ),
        "reference": (
            "Porter & Herman (2011) — Journal of Lipid Research. "
            "Smith-Lemli-Opitz syndrome review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — cholesterol supplementation shows variable benefit",
        },
        "uncertainty_note": (
            "Phenotypic spectrum is broad. Prenatal and postnatal cholesterol "
            "supplementation efficacy varies by residual enzyme activity."
        ),
    },
    "ACADM": {
        "metabolic": 0.50,
        "cardiovascular": 0.10,
        "neurodevelopmental": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,
        "time_multiplier": 1.12,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "ACADM 编码中链酰基辅酶A脱氢酶，致病性变异导致MCAD缺乏症——"
            "一种脂肪酸氧化障碍疾病。空腹可诱发低血糖和代谢危象；"
            "规律喂养和避免长时间空腹是核心预防措施。"
            "ACADM variants cause MCAD deficiency; avoidance of fasting prevents "
            "metabolic crises. A model G×E interaction: dietary management is key."
        ),
        "reference": (
            "Grosse et al. (2010) — Genetics in Medicine. "
            "MCAD deficiency newborn screening outcomes review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — feeding schedule prevents crises",
        },
        "uncertainty_note": (
            "Common c.985A>G mutation accounts for ~90% of cases in Northern Europeans. "
            "Newborn screening has dramatically reduced mortality."
        ),
    },
    "SLC2A1": {
        "metabolic": 0.45,
        "neurodevelopmental": 0.35,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "SLC2A1 编码葡萄糖转运蛋白1(GLUT1)，致病性变异导致GLUT1缺乏症——"
            "一种影响大脑葡萄糖供应的疾病，表现为早发性癫痫和发育迟缓。"
            "生酮饮食是有效的治疗策略——典型的饮食干预G×E案例。"
            "SLC2A1 variants cause GLUT1 deficiency syndrome; ketogenic diet is "
            "an effective treatment — a classic dietary G×E interaction."
        ),
        "reference": (
            "Klepper et al. (2020) — Epilepsia. "
            "GLUT1 deficiency syndrome management guidelines."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — ketogenic diet is established treatment",
        },
        "uncertainty_note": (
            "Phenotype ranges from severe early-onset epilepsy to mild paroxysmal "
            "exercise-induced dyskinesia. Ketogenic diet response varies."
        ),
    },

    # ═══ 心血管与血液 (Cardiovascular) ═══
    "HBB": {
        "cardiovascular": 0.50,
        "metabolic": 0.10,
        "neurodevelopmental": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.40,
        "time_multiplier": 1.15,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "HBB 编码β-珠蛋白，致病性变异导致镰状细胞病和β-地中海贫血——"
            "全球最常见的严重单基因遗传病。新生儿筛查、预防性抗生素和疫苗接种"
            "显著降低儿童死亡率。"
            "HBB variants cause sickle cell disease and β-thalassemia; newborn screening "
            "and prophylactic care dramatically improve outcomes."
        ),
        "reference": (
            "Piel et al. (2017) — NEJM 376:1561-1573. "
            "Global epidemiology of sickle cell disease."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — medical management prevents complications",
        },
        "uncertainty_note": (
            "Disease severity modified by HbF levels, α-globin gene copy number, "
            "and coinherited variants. Hydroxyurea therapy is a major advance."
        ),
    },
    "FBN1": {
        "cardiovascular": 0.45,
        "sensory": 0.25,
        "neurodevelopmental": 0.05,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "FBN1 编码原纤蛋白-1，致病性变异导致马凡综合征——"
            "一种结缔组织疾病，以主动脉根部扩张、晶状体脱位和骨骼特征为主要表现。"
            "定期心脏监测和预防性β受体阻滞剂/ARB治疗可延缓主动脉扩张。"
            "FBN1 variants cause Marfan syndrome; regular cardiac monitoring and "
            "prophylactic medication improve vascular outcomes."
        ),
        "reference": (
            "Loeys et al. (2010) — Journal of Medical Genetics. "
            "Revised Ghent criteria for Marfan syndrome."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — medical surveillance prevents aortic events",
        },
        "uncertainty_note": (
            "Considerable clinical variability even within families. "
            "Early diagnosis and prophylactic treatment significantly improve life expectancy."
        ),
    },
    "MYH7": {
        "cardiovascular": 0.50,
        "neurodevelopmental": 0.05,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "MYH7 编码β-肌球蛋白重链，致病性变异是家族性肥厚型心肌病最常见的"
            "遗传原因。婴儿期即可表现，是婴幼儿心衰和猝死的重要原因之一。"
            "定期心脏评估和活动限制是标准管理方案。"
            "MYH7 variants are the most common cause of familial hypertrophic "
            "cardiomyopathy; can present in infancy with heart failure."
        ),
        "reference": (
            "Maron et al. (2014) — Journal of the American College of Cardiology. "
            "HCM clinical practice guidelines."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — activity modification and surveillance recommended",
        },
        "uncertainty_note": (
            "Genotype-phenotype correlation is imperfect; some variant carriers "
            "remain asymptomatic. Early-onset forms tend to be more severe."
        ),
    },
    "CHD7": {
        "cardiovascular": 0.40,
        "sensory": 0.30,
        "neurodevelopmental": 0.20,
        "metabolic": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,
        "time_multiplier": 1.12,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "CHD7 编码染色质解旋酶DNA结合蛋白7，致病性变异导致CHARGE综合征——"
            "一种涉及眼缺损、心脏缺陷、后鼻孔闭锁、发育迟缓、生殖器异常和"
            "耳部异常的多系统先天性疾病。多学科综合管理是关键。"
            "CHD7 variants cause CHARGE syndrome — a multisystem disorder requiring "
            "coordinated multidisciplinary care from infancy."
        ),
        "reference": (
            "Hale et al. (2016) — American Journal of Medical Genetics. "
            "CHARGE syndrome clinical diagnostic criteria update."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early intervention improves outcomes",
        },
        "uncertainty_note": (
            "Clinical spectrum ranges from severe neonatal presentation to mild. "
            "Individualized care plans are essential due to variable organ involvement."
        ),
    },

    # ═══ 神经发育 (Neurodevelopmental) ═══
    "SMN1": {
        "neurodevelopmental": 0.55,
        "metabolic": 0.05,
        "overall_health": 0.35,
        "base_effect": 0.50,
        "time_multiplier": 1.25,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "SMN1 编码运动神经元存活蛋白1，其纯合缺失/致病性变异导致脊髓性肌萎缩(SMA)——"
            "婴幼儿最常见的致死性神经肌肉疾病。新生儿筛查+早期基因治疗/药物干预"
            "(nusinersen, onasemnogene, risdiplam)可显著改变病程。"
            "SMA is the most common lethal neuromuscular disease in infants; "
            "newborn screening + early gene-targeted therapy dramatically alters outcomes."
        ),
        "reference": (
            "Mendell et al. (2017) — NEJM 377:1713-1722. "
            "Gene therapy for SMA type 1 clinical trial."
        ),
        "evidence_confidence": {
            "genetic_association": "high — homozygous SMN1 deletion is diagnostic",
            "gene_environment_interaction": "high — treatment timing is critical; pre-symptomatic treatment is best",
        },
        "uncertainty_note": (
            "SMN2 copy number modifies disease severity (SMA type 0-IV). "
            "Treatment window is narrow — newborn screening is transformative."
        ),
    },
    "SCN1A": {
        "neurodevelopmental": 0.50,
        "cardiovascular": 0.05,
        "overall_health": 0.30,
        "base_effect": 0.40,
        "time_multiplier": 1.15,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "SCN1A 编码电压门控钠通道α亚基，致病性变异导致Dravet综合征——"
            "一种婴儿期起病的药物难治性癫痫，常伴发热敏感和发育倒退。"
            "避免过热和特定抗癫痫药物(钠通道阻滞剂)是关键管理原则。"
            "SCN1A variants cause Dravet syndrome; fever management and avoidance "
            "of sodium channel blocker anticonvulsants are critical."
        ),
        "reference": (
            "Claes et al. (2001) — American Journal of Human Genetics. "
            "De novo SCN1A mutations in Dravet syndrome."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — fever management reduces seizure triggers",
        },
        "uncertainty_note": (
            "Seizure frequency and developmental outcomes vary widely. "
            "Early diagnosis guides anticonvulsant choice and fever precautions."
        ),
    },
    "MECP2": {
        "neurodevelopmental": 0.55,
        "metabolic": 0.10,
        "sensory": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.45,
        "time_multiplier": 1.18,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "MECP2 编码甲基CpG结合蛋白2，致病性变异导致Rett综合征——"
            "一种主要影响女性的严重神经发育障碍，特征为6-18月龄出现发育倒退、"
            "手部刻板动作和语言丧失。早期康复干预可改善功能预后。"
            "MECP2 variants cause Rett syndrome; early developmental intervention "
            "and supportive care improve quality of life outcomes."
        ),
        "reference": (
            "Amir et al. (1999) — Nature Genetics 23:185-188. "
            "MECP2 mutations in Rett syndrome. "
            "Neul et al. (2010) — Annals of Neurology. Rett syndrome diagnostic criteria."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early rehabilitation and communication support improve outcomes",
        },
        "uncertainty_note": (
            "Phenotype ranges from classic Rett to milder variants. "
            "X-inactivation patterns influence severity in females."
        ),
    },
    "FMR1": {
        "neurodevelopmental": 0.55,
        "sensory": 0.15,
        "overall_health": 0.25,
        "base_effect": 0.40,
        "time_multiplier": 1.12,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "FMR1 编码FMRP蛋白，其CGG重复扩增(>200)导致脆性X综合征——"
            "最常见的遗传性智力障碍。早期行为干预、言语治疗和特殊教育支持"
            "可显著改善发育轨迹。"
            "FMR1 CGG expansion causes Fragile X syndrome, the most common inherited "
            "intellectual disability; early intervention improves developmental outcomes."
        ),
        "reference": (
            "Hagerman et al. (2017) — Nature Reviews Disease Primers. "
            "Fragile X syndrome comprehensive review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early behavioral and educational intervention improves outcomes",
        },
        "uncertainty_note": (
            "CGG repeat size categories: normal (<45), intermediate (45-54), "
            "premutation (55-200, risk of FXTAS/POI), full mutation (>200). "
            "Mosaicism and methylation status affect phenotype."
        ),
    },
    "TSC1": {
        "neurodevelopmental": 0.45,
        "sensory": 0.20,
        "cardiovascular": 0.10,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "TSC1 编码错构瘤蛋白(hamartin)，致病性变异导致结节性硬化症——"
            "一种多系统错构瘤疾病，影响大脑、皮肤、肾脏、心脏和肺。"
            "婴儿痉挛是常见首发表现；mTOR抑制剂可靶向治疗相关肿瘤。"
            "TSC1 variants cause tuberous sclerosis complex; mTOR inhibitor therapy "
            "is a targeted treatment for associated tumors and epilepsy."
        ),
        "reference": (
            "Northrup et al. (2021) — Nature Reviews Disease Primers. "
            "Tuberous sclerosis complex update."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early seizure control and surveillance improve outcomes",
        },
        "uncertainty_note": (
            "TSC1 variants tend to cause milder disease than TSC2. "
            "mTOR inhibitor (everolimus) effectiveness is well-established for SEGA and AML."
        ),
    },
    "NF1": {
        "neurodevelopmental": 0.40,
        "sensory": 0.25,
        "cardiovascular": 0.10,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "NF1 编码神经纤维瘤蛋白，致病性变异导致神经纤维瘤病1型——"
            "一种常见的常染色体显性遗传肿瘤易感综合征。表现为咖啡牛奶斑、"
            "神经纤维瘤和视路胶质瘤。定期监测和早期干预是管理核心。"
            "NF1 variants cause neurofibromatosis type 1; regular surveillance "
            "and early intervention for complications are standard of care."
        ),
        "reference": (
            "Gutmann et al. (2017) — Nature Reviews Disease Primers. "
            "Neurofibromatosis type 1 review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — surveillance and early excision prevent complications",
        },
        "uncertainty_note": (
            "Extreme clinical variability — some individuals have only café-au-lait "
            "spots, others develop plexiform neurofibromas or MPNST. "
            "Selumetinib recently approved for inoperable plexiform neurofibromas."
        ),
    },

    # ═══ 免疫与感染 (Immunodeficiency) ═══
    "IL2RG": {
        "immunodeficiency": 0.55,
        "neurodevelopmental": 0.05,
        "metabolic": 0.05,
        "overall_health": 0.35,
        "base_effect": 0.50,
        "time_multiplier": 1.22,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "IL2RG 编码白细胞介素-2受体共同γ链，致病性变异导致X连锁严重联合免疫缺陷"
            "(SCID-X1)——患儿缺乏功能性T细胞和NK细胞，出生后数月内即面临致死性感染。"
            "新生儿筛查(TREC检测)+早期造血干细胞移植/基因治疗可挽救生命。"
            "IL2RG variants cause X-linked SCID; newborn TREC screening + early HSCT "
            "or gene therapy is lifesaving. A quintessential G×E: early medical "
            "intervention completely changes the outcome."
        ),
        "reference": (
            "Hacein-Bey-Abina et al. (2010) — NEJM 363:355-364. "
            "Gene therapy for X-linked SCID. "
            "Kwan et al. (2014) — JAMA 312:729-738. Newborn SCID screening outcomes."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early intervention is lifesaving",
        },
        "uncertainty_note": (
            "TREC-based newborn screening identifies SCID before symptoms appear. "
            "Survival >95% with early HSCT before 3.5 months of age."
        ),
    },
    "BTK": {
        "immunodeficiency": 0.55,
        "cardiovascular": 0.05,
        "overall_health": 0.30,
        "base_effect": 0.40,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "BTK 编码Bruton酪氨酸激酶，致病性变异导致X连锁无丙种球蛋白血症(XLA)——"
            "B细胞发育停滞，抗体缺乏，男性患儿反复发生细菌感染。"
            "免疫球蛋白替代治疗是标准方案。"
            "BTK variants cause XLA; immunoglobulin replacement therapy prevents "
            "infections and supports normal development."
        ),
        "reference": (
            "Conley et al. (2009) — Annual Review of Immunology. "
            "X-linked agammaglobulinemia review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — IVIG therapy is established standard of care",
        },
        "uncertainty_note": (
            "Diagnosis often delayed until after 6 months when maternal IgG wanes. "
            "Lifelong IVIG/SCIG replacement is highly effective."
        ),
    },
    "RAG1": {
        "immunodeficiency": 0.55,
        "neurodevelopmental": 0.05,
        "overall_health": 0.35,
        "base_effect": 0.45,
        "time_multiplier": 1.18,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "RAG1 编码重组激活基因1，致病性变异导致多种形式的SCID或Omenn综合征。"
            "TREC新生儿筛查可早期发现；造血干细胞移植是当前标准治疗。"
            "RAG1 variants cause various SCID forms; newborn screening + early HSCT "
            "are the standard approach."
        ),
        "reference": (
            "Schuetz et al. (2014) — Blood. "
            "RAG deficiency clinical spectrum and treatment outcomes."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early transplant prevents complications",
        },
        "uncertainty_note": (
            "Phenotype ranges from classic SCID to Omenn syndrome (erythroderma, "
            "eosinophilia, hepatosplenomegaly) to delayed-onset combined immunodeficiency."
        ),
    },

    # ═══ 感官与结构 (Sensory) ═══
    "GJB2": {
        "sensory": 0.55,
        "neurodevelopmental": 0.15,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "GJB2 编码连接蛋白26(Cx26)，致病性变异是遗传性先天性听力损失最常见的"
            "病因。新生儿听力筛查+早期听力辅助(助听器/人工耳蜗)和语言康复可"
            "显著改善语言发育和社交沟通。"
            "GJB2 variants are the most common cause of congenital hearing loss; "
            "newborn hearing screening + early intervention enables normal language development."
        ),
        "reference": (
            "Kenneson et al. (2002) — Genetics in Medicine. "
            "GJB2 (connexin 26) prevalence and mutation spectrum. "
            "Joint Committee on Infant Hearing (2019) position statement."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early amplification and therapy transform outcomes",
        },
        "uncertainty_note": (
            "GJB2 hearing loss is usually non-progressive. Early cochlear implantation "
            "(<12 months) results in near-normal language outcomes."
        ),
    },
    "SLC26A4": {
        "sensory": 0.50,
        "neurodevelopmental": 0.10,
        "metabolic": 0.05,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.08,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "SLC26A4 编码pendrin蛋白，致病性变异导致Pendred综合征——"
            "以先天性感音神经性听力损失和甲状腺肿为特征。"
            "新生儿听力筛查和早期听力干预是改善预后的关键。"
            "SLC26A4 variants cause Pendred syndrome with congenital hearing loss; "
            "early hearing intervention and thyroid monitoring are standard care."
        ),
        "reference": (
            "Suzuki et al. (2017) — GeneReviews. "
            "Pendred syndrome / nonsyndromic enlarged vestibular aqueduct."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early amplification improves language outcomes",
        },
        "uncertainty_note": (
            "Hearing loss may be progressive and exacerbated by head trauma. "
            "Enlarged vestibular aqueduct (EVA) is a characteristic imaging finding."
        ),
    },
    "COL1A1": {
        "sensory": 0.50,
        "cardiovascular": 0.10,
        "neurodevelopmental": 0.05,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "COL1A1 编码I型胶原α1链，致病性变异导致成骨不全症(OI)——"
            "以骨骼脆弱、反复骨折、蓝巩膜和听力损失为特征。"
            "多学科管理包括物理治疗、支具辅助和双膦酸盐药物。"
            "COL1A1 variants cause osteogenesis imperfecta; multidisciplinary care "
            "including physiotherapy and bisphosphonate therapy improves outcomes."
        ),
        "reference": (
            "Forlino & Marini (2016) — Lancet 387:1657-1671. "
            "Osteogenesis imperfecta review."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — physiotherapy and protective measures reduce fractures",
        },
        "uncertainty_note": (
            "Severity spans from perinatal lethal (type II) to mild non-deforming "
            "(type I). COL1A1 haploinsufficiency forms are generally milder."
        ),
    },
    "USH2A": {
        "sensory": 0.55,
        "neurodevelopmental": 0.05,
        "overall_health": 0.25,
        "base_effect": 0.35,
        "time_multiplier": 1.10,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "USH2A 编码usherin蛋白，致病性变异是Usher综合征II型的主要原因——"
            "导致先天性中度-重度听力损失和青春期起病的视网膜色素变性。"
            "早期听力干预和定期眼科监测对维持功能至关重要。"
            "USH2A variants cause Usher syndrome type II; early cochlear implantation "
            "and regular ophthalmologic surveillance are essential."
        ),
        "reference": (
            "Mathur & Yang (2015) — Biochimica et Biophysica Acta. "
            "Usher syndrome: hearing loss, retinitis pigmentosa, and therapeutic approaches."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early sensory support preserves function",
        },
        "uncertainty_note": (
            "Dual sensory loss requires coordinated audiology and ophthalmology care. "
            "Gene therapy trials for USH2A-related retinitis pigmentosa are underway."
        ),
    },
    "RB1": {
        "sensory": 0.50,
        "neurodevelopmental": 0.05,
        "overall_health": 0.30,
        "base_effect": 0.45,
        "time_multiplier": 1.12,
        "parameter_type": "educational_relative_weight",
        "interpretation": "simulation coefficient, not biological effect size",
        "description": (
            "RB1 编码视网膜母细胞瘤蛋白(pRb)，致病性变异导致视网膜母细胞瘤——"
            "婴幼儿最常见的眼内恶性肿瘤。定期眼底筛查(从出生开始)和早期治疗"
            "可挽救视力和生命。"
            "RB1 variants cause retinoblastoma, the most common infant eye cancer; "
            "regular surveillance from birth enables early vision-sparing treatment."
        ),
        "reference": (
            "Dimaras et al. (2015) — Nature Reviews Disease Primers. "
            "Retinoblastoma review. "
            "Skalet et al. (2018) — Ophthalmology. RB1 screening guidelines."
        ),
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — screening and early treatment save vision and life",
        },
        "uncertainty_note": (
            "Hereditary RB (bilateral, earlier onset) vs sporadic (unilateral). "
            "Surveillance schedule depends on risk category."
        ),
    },
}

# =============================================================================
# 4. Environment Factor Weights — 婴儿早期成长环境因素
# =============================================================================
#
# These are model-internal relative coefficients representing how each
# infant growth factor contributes to each health dimension in the simulation.
#
# Environmental factors are deliberately weighted more heavily than
# genetic factors in this model to emphasize their modifiability —
# a pedagogical design choice particularly relevant to infant development.
# =============================================================================

ENVIRONMENT_WEIGHTS: dict[str, EnvironmentWeightEntry] = {
    "nutrition_type": {
        "metabolic": 0.40,
        "neurodevelopmental": 0.30,
        "immunodeficiency": 0.20,
        "cardiovascular": 0.15,
        "sensory": 0.15,
        "overall_health": 0.30,
        "parameter_type": "educational_relative_weight",
        "description": (
            "喂养方式对婴儿代谢和神经发育有深远影响。母乳喂养提供免疫保护、"
            "最佳营养配比和神经发育必需的脂肪酸。对于某些代谢性疾病，"
            "特殊配方奶粉是医学必需品。喂养方式是最基础的可改变因素。"
            "Infant feeding type profoundly impacts metabolic and neurodevelopmental "
            "trajectories. Breastfeeding provides immune protection and optimal nutrition."
        ),
        "reference": (
            "WHO/UNICEF breastfeeding guidelines; "
            "AAP policy statement on breastfeeding"
        ),
        "uncertainty_note": (
            "Breastfeeding benefits are well-documented but observational studies "
            "are subject to confounding by socioeconomic factors. For specific inborn "
            "errors of metabolism, specialized formula is medically necessary."
        ),
    },
    "sleep_quality": {
        "metabolic": 0.15,
        "neurodevelopmental": 0.40,
        "cardiovascular": 0.10,
        "immunodeficiency": 0.15,
        "sensory": 0.10,
        "overall_health": 0.25,
        "parameter_type": "educational_relative_weight",
        "description": (
            "婴儿睡眠质量直接影响大脑发育、突触可塑性和生长激素分泌。"
            "规律睡眠习惯的建立对神经发育有促进作用，睡眠不足可能加重"
            "某些神经发育疾病的症状(如SCN1A相关的癫痫发作阈值)。"
            "Infant sleep quality directly affects brain development, synaptic "
            "plasticity, and growth hormone secretion. Sleep deprivation may "
            "lower seizure threshold in susceptible infants."
        ),
        "reference": (
            "Evidence based on pediatric sleep research "
            "and infant development cohort studies"
        ),
        "uncertainty_note": (
            "Infant sleep patterns vary widely and are influenced by temperament, "
            "feeding method, and parental practices. Optimal ranges are approximate."
        ),
    },
    "development_stimulation": {
        "metabolic": 0.05,
        "neurodevelopmental": 0.45,
        "cardiovascular": 0.05,
        "immunodeficiency": 0.05,
        "sensory": 0.25,
        "overall_health": 0.25,
        "parameter_type": "educational_relative_weight",
        "description": (
            "早期感官刺激、互动游戏和语言暴露对婴儿神经发育至关重要。"
            "对于有神经发育风险基因(如FMR1、MECP2、SMN1)的婴儿，"
            "丰富的早期刺激环境和康复训练可显著改善发育轨迹。"
            "Early sensory stimulation, interactive play, and language exposure are "
            "critical for infant neurodevelopment, particularly for those with "
            "neurodevelopmental genetic risk variants."
        ),
        "reference": (
            "Evidence based on early intervention outcome studies; "
            "Heckman equation — early investment in human capital"
        ),
        "uncertainty_note": (
            "Stimulation effects are difficult to quantify precisely. "
            "Optimal amount and type vary by developmental stage and individual needs. "
            "The 'enrichment' concept is supported by animal models and human cohort studies."
        ),
    },
    "medical_adherence": {
        "metabolic": 0.35,
        "neurodevelopmental": 0.25,
        "cardiovascular": 0.20,
        "immunodeficiency": 0.35,
        "sensory": 0.20,
        "overall_health": 0.35,
        "parameter_type": "educational_relative_weight",
        "description": (
            "对新生儿筛查异常结果的随访依从性、定期专科评估、按时用药和"
            "疫苗接种是调节遗传风险的直接方式。对于PKU、CAH、SCID等可治疗"
            "遗传病，医疗依从性直接决定预后。"
            "Adherence to newborn screening follow-up, specialist appointments, "
            "medication schedules, and vaccination directly modulates genetic risk. "
            "For treatable conditions like PKU, CAH, and SCID, adherence determines outcomes."
        ),
        "reference": (
            "Evidence from newborn screening outcome studies; "
            "WHO immunization guidelines; treatment adherence research"
        ),
        "uncertainty_note": (
            "Medical adherence is influenced by healthcare access, parental health "
            "literacy, and socioeconomic factors — not purely individual choice."
        ),
    },
    "environmental_safety": {
        "metabolic": 0.10,
        "neurodevelopmental": 0.30,
        "cardiovascular": 0.15,
        "immunodeficiency": 0.30,
        "sensory": 0.20,
        "overall_health": 0.25,
        "parameter_type": "educational_relative_weight",
        "description": (
            "家居环境安全包括避免毒素暴露(铅、农药)、过敏原控制、安全睡眠环境"
            "(SIDS预防)和感染防护。对于免疫缺陷(G6PD、IL2RG、BTK、RAG1)和"
            "代谢性疾病患儿，环境安全是预防急性事件的第一道防线。"
            "Environmental safety includes toxin avoidance, allergen control, safe "
            "sleep practices, and infection protection — critical for infants with "
            "immunodeficiency or metabolic conditions."
        ),
        "reference": (
            "AAP policy statements on safe sleep and environmental health; "
            "CDC childhood lead poisoning prevention guidelines"
        ),
        "uncertainty_note": (
            "Environmental exposures are difficult to measure comprehensively. "
            "Effects are often cumulative and may interact with genetic susceptibility "
            "in complex ways not fully captured by simple exposure metrics."
        ),
    },
}

# =============================================================================
# 5. Gene × Environment Interaction Coefficients — 基因×环境交互
# =============================================================================
#
# 25 genes × 5 infant factors interaction matrix.
# Sign convention:
#   Positive: favourable environment may buffer genetic predisposition
#   Negative: unfavourable environment may amplify genetic susceptibility
#
# These are MODEL PARAMETERS only — pedagogical coefficients, NOT validated
# biological interaction effect sizes.
# =============================================================================

INTERACTION_COEFFICIENTS: dict[str, InteractionEntry] = {
    # ═══ Metabolic genes ═══
    "PAH": {
        "nutrition_type": 0.15,
        "sleep_quality": 0.05,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "PAH(PKU)的G×E交互是最经典案例：严格的苯丙氨酸限制饮食可完全预防"
            "神经系统损伤。医疗依从性和饮食管理是核心环境调节因素。"
            "Dietary phenylalanine restriction is the prototypical G×E interaction "
            "in human genetics."
        ),
        "uncertainty_note": (
            "Dietary response is genotype-dependent. Some variants (e.g., mild "
            "hyperphenylalaninemia) require less strict restriction."
        ),
    },
    "G6PD": {
        "nutrition_type": 0.08,
        "sleep_quality": 0.03,
        "development_stimulation": 0.03,
        "medical_adherence": 0.12,
        "environmental_safety": 0.15,
        "parameter_type": "model_parameter",
        "description": (
            "G6PD缺乏症是药物/食物×基因交互的经典案例：避免氧化性触发因素"
            "(蚕豆、某些药物、樟脑丸)可预防急性溶血。"
            "G6PD deficiency exemplifies trigger×gene interaction: avoiding oxidative "
            "triggers prevents hemolytic crises."
        ),
        "uncertainty_note": (
            "Trigger sensitivity varies by variant class (I-IV) and residual enzyme "
            "activity. Not all G6PD-deficient individuals react to all triggers."
        ),
    },
    "CYP21A2": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.08,
        "parameter_type": "model_parameter",
        "description": (
            "CAH的G×E交互核心在于激素替代治疗的依从性：规律用药预防盐耗危象，"
            "应激剂量调整应对感染/手术等应激状态。"
            "Hormone replacement adherence and stress dosing for illness/surgery "
            "are critical environmental modulators of CAH outcomes."
        ),
        "uncertainty_note": "Stress dosing requirements vary by CAH form (salt-wasting vs simple virilising).",
    },
    "CFTR": {
        "nutrition_type": 0.12,
        "sleep_quality": 0.05,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.08,
        "parameter_type": "model_parameter",
        "description": (
            "CF的G×E交互涉及多方面环境调节：营养支持(胰酶、高热量饮食)、"
            "呼吸道清理、避免感染、CFTR调节剂药物等综合管理是改善预后的核心。"
            "Multidisciplinary care — nutrition, airway clearance, infection prevention, "
            "and CFTR modulators — synergistically improves CF outcomes."
        ),
        "uncertainty_note": "CFTR modulator eligibility depends on specific variants. Care complexity is high.",
    },
    "DHCR7": {
        "nutrition_type": 0.10,
        "sleep_quality": 0.03,
        "development_stimulation": 0.08,
        "medical_adherence": 0.12,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "胆固醇补充治疗是DHCR7(SLOS)的核心G×E交互案例。"
            "Cholesterol supplementation exemplifies G×E interaction in SLOS."
        ),
        "uncertainty_note": "Variable response to cholesterol supplementation; benefit may be limited in severe forms.",
    },
    "ACADM": {
        "nutrition_type": 0.12,
        "sleep_quality": 0.05,
        "development_stimulation": 0.03,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "MCAD缺乏症的G×E交互极为明确：规律喂养、避免空腹是预防代谢危象的"
            "核心。新生儿筛查+喂养指导几乎消除了MCAD相关死亡率。"
            "Avoidance of fasting is the key G×E interaction in MCAD deficiency. "
            "Newborn screening + feeding guidance has nearly eliminated mortality."
        ),
        "uncertainty_note": "Fasting tolerance varies by residual enzyme activity and intercurrent illness.",
    },
    "SLC2A1": {
        "nutrition_type": 0.15,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.12,
        "environmental_safety": 0.03,
        "parameter_type": "model_parameter",
        "description": (
            "生酮饮食是GLUT1缺乏症的标志性G×E交互——通过改变代谢底物绕过"
            "葡萄糖转运缺陷，直接改善癫痫控制和发育。"
            "Ketogenic diet is the signature G×E interaction for GLUT1 deficiency."
        ),
        "uncertainty_note": "Ketogenic diet adherence is challenging. Response varies by age at initiation.",
    },

    # ═══ Cardiovascular genes ═══
    "HBB": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.05,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.10,
        "parameter_type": "model_parameter",
        "description": (
            "镰状细胞病的G×E交互：预防性抗生素、疫苗接种、羟基脲治疗和"
            "避免脱水/低氧/寒冷等触发因素共同管理疾病。"
            "Prophylactic antibiotics, vaccination, hydroxyurea, and trigger avoidance "
            "are key environmental modulators in sickle cell disease."
        ),
        "uncertainty_note": "Outcomes vary by healthcare access and disease-modifying therapy availability.",
    },
    "FBN1": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.05,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "马凡综合征的G×E交互：定期心脏影像监测、β受体阻滞剂/ARB预防性治疗、"
            "避免高强度对抗性运动可延缓主动脉扩张。"
            "Regular cardiac surveillance, prophylactic medication, and activity "
            "modification are key G×E interactions in Marfan syndrome."
        ),
        "uncertainty_note": "Aortic dilation rate varies individually. Genetic modifiers not fully understood.",
    },
    "MYH7": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.12,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "肥厚型心肌病的G×E交互：定期心脏评估、避免竞技性运动和脱水是"
            "管理核心。"
            "Regular cardiac evaluation and activity modification are primary "
            "environmental modulators in HCM."
        ),
        "uncertainty_note": "Penetrance is age-dependent and incomplete. Risk stratification guides management.",
    },
    "CHD7": {
        "nutrition_type": 0.08,
        "sleep_quality": 0.05,
        "development_stimulation": 0.10,
        "medical_adherence": 0.15,
        "environmental_safety": 0.08,
        "parameter_type": "model_parameter",
        "description": (
            "CHARGE综合征需要多学科综合管理：心脏手术、听力辅助、胃造口喂养、"
            "发育支持——环境干预涉及多个系统的协同。"
            "Multidisciplinary care coordination is the core environmental modulator "
            "in CHARGE syndrome."
        ),
        "uncertainty_note": "Individual organ involvement varies. Care plans are highly individualized.",
    },

    # ═══ Neurodevelopmental genes ═══
    "SMN1": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.05,
        "development_stimulation": 0.10,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "SMA是最具时间紧迫性的G×E交互案例：症状前治疗(新生儿筛查+早期用药)"
            "vs 症状后治疗的预后差异巨大。发育支持(物理治疗、呼吸管理)也至关重要。"
            "Pre-symptomatic treatment is the most impactful G×E interaction in SMA — "
            "timing is everything."
        ),
        "uncertainty_note": "SMN2 copy number modifies severity and treatment urgency.",
    },
    "SCN1A": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.12,
        "development_stimulation": 0.08,
        "medical_adherence": 0.15,
        "environmental_safety": 0.10,
        "parameter_type": "model_parameter",
        "description": (
            "Dravet综合征的多因素G×E交互：避免过热(洗澡水温、环境温度)、"
            "选择适当抗癫痫药物(避免钠通道阻滞剂)、发热管理、睡眠充足——"
            "这些都是明确的癫痫发作控制环境因素。"
            "Fever management, anticonvulsant selection, and sleep hygiene are "
            "established environmental modulators in Dravet syndrome."
        ),
        "uncertainty_note": "Seizure control is multifactorial; some triggers are unavoidable.",
    },
    "MECP2": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.08,
        "development_stimulation": 0.15,
        "medical_adherence": 0.10,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "Rett综合征的G×E交互主要在于早期康复干预：物理治疗、沟通辅助、"
            "手部功能训练等发育支持可改善功能预后。"
            "Early developmental intervention is the most impactful environmental "
            "modulator in Rett syndrome."
        ),
        "uncertainty_note": "Regression phase timing varies. Intervention benefits are well-supported but variable.",
    },
    "FMR1": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.10,
        "development_stimulation": 0.15,
        "medical_adherence": 0.10,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "脆性X综合征的G×E交互：早期行为干预、言语治疗、特殊教育和"
            "感觉统合训练是改善发育轨迹的核心环境因素。"
            "Early behavioral intervention, speech therapy, and special education "
            "are key environmental modulators in Fragile X syndrome."
        ),
        "uncertainty_note": "Intervention response varies individually. Early initiation is consistently beneficial.",
    },
    "TSC1": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.08,
        "development_stimulation": 0.10,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "结节性硬化症的G×E交互：婴儿痉挛的早期识别和治疗、mTOR抑制剂靶向治疗、"
            "定期多系统监测是管理核心。"
            "Early infantile spasm treatment, mTOR inhibitor therapy, and regular "
            "surveillance are key environmental modulators in TSC."
        ),
        "uncertainty_note": "mTOR inhibitor therapy is effective but requires monitoring for side effects.",
    },
    "NF1": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.05,
        "development_stimulation": 0.10,
        "medical_adherence": 0.12,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "NF1的G×E交互核心在于定期肿瘤筛查(视路胶质瘤、神经纤维瘤)和"
            "学习支持——环境监测和支持可显著改善生活质量和功能预后。"
            "Regular tumor surveillance and learning support are key environmental "
            "modulators in NF1."
        ),
        "uncertainty_note": "Clinical course is unpredictable. Surveillance schedules are risk-stratified.",
    },

    # ═══ Immunodeficiency genes ═══
    "IL2RG": {
        "nutrition_type": 0.08,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.12,
        "parameter_type": "model_parameter",
        "description": (
            "SCID-X1是最具决定性的G×E交互案例：TREC新生儿筛查+早期HSCT/基因治疗"
            "可挽救生命并重建免疫功能。感染防护在移植前至关重要。"
            "Early HSCT/gene therapy is the most decisive G×E interaction — "
            "treating before infections occur is lifesaving."
        ),
        "uncertainty_note": "Survival >95% with HSCT before 3.5 months. Delayed diagnosis worsens outcomes.",
    },
    "BTK": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.10,
        "parameter_type": "model_parameter",
        "description": (
            "XLA的G×E交互：定期免疫球蛋白替代治疗可维持正常生长发育和预防感染。"
            "Regular immunoglobulin replacement is the definitive environmental "
            "modulator in XLA."
        ),
        "uncertainty_note": "Diagnosis is often delayed. Early treatment enables normal development.",
    },
    "RAG1": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.12,
        "parameter_type": "model_parameter",
        "description": (
            "RAG1-SCID的G×E交互与IL2RG类似：新生儿筛查+早期HSCT是决定性的环境干预。"
            "Early HSCT is the decisive environmental intervention in RAG1-SCID."
        ),
        "uncertainty_note": "Omenn syndrome requires additional immunomodulation pre-transplant.",
    },

    # ═══ Sensory genes ═══
    "GJB2": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.05,
        "development_stimulation": 0.12,
        "medical_adherence": 0.10,
        "environmental_safety": 0.03,
        "parameter_type": "model_parameter",
        "description": (
            "GJB2先天性听力损失的G×E交互极为明确：新生儿听力筛查+早期助听器/"
            "人工耳蜗(<12月龄)+语言康复可使语言发育接近正常水平。"
            "Early amplification/cochlear implantation before 12 months is the key "
            "G×E interaction enabling normal language development."
        ),
        "uncertainty_note": "Outcomes depend on intervention timing. Cochlear implant candidacy varies.",
    },
    "SLC26A4": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.05,
        "development_stimulation": 0.10,
        "medical_adherence": 0.10,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "SLC26A4相关听力损失的G×E交互：避免头部外伤(可加速听力下降)、"
            "早期听力干预和甲状腺功能监测是管理核心。"
            "Head trauma avoidance, early hearing intervention, and thyroid monitoring "
            "are key environmental modulators in Pendred syndrome/EVA."
        ),
        "uncertainty_note": "Hearing loss may be progressive and asymmetric. EVA management is supportive.",
    },
    "COL1A1": {
        "nutrition_type": 0.05,
        "sleep_quality": 0.05,
        "development_stimulation": 0.08,
        "medical_adherence": 0.12,
        "environmental_safety": 0.10,
        "parameter_type": "model_parameter",
        "description": (
            "成骨不全症(OI)的G×E交互：物理治疗增强肌力、支具辅助、环境安全改造"
            "(预防跌倒)和双膦酸盐治疗共同减少骨折率和改善功能。"
            "Physiotherapy, bracing, environmental safety modifications, and "
            "bisphosphonate therapy combine to reduce fracture rate in OI."
        ),
        "uncertainty_note": "Fracture rate varies by OI type and individual. Bisphosphonate response is variable.",
    },
    "USH2A": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.05,
        "development_stimulation": 0.10,
        "medical_adherence": 0.10,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "Usher综合征的G×E交互：早期听力干预(人工耳蜗)+定期眼科随访+"
            "低视力辅助和定向行走训练共同维持感官功能和生活质量。"
            "Dual sensory support — early cochlear implantation + regular eye care "
            "+ orientation and mobility training — preserves function in Usher syndrome."
        ),
        "uncertainty_note": "Rate of visual decline varies. Gene therapy trials ongoing for USH2A RP.",
    },
    "RB1": {
        "nutrition_type": 0.03,
        "sleep_quality": 0.03,
        "development_stimulation": 0.05,
        "medical_adherence": 0.15,
        "environmental_safety": 0.05,
        "parameter_type": "model_parameter",
        "description": (
            "视网膜母细胞瘤的G×E交互最为直接：从出生开始的定期眼底筛查+"
            "早期治疗可挽救视力并实现>95%的生存率。"
            "Regular fundoscopic screening from birth is the definitive G×E "
            "interaction — early detection saves vision and life."
        ),
        "uncertainty_note": "Hereditary RB requires lifelong surveillance. Second tumor risk is elevated.",
    },
}

# =============================================================================
# 6. Evidence Confidence — 证据可信度等级
# =============================================================================

EVIDENCE_CONFIDENCE: dict[str, dict[str, Union[str, Dict[str, str]]]] = {
    "PAH": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — dietary management is established treatment",
        },
        "note": "PKU is the archetypal treatable genetic disease. G×E interaction is definitively established.",
    },
    "G6PD": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — trigger avoidance is established management",
        },
        "note": "Over 200 variants characterized. Trigger-avoidance is the most direct G×E interaction in clinical genetics.",
    },
    "CYP21A2": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — medical adherence prevents crises",
        },
        "note": "CAH newborn screening reduces salt-wasting crisis mortality. Genotype-phenotype correlation is strong.",
    },
    "CFTR": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — multidisciplinary care and CFTR modulators improve outcomes",
        },
        "note": "CF care has transformed from fatal childhood disease to chronic manageable condition through environmental modulation.",
    },
    "DHCR7": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — cholesterol supplementation shows variable benefit",
        },
        "note": "Cholesterol synthesis defect. Treatment benefit varies by severity.",
    },
    "ACADM": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — feeding management prevents crises",
        },
        "note": "Newborn screening has dramatically reduced MCAD mortality. Simple feeding management is highly effective.",
    },
    "SLC2A1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — ketogenic diet is established treatment",
        },
        "note": "Ketogenic diet exemplifies metabolic bypass strategy. Response varies by age at initiation.",
    },
    "HBB": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — prophylactic care prevents complications",
        },
        "note": "Sickle cell outcomes dramatically improved by newborn screening and prophylactic care.",
    },
    "FBN1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — surveillance and prophylaxis prevent aortic events",
        },
        "note": "Prophylactic beta-blockade and elective aortic surgery have transformed Marfan life expectancy.",
    },
    "MYH7": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — activity modification and surveillance are standard",
        },
        "note": "HCM risk stratification guides management. ICD therapy prevents sudden death in high-risk patients.",
    },
    "CHD7": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — multidisciplinary care improves outcomes",
        },
        "note": "CHARGE syndrome requires complex, individualized multidisciplinary coordination.",
    },
    "SMN1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high — homozygous deletion is diagnostic",
            "gene_environment_interaction": "high — pre-symptomatic treatment transforms outcomes",
        },
        "note": "SMA treatment timing is the most critical G×E interaction in pediatric neurology.",
    },
    "SCN1A": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — fever and medication management reduce seizures",
        },
        "note": "Dravet syndrome management is a multi-factor G×E optimization problem.",
    },
    "MECP2": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early rehabilitation improves functional outcomes",
        },
        "note": "Rett syndrome intervention focuses on maximizing function and communication.",
    },
    "FMR1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early behavioral and educational intervention is well-supported",
        },
        "note": "Fragile X is the most common inherited intellectual disability. Early intervention consistently improves outcomes.",
    },
    "TSC1": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — mTOR inhibition is targeted therapy",
        },
        "note": "mTOR inhibitor therapy represents a targeted pharmacological G×E interaction.",
    },
    "NF1": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — surveillance and early intervention prevent complications",
        },
        "note": "NF1 management balances surveillance burden with complication prevention.",
    },
    "IL2RG": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early HSCT is lifesaving",
        },
        "note": "SCID-X1 exemplifies the most decisive G×E interaction: treatment before infection = survival.",
    },
    "BTK": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — immunoglobulin replacement is standard of care",
        },
        "note": "IVIG replacement enables normal life for XLA patients.",
    },
    "RAG1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early HSCT is standard of care",
        },
        "note": "RAG1-SCID outcomes depend on early diagnosis and transplant timing.",
    },
    "GJB2": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — early amplification enables normal language",
        },
        "note": "GJB2 hearing loss has excellent outcomes with early intervention.",
    },
    "SLC26A4": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early intervention and head trauma avoidance are beneficial",
        },
        "note": "EVA-associated hearing loss management includes precautions against progression.",
    },
    "COL1A1": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — multidisciplinary care reduces fracture and improves function",
        },
        "note": "OI management is increasingly proactive with bisphosphonate therapy.",
    },
    "USH2A": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "moderate — early sensory support preserves function",
        },
        "note": "Dual sensory loss requires coordinated audiology and ophthalmology care.",
    },
    "RB1": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
        "evidence_confidence": {
            "genetic_association": "high",
            "gene_environment_interaction": "high — screening is lifesaving and vision-sparing",
        },
        "note": "RB1 is the classic cancer predisposition gene where surveillance directly prevents mortality.",
    },
}

# =============================================================================
# 7. Health Dimension Configuration — 儿科健康维度
# =============================================================================

DIMENSION_CONFIG: dict[str, DimensionEntry] = {
    "metabolic": {
        "label": "代谢与内分泌",
        "icon": "⚡",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting inborn errors of metabolism and "
            "endocrine disorders risk awareness. Not a clinical measurement. "
            "反映先天性代谢缺陷和内分泌疾病风险意识的模拟指标。"
        ),
        "time_sensitivity": 1.2,
    },
    "cardiovascular": {
        "label": "心血管与血液",
        "icon": "❤️",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting congenital heart defects, "
            "cardiomyopathies, and hemoglobinopathies risk awareness. "
            "反映先天性心脏病、心肌病和血红蛋白病风险意识的模拟指标。"
        ),
        "time_sensitivity": 1.25,
    },
    "neurodevelopmental": {
        "label": "神经发育",
        "icon": "🧠",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting neurodevelopmental disorder risk "
            "awareness — intellectual disability, epilepsy, autism spectrum. "
            "反映神经发育障碍(智力障碍、癫痫、自闭症谱系)风险意识的模拟指标。"
        ),
        "time_sensitivity": 1.3,
    },
    "immunodeficiency": {
        "label": "免疫与感染",
        "icon": "🛡️",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting primary immunodeficiency risk awareness. "
            "Not a clinical immune function assessment. "
            "反映原发性免疫缺陷风险意识的模拟指标。不构成免疫功能评估。"
        ),
        "time_sensitivity": 1.2,
    },
    "sensory": {
        "label": "感官与结构",
        "icon": "👁️",
        "baseline": 50,
        "description": (
            "Simulated indicator reflecting congenital hearing loss, vision "
            "disorders, and skeletal dysplasia risk awareness. "
            "反映先天性听力损失、视力障碍和骨骼发育异常风险意识的模拟指标。"
        ),
        "time_sensitivity": 1.1,
    },
}

# =============================================================================
# 8. Simulation Parameters — 模拟运行参数
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
    "_parameter_notes": {
        "baseline_hti": (
            "Internally-defined educational index. NOT calibrated to any real "
            "population health distribution or clinical reference range."
        ),
        "gene_relative_weight_ceiling": (
            "Pedagogical design choice (40% gene, 60% environment) emphasizing "
            "that early intervention and care can modulate genetic predisposition."
        ),
        "environment_relative_weight_ceiling": (
            "Higher environment weight reflects the educational message that "
            "early growth factors are potent modulators of developmental trajectory."
        ),
        "interaction_contribution_range": (
            "Constrained to ±0.15 as published G×E effects are typically modest."
        ),
        "confidence_interval_range": "Model-internal uncertainty estimate.",
        "base_annual_decay": (
            "Model-internal trajectory parameter calibrated for educational "
            "demonstration over 5-20 year horizons."
        ),
    },
}

# =============================================================================
# 9. Trend Level Classification — 趋势等级映射
# =============================================================================

TREND_LEVEL_THRESHOLDS: dict[str, tuple[float, float]] = {
    "advantage": (0, 25),
    "favorable": (25, 40),
    "moderate": (40, 60),
    "attention": (60, 75),
    "significant": (75, 100),
}

# =============================================================================
# 10. Environment Factor Ranges — 婴儿成长环境标准化量表
# =============================================================================

ENVIRONMENT_RANGES: dict[str, EnvironmentRangeEntry] = {
    "nutrition_type": {
        "min": 0, "max": 10, "optimal": 8,
        "unit": "喂养方式评分（标准化模拟量表 0-10）",
        "label": "喂养方式",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Higher values: exclusive breastfeeding with appropriate frequency. "
            "Mid values: mixed feeding or formula with adequate schedule. "
            "Lower values: irregular feeding pattern. "
            "For certain metabolic conditions, specialized formula is medically indicated."
        ),
    },
    "sleep_quality": {
        "min": 0, "max": 10, "optimal": 9,
        "unit": "睡眠质量评分（标准化模拟量表 0-10）",
        "label": "睡眠质量",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Higher values: consistent sleep routine, adequate duration for age, "
            "safe sleep environment. Lower values: irregular schedule, insufficient sleep."
        ),
    },
    "development_stimulation": {
        "min": 0, "max": 10, "optimal": 8,
        "unit": "早期刺激评分（标准化模拟量表 0-10）",
        "label": "早期刺激",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Higher values: regular interactive play, language exposure, "
            "sensory stimulation appropriate for developmental stage. "
            "Lower values: limited interaction or stimulation opportunities."
        ),
    },
    "medical_adherence": {
        "min": 0, "max": 10, "optimal": 10,
        "unit": "医疗依从性评分（标准化模拟量表 0-10）",
        "label": "医疗依从性",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Higher values: full adherence to newborn screening follow-up, "
            "specialist appointments, medication schedules, and immunizations. "
            "Lower values: missed appointments, inconsistent medication."
        ),
    },
    "environmental_safety": {
        "min": 0, "max": 10, "optimal": 9,
        "unit": "环境安全评分（标准化模拟量表 0-10）",
        "label": "环境安全",
        "note": (
            "Model optimal point on a standardized input scale. "
            "Higher values: safe home environment, no toxin/lead exposure, "
            "allergen control, safe sleep practices, infection precautions. "
            "Lower values: known environmental hazards or exposure risks."
        ),
    },
}

# =============================================================================
# 11. Counterfactual Simulation — 反事实模拟参数
# =============================================================================

COUNTERFACTUAL_CONFIG: dict = {
    "changeable_factors": [
        "nutrition_type",
        "sleep_quality",
        "development_stimulation",
        "medical_adherence",
        "environmental_safety",
    ],
    "min_meaningful_change": 3,
    "significant_change_threshold": 10,
    "note": (
        "Counterfactual simulations illustrate potential trajectory "
        "differences under alternative early-growth scenarios for educational "
        "purposes. Results are model-generated scenarios, not predictions of "
        "individual intervention outcomes."
    ),
}

# =============================================================================
# 12. Model Limitations — 模型局限性声明
# =============================================================================
MODEL_LIMITATIONS = {
    "gene_disease_associations": (
        "Gene-disease relationships used in this model are based on ClinVar "
        "pathogenic assertions and published evidence. Not all variants in "
        "these genes are pathogenic. Variant interpretation requires expert review."
    ),
    "gxe_estimates": (
        "Published G×E interaction estimates are typically modest in magnitude "
        "and are predominantly from observational studies and clinical experience. "
        "The model's interaction coefficients are pedagogical parameters, not "
        "empirically validated effect sizes."
    ),
    "environmental_effects": (
        "Early-growth environmental factors (feeding, sleep, stimulation, medical "
        "adherence, safety) are measured on simplified standardized scales. "
        "Real environmental influences are multidimensional and difficult to quantify."
    ),
    "population_scope": (
        "Most genetic epidemiology data are from European-ancestry populations. "
        "Allele frequencies, effect sizes, and variant spectra differ across "
        "ancestry groups. This model uses simplified educational parameters only."
    ),
    "limited_snp_coverage": (
        "This model uses a curated panel of 25 pediatric genes for educational "
        "demonstration. It does NOT represent comprehensive genomic analysis. "
        "A clinical evaluation would consider many more genes and variants."
    ),
    "hti_validation": (
        "The Health Trajectory Index (HTI) has NOT been clinically validated. "
        "It does not correspond to any established pediatric health scoring system, "
        "diagnostic instrument, or risk assessment tool."
    ),
    "not_a_diagnostic": (
        "This system is NOT a medical device. It must NOT be used for "
        "clinical decision-making, disease diagnosis, treatment guidance, "
        "or individual risk assessment. It is an educational tool for "
        "genetic risk awareness only."
    ),
}

# =============================================================================
# 13. Model Assumptions — 模型假设
# =============================================================================
MODEL_ASSUMPTIONS = {
    "environment_modifiable": (
        "The model assumes that early-growth environmental factors (feeding, "
        "sleep, stimulation, medical adherence, safety) are modifiable inputs. "
        "In reality, healthcare access, socioeconomic factors, and parental "
        "resources constrain these choices."
    ),
    "genes_influence_not_determine": (
        "The model treats genetic variants as susceptibility modifiers, "
        "NOT deterministic causes. Even highly penetrant pathogenic variants "
        "have variable expressivity and may be modified by environment and "
        "other genetic factors."
    ),
    "interaction_educational": (
        "G×E interaction coefficients represent educational scenarios "
        "for demonstrating the CONCEPT of gene-environment interaction in "
        "infant development. They are not empirical estimates from specific studies."
    ),
    "linear_additivity": (
        "The model uses linear additive contributions for simplicity. "
        "Real biological relationships involve non-linear effects, threshold "
        "phenomena, feedback loops, and complex gene-gene and gene-environment "
        "interactions beyond the scope of this educational model."
    ),
    "early_intervention_benefit": (
        "The model assumes that early intervention (medical, developmental, "
        "environmental) is generally beneficial. While strongly supported by "
        "clinical evidence for many conditions, the magnitude of benefit varies "
        "individually."
    ),
    "standardized_input_scale": (
        "Environmental inputs use a 0-10 standardized scale for simplicity. "
        "This abstracts away from real clinical measurement instruments and "
        "should not be confused with validated pediatric assessment tools."
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
    "max_genes": 25,
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
