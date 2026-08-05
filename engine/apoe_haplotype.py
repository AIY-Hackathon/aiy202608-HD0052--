# =============================================================================
# engine/apoe_haplotype.py — APOE ε2/ε3/ε4 Haplotype Interpretation Module
# =============================================================================
#
# 将 rs429358 和 rs7412 两个定义性 SNP 的基因型组合为 APOE 单倍型
#（ε2/ε3/ε4），并输出分类结果、风险分层和科学解释。
#
# 两个 SNP 共同定义三个常见的 APOE 等位基因：
#
#   rs429358 (C = ε4 风险)    rs7412 (T = ε2 保护性)    等位基因
#   ─────────────────────    ──────────────────────    ──────
#   C (ε4 定义性)             C (参考)                  ε4 — 风险
#   T (参考)                  C (参考)                  ε3 — 中性参考
#   T (参考)                  T (ε2 定义性)             ε2 — 保护性
#
#   注意：rs429358-C + rs7412-T 组合未在人群中观察到（ε4/ε2 顺式），
#   因为 ε4 和 ε2 是互斥的单倍型。杂合子个体可以同时携带 ε2 和 ε4
#   （反式 — 一条染色体上一个），这种情况下的基因型为 ε2/ε4。
#
# 参考文献：
#   Lambert et al. (2013) Nat Genet 45:1452-1458
#   Bertram et al. (2007) Alzgene meta-analysis
#
# =============================================================================

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# APOE 风险分层配置
# ---------------------------------------------------------------------------

# 每种 APOE 二倍体基因型的风险类别和效果大小。
# ε2/ε2 参考：对阿尔茨海默病具有最强的保护作用。
# ε3/ε3 参考：人群中常见的中性参考（~60% 的欧洲人群）。
# ε3/ε4 和 ε2/ε4：每个 ε4 拷贝的比值比约为 3-4。
# ε4/ε4：比值比约为 12-15。

APOE_GENOTYPE_INTERPRETATIONS: dict[str, dict[str, Any]] = {
    "ε2/ε2": {
        "risk_category": "protective",
        "risk_label": "Strong Protection",
        "estimated_or_vs_e3e3": 0.40,
        "description": (
            "两个拷贝的 ε2 保护性等位基因。与 ε3/ε3 相比，"
            "晚发性阿尔茨海默病风险降低约 60%。这是最强健的保护性常见基因型，"
            "在 ~0.5-1% 的欧洲血统人群中发现。注意：ε2/ε2 基因型与"
            "III 型高脂蛋白血症（一种独立的罕见脂质疾病）风险增加相关，"
            "但与本模拟无关。"
        ),
    },
    "ε2/ε3": {
        "risk_category": "protective",
        "risk_label": "Mild Protection",
        "estimated_or_vs_e3e3": 0.55,
        "description": (
            "一个拷贝的 ε2 保护性等位基因和一个 ε3 参考等位基因。"
            "AD 风险比 ε3/ε3 参考降低约 45%。"
            "在 ~12-15% 的欧洲血统人群中发现。"
        ),
    },
    "ε3/ε3": {
        "risk_category": "reference",
        "risk_label": "Reference (Neutral)",
        "estimated_or_vs_e3e3": 1.0,
        "description": (
            "两个拷贝的 ε3 参考等位基因。这是最常见的 APOE 基因型，"
            "在 ~60% 的欧洲血统人群中发现。既不增加也不减少 AD 风险 —— "
            "人群基线。"
        ),
    },
    "ε2/ε4": {
        "risk_category": "elevated_risk",
        "risk_label": "Elevated Risk (ε4 carrier)",
        "estimated_or_vs_e3e3": 3.2,
        "description": (
            "一个 ε2 保护性等位基因和一个 ε4 风险等位基因（反式杂合）。"
            "ε2 和 ε4 的影响部分抵消，产生的净风险介于 ε3/ε3 和 ε3/ε4 之间。"
            "每个 ε4 拷贝使 AD 风险增加约 3-4 倍；ε2 提供了适度的补偿。"
            "在 ~2-3% 的欧洲血统人群中发现。"
        ),
    },
    "ε3/ε4": {
        "risk_category": "elevated_risk",
        "risk_label": "Elevated Risk (ε4 carrier)",
        "estimated_or_vs_e3e3": 3.7,
        "description": (
            "一个拷贝的 ε4 风险等位基因和一个 ε3 参考等位基因。"
            "每个 ε4 拷贝的晚发性 AD 比值比约为 3.7。"
            "这是最常见的风险相关 APOE 基因型，"
            "在 ~20-25% 的欧洲血统人群中发现。ε4 等位基因降低了 "
            "APOE 蛋白从大脑清除淀粉样蛋白 β 的效率。"
        ),
    },
    "ε4/ε4": {
        "risk_category": "high_risk",
        "risk_label": "High Risk (ε4 homozygous)",
        "estimated_or_vs_e3e3": 14.0,
        "description": (
            "两个拷贝的 ε4 风险等位基因。"
            "晚发性 AD 的比值比约为 12-15。"
            "这是与 AD 风险相关的最高影响常见基因型，"
            "在 ~2-3% 的欧洲血统人群中发现。ε4/ε4 携带者占所有"
            "晚发性 AD 病例的约 10-15%。即使有这种基因型，"
            "许多个体永远不会发展为痴呆 —— 环境因素（教育、"
            "心血管健康、饮食、认知储备）会显著改变风险。"
        ),
    },
}


