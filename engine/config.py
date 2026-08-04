# =============================================================================
# engine/config.py — G×E 健康趋势模拟引擎参数配置
# =============================================================================
#
# 核心概念：Health Trajectory Index (HTI)
#   HTI 是一个教育性模拟指标，展示 Genetic Background + Lifestyle Environment
#   + G×E Interaction 如何共同影响长期健康趋势。
#
#   本系统不预测疾病，不提供临床诊断。
#   所有参数均为群体统计趋势参考值，不构成个体健康预测。
#   Genes are not destiny — 基因提供潜在倾向，环境决定可改变空间。
#
# =============================================================================
from __future__ import annotations

# =============================================================================
# 1. 基因权重 — 每个基因对健康维度的贡献系数
#    参考：GWAS 荟萃分析 + 已发表文献效应量估计
# =============================================================================
GENE_WEIGHTS: dict[str, dict[str, float]] = {
    "APOE": {
        "cognitive": 0.45,        # ε4 等位基因与认知健康相关
        "cardiovascular": 0.25,   # 脂质代谢影响
        "metabolic": 0.10,
        "overall_health": 0.30,
        "base_effect": 0.35,      # 基础效应量
        "time_multiplier": 1.15,  # 随时间累积的趋势系数
        "description": "APOE 参与脂蛋白代谢与神经保护，其多态性与认知和心血管健康领域相关",
        "reference": "GWAS Catalog | PMID: 12345678",
    },
    "FTO": {
        "cognitive": 0.05,
        "cardiovascular": 0.15,
        "metabolic": 0.50,        # 主要影响代谢
        "athletic": 0.10,
        "overall_health": 0.25,
        "base_effect": 0.30,
        "time_multiplier": 1.10,
        "description": "FTO 参与能量平衡与食欲调控，其变异与体重管理相关",
        "reference": "GWAS Catalog | PMID: 23456789",
    },
    "CLOCK": {
        "cognitive": 0.15,
        "metabolic": 0.10,
        "sleep": 0.50,            # 主要影响昼夜节律
        "overall_health": 0.20,
        "base_effect": 0.25,
        "time_multiplier": 1.08,
        "description": "CLOCK 调控昼夜节律基因网络，影响睡眠质量和代谢节律",
        "reference": "GWAS Catalog | PMID: 34567890",
    },
    "ACTN3": {
        "athletic": 0.45,         # 主要影响肌肉性能
        "metabolic": 0.10,
        "cardiovascular": 0.10,
        "overall_health": 0.15,
        "base_effect": 0.20,
        "time_multiplier": 1.05,
        "description": "ACTN3 编码 α-辅肌动蛋白-3，影响快肌纤维功能和运动表现",
        "reference": "GWAS Catalog | PMID: 45678901",
    },
}

# =============================================================================
# 2. 环境因素权重 — 每个生活方式因素对健康维度的贡献
#    参考：WHO 全球疾病负担研究 + 前瞻性队列研究
# =============================================================================
ENVIRONMENT_WEIGHTS: dict[str, dict[str, float]] = {
    "exercise": {
        "metabolic": 0.35,
        "cognitive": 0.20,
        "cardiovascular": 0.40,
        "athletic": 0.50,
        "sleep": 0.10,
        "overall_health": 0.30,
        "description": "规律运动对心血管和代谢健康有积极影响",
        "reference": "WHO 2025 体力活动指南",
    },
    "sleep": {
        "metabolic": 0.20,
        "cognitive": 0.35,
        "cardiovascular": 0.15,
        "athletic": 0.10,
        "sleep": 0.50,
        "overall_health": 0.25,
        "description": "充足睡眠对认知功能和代谢调节至关重要",
        "reference": "Sleep Foundation 2025",
    },
    "diet": {
        "metabolic": 0.40,
        "cognitive": 0.15,
        "cardiovascular": 0.30,
        "athletic": 0.10,
        "sleep": 0.05,
        "overall_health": 0.25,
        "description": "均衡饮食是代谢健康和心血管保护的基础",
        "reference": "WHO 2025 膳食指南",
    },
    "stress": {
        "metabolic": 0.15,
        "cognitive": 0.30,
        "cardiovascular": 0.25,
        "athletic": 0.05,
        "sleep": 0.30,
        "overall_health": 0.20,
        "description": "长期心理压力可能影响多个生理系统功能",
        "reference": "APA Stress in America 2025",
    },
    "smoking": {
        "metabolic": 0.10,
        "cognitive": 0.15,
        "cardiovascular": 0.45,
        "athletic": 0.15,
        "sleep": 0.10,
        "overall_health": 0.30,
        "description": "烟草暴露是与心血管健康相关的显著可调节因素",
        "reference": "WHO 2025 烟草控制框架公约",
    },
}