# ---------------------------------------------------------------------------
# 内部帮助函数（本地副本以避免与 mini_prs.py 循环导入）
# ---------------------------------------------------------------------------


def _count_risk_alleles(genotype: str, risk_allele: str) -> int:
    """计算给定基因型字符串中风险等位基因的数量。"""
    if len(genotype) != 2:
        raise ValueError(f"Genotype must be exactly 2 characters, got {len(genotype)}: {genotype!r}")
    gt = genotype.upper()
    ra = risk_allele.upper()
    valid_bases = {"A", "T", "C", "G"}
    if gt[0] not in valid_bases or gt[1] not in valid_bases:
        raise ValueError(f"Genotype contains invalid characters: {genotype!r}. Expected DNA bases A/T/C/G.")
    return gt.count(ra)


# ---------------------------------------------------------------------------
# 公开 API
# ---------------------------------------------------------------------------


def classify_apoe(
    rs429358_genotype: str,
    rs7412_genotype: str,
) -> dict[str, Any]:
    """将 rs429358 + rs7412 基因型分类为 APOE ε2/ε3/ε4 单倍型。

    这是 APOE 单倍型解释模块的主要入口点。
    接收两个定义性 SNP 的原始基因型字符串，并返回
    包含单倍型分类、风险分层和科学解释的完整字典。

    Args:
        rs429358_genotype: rs429358 的基因型字符串（定义 ε4）。
                           例如 "CC"（ε4/ε4）、"CT"（ε3/ε4）、"TT"（非 ε4）。
        rs7412_genotype: rs7412 的基因型字符串（定义 ε2）。
                         例如 "TT"（ε2/ε2）、"CT"（ε2/ε3）、"CC"（非 ε2）。

    Returns:
        包含以下内容的字典：
        {
            "genotype": "ε3/ε4",          # 规范化的 ε 等位基因表示
            "e2_count": 0,                # ε2 等位基因数量
            "e3_count": 1,                # ε3 等位基因数量
            "e4_count": 1,                # ε4 等位基因数量
            "risk_category": "elevated_risk",
            "risk_label": "Elevated Risk (ε4 carrier)",
            "estimated_or_vs_e3e3": 3.7,
            "numeric_score": 0.40,        # 原始 PRS 分数（e4 × 0.40 + e2 × -0.30）
            "description": "...",         # 科学解释
            "snps_resolved": ["rs429358", "rs7412"],
            "snps_provided": {
                "rs429358": "CT",
                "rs7412": "CC",
            },
        }

    Raises:
        ValueError: 如果任一基因型格式无效。

    Example:
        >>> result = classify_apoe("CT", "CC")
        >>> result["genotype"]
        'ε3/ε4'
        >>> result["risk_category"]
        'elevated_risk'
    """
    # 计算等位基因剂量
    try:
        e4_count = _count_risk_alleles(rs429358_genotype, "C")
        e2_count = _count_risk_alleles(rs7412_genotype, "T")
    except ValueError as exc:
        raise ValueError(
            f"Invalid APOE genotype: {exc}. "
            f"rs429358={rs429358_genotype!r}, rs7412={rs7412_genotype!r}"
        ) from exc

    return _classify_from_dosage(
        e4_count=e4_count,
        e2_count=e2_count,
        rs429358_genotype=rs429358_genotype.upper(),
        rs7412_genotype=rs7412_genotype.upper(),
    )


def classify_from_dosage(
    e4_count: int,
    e2_count: int,
) -> dict[str, Any]:
    """直接从等位基因计数（无需原始基因型）分类 APOE 单倍型。

    当您已经拥有来自上游处理的 allele dosage 值时很有用
    （例如来自 calculate_mini_prs 或 VCF 解析器）。

    Args:
        e4_count: ε4 等位基因数量（0、1 或 2）。
        e2_count: ε2 等位基因数量（0、1 或 2）。

    Returns:
        与 classify_apoe() 相同的字典结构，但 snps_provided 字段为 None。

    Raises:
        ValueError: 如果 e2 + e4 超过 2（二倍体）。
    """
    return _classify_from_dosage(
        e4_count=e4_count,
        e2_count=e2_count,
        rs429358_genotype=None,
        rs7412_genotype=None,
    )


def get_apoe_interpretation(genotype: str) -> dict[str, Any]:
    """查找给定 ε 基因型字符串的科学解释。

    Args:
        genotype: APOE 基因型如 "ε3/ε4"、"ε2/ε3" 等。

    Returns:
        来自 APOE_GENOTYPE_INTERPRETATIONS 的解释字典，
        或未知基因型的后备说明。

    Example:
        >>> interp = get_apoe_interpretation("ε3/ε4")
        >>> interp["risk_category"]
        'elevated_risk'
    """
    interpretation = APOE_GENOTYPE_INTERPRETATIONS.get(genotype)
    if interpretation is not None:
        return dict(interpretation)

    return {
        "risk_category": "unknown",
        "risk_label": "Unknown APOE genotype",
        "estimated_or_vs_e3e3": None,
        "description": (
            f"The APOE genotype '{genotype}' was not recognized. "
            "Common genotypes are ε2/ε2, ε2/ε3, ε3/ε3, ε2/ε4, ε3/ε4, ε4/ε4."
        ),
    }


# ---------------------------------------------------------------------------
# 内部实现
# ---------------------------------------------------------------------------


def _classify_from_dosage(
    e4_count: int,
    e2_count: int,
    rs429358_genotype: str | None,
    rs7412_genotype: str | None,
) -> dict[str, Any]:
    """从 ε2 和 ε4 等位基因计数构建完整的分类字典。"""
    if e2_count + e4_count > 2:
        raise ValueError(
            f"Invalid APOE allele combination: {e2_count} ε2 + {e4_count} ε4 > 2 total. "
            f"A diploid individual can carry at most 2 alleles."
        )

    e3_count = 2 - e2_count - e4_count

    # 构建规范化的基因型字符串（排序：ε2 < ε3 < ε4）
    alleles = (["ε2"] * e2_count) + (["ε3"] * e3_count) + (["ε4"] * e4_count)
    genotype_str = "/".join(sorted(alleles, key=lambda a: int(a[1])))

    # 原始 PRS 分数：ε4 × 0.40 + ε2 × (−0.30)
    numeric_score = round(e4_count * 0.40 + e2_count * (-0.30), 4)

    # 归一化到 [0, 1]：min = ε2/ε2 = −0.60，max = ε4/ε4 = 0.80
    normalized = round((numeric_score - (-0.60)) / (0.80 - (-0.60)), 4)
    normalized = max(0.0, min(1.0, normalized))

    # 查找解释
    interpretation = get_apoe_interpretation(genotype_str)

    result: dict[str, Any] = {
        "genotype": genotype_str,
        "e2_count": e2_count,
        "e3_count": e3_count,
        "e4_count": e4_count,
        "risk_category": interpretation["risk_category"],
        "risk_label": interpretation["risk_label"],
        "estimated_or_vs_e3e3": interpretation["estimated_or_vs_e3e3"],
        "numeric_score": numeric_score,
        "normalized_sensitivity": normalized,
        "description": interpretation["description"],
        "snps_resolved": ["rs429358", "rs7412"],
    }

    # 仅当提供时包含原始基因型
    if rs429358_genotype is not None and rs7412_genotype is not None:
        result["snps_provided"] = {
            "rs429358": rs429358_genotype,
            "rs7412": rs7412_genotype,
        }

    return result


# =============================================================================
# 独立运行演示
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("APOE Haplotype Classification — Demonstration")
    print("=" * 70)

    test_cases = [
        ("CC", "CC"),   # ε4/ε4
        ("CT", "CC"),   # ε3/ε4
        ("TT", "CC"),   # ε3/ε3
        ("TT", "CT"),   # ε2/ε3
        ("TT", "TT"),   # ε2/ε2
        ("CT", "CT"),   # ε2/ε4 (compound)
    ]

    for rs42, rs74 in test_cases:
        result = classify_apoe(rs42, rs74)
        print(f"\n  rs429358={rs42}, rs7412={rs74}")
        print(f"    → {result['genotype']} ({result['risk_label']})")
        print(f"    OR vs ε3/ε3: {result['estimated_or_vs_e3e3']}")
        print(f"    Numeric score: {result['numeric_score']:.2f}")
        print(f"    Normalized sensitivity: {result['normalized_sensitivity']:.4f}")

    print()