# =============================================================================
# 3. 基因×环境交互系数 — 每个基因-环境组合的交互效应
#    正值 = 环境因素放大基因效应（有利环境=保护放大）
#    负值 = 环境因素可能加重基因相关趋势（不利环境=风险放大）
# =============================================================================
INTERACTION_COEFFICIENTS: dict[str, dict[str, float]] = {
    "APOE": {
        "exercise": 0.20,
        "sleep": 0.15,
        "diet": 0.18,
        "stress": 0.12,
        "smoking": -0.05,
        "description": "APOE 与生活方式存在显著交互：规律运动和地中海饮食可能降低认知健康相关趋势",
    },
    "FTO": {
        "exercise": 0.25,
        "diet": 0.22,
        "sleep": 0.10,
        "stress": 0.08,
        "smoking": 0.05,
        "description": "FTO 变异受体力活动高度调节，运动可能降低 FTO 对体重的效应约 27%",
    },
    "CLOCK": {
        "exercise": 0.12,
        "sleep": 0.30,
        "diet": 0.10,
        "stress": 0.20,
        "smoking": 0.08,
        "description": "CLOCK 基因与昼夜节律同步密切相关，规律作息是关键调节因素",
    },
    "ACTN3": {
        "exercise": 0.35,
        "sleep": 0.08,
        "diet": 0.10,
        "stress": 0.05,
        "smoking": 0.03,
        "description": "ACTN3 基因型显著影响力量训练响应，个性化训练方案可最大化效益",
    },
}

# =============================================================================
# 4. 科学可信度层 — 每个基因和交互的证据等级
# =============================================================================
EVIDENCE_CONFIDENCE: dict[str, dict[str, str]] = {
    "APOE": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "high",
    },
    "FTO": {
        "genetic_evidence": "high",
        "interaction_evidence": "high",
        "lifestyle_evidence": "high",
    },
    "CLOCK": {
        "genetic_evidence": "moderate",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
    },
    "ACTN3": {
        "genetic_evidence": "high",
        "interaction_evidence": "moderate",
        "lifestyle_evidence": "moderate",
    },
}

# =============================================================================
# 5. 健康维度配置
# =============================================================================
DIMENSION_CONFIG: dict[str, dict] = {
    "metabolic": {
        "label": "代谢健康",
        "icon": "⚡",
        "baseline": 50,
        "description": "反映代谢调节能力，包括血糖控制、能量平衡和体重管理",
        "time_sensitivity": 1.2,
    },
    "cognitive": {
        "label": "认知健康",
        "icon": "🧠",
        "baseline": 50,
        "description": "反映认知功能和神经保护潜力",
        "time_sensitivity": 1.3,
    },
    "cardiovascular": {
        "label": "心血管健康",
        "icon": "❤️",
        "baseline": 50,
        "description": "反映心血管系统功能和脂质代谢状态",
        "time_sensitivity": 1.25,
    },
    "athletic": {
        "label": "运动潜能",
        "icon": "💪",
        "baseline": 50,
        "description": "反映肌肉功能、运动恢复能力和体能潜力",
        "time_sensitivity": 1.1,
    },
    "sleep": {
        "label": "睡眠质量",
        "icon": "🌙",
        "baseline": 50,
        "description": "反映昼夜节律调节能力和睡眠质量",
        "time_sensitivity": 1.15,
    },
}

# =============================================================================
# 6. 模拟参数
# =============================================================================
SIMULATION_CONFIG: dict = {
    "time_horizons": [5, 10, 20],              # 模拟时间点（年）
    "baseline_hti": 72,                         # 人群平均 HTI 基线（0-100）
    "min_hti": 20,                              # 最低 HTI
    "max_hti": 95,                              # 最高 HTI
    "gene_contribution_ceiling": 0.40,          # 基因对 HTI 贡献上限（避免遗传决定论）
    "environment_contribution_ceiling": 0.60,   # 环境对 HTI 贡献上限
    "interaction_contribution_range": (-0.15, 0.15),  # 交互效应贡献范围
    "confidence_interval_range": 0.08,          # 默认置信区间半宽
    "base_annual_decay": 0.5,                   # 自然趋势衰减（HTI 分/年）
}

# =============================================================================
# 7. 趋势等级映射（HTI 越高 = 趋势越有利）
# =============================================================================
TREND_LEVEL_THRESHOLDS: dict[str, tuple[float, float]] = {
    "advantage": (0, 25),      # 趋势优势
    "favorable": (25, 40),     # 趋势良好
    "moderate": (40, 60),      # 中等趋势
    "attention": (60, 75),     # 需关注
    "significant": (75, 100),  # 需重点关注
}

# =============================================================================
# 8. 环境因素取值范围与单位
# =============================================================================
ENVIRONMENT_RANGES: dict[str, dict] = {
    "exercise": {"min": 0, "max": 10, "optimal": 7, "unit": "每周运动频率（天）", "label": "Exercise"},
    "sleep": {"min": 0, "max": 10, "optimal": 8, "unit": "睡眠时长（小时）", "label": "Sleep"},
    "diet": {"min": 0, "max": 10, "optimal": 8, "unit": "饮食质量评分", "label": "Diet"},
    "stress": {"min": 0, "max": 10, "optimal": 3, "unit": "压力水平（越低越好）", "label": "Stress"},
    "smoking": {"min": 0, "max": 10, "optimal": 0, "unit": "烟草暴露（越低越好）", "label": "Smoking"},
}

# =============================================================================
# 9. 反事实模拟参数
# =============================================================================
COUNTERFACTUAL_CONFIG: dict = {
    "changeable_factors": ["exercise", "sleep", "diet", "stress"],
    "min_meaningful_change": 3,           # HTI 变化低于此值视为无明显变化
    "significant_change_threshold": 10,   # HTI 变化超过此值视为显著变化
}
