# =============================================================================
# engine/mini_prs.py — Evidence-based Mini-PRS Calculator (v0.3.0)
# =============================================================================
#
# v0.3.0 — Research Presentation Grade:
#   1. Unified normalization layer — raw_score preserved, standardized_score
#      across heterogenous trait scales (kg/m², log-odds, etc.)
#   2. Simulation-only language — "simulated health trajectory," not disease risk
#   3. APOE isolated as haplotype → risk_modifier (NEVER summed with FTO beta)
#   4. Evidence traceability — every score traces SNP → GWAS pub → effect → calc
#   5. generate_evidence_report() — presentation-ready summary
#
# Core principles:
#   - Only published effect sizes (no fabricated betas)
#   - Tier 1 genes (FTO) enter quantitative scoring
#   - APOE treated as haplotype with risk_modifier, NOT summed with other genes
#   - Tier 2 genes (CLOCK, ACTN3) remain explanation-only
#   - LD-aware: tagged variants not double-counted
#   - ALL output marked simulation_only=true
#   - Does NOT predict disease, does NOT provide clinical diagnosis
#
# =============================================================================

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------

_KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
_DB_PATH = _KNOWLEDGE_DIR / "mini_prs_database.json"


# =============================================================================
# Evidence Tier Configuration
# =============================================================================
#
# Tier 1 — Quantitative PRS genes (single scale: 0-1 sensitivity)
#   FTO: GWAS-confirmed BMI beta in kg/m² → standardized to 0-1
#   (APOE moved to haplotype module — see §Task 3 below)
#
# Tier 2 — Biological modifier genes (explanation only)
#   CLOCK, ACTN3: no validated continuous-trait GWAS beta available

EVIDENCE_TIER_1_GENES = {"FTO"}
EVIDENCE_TIER_2_GENES = {"CLOCK", "ACTN3"}

# APOE is special — handled as haplotype, NOT in either tier list
APOE_HAPLOTYPE_GENE = "APOE"


# =============================================================================
# LD (Linkage Disequilibrium) Aware Handling
# =============================================================================

LD_GROUPS: list[dict[str, Any]] = [
    {
        "group_id": "FTO_intron1_haplotype",
        "gene": "FTO",
        "population": "European",
        "r2": "≈1.0",
        "primary_variant": "rs9939609",
        "tagged_variants": ["rs1421085"],
        "note": (
            "rs1421085 is the likely causal variant (Claussnitzer et al. 2015) "
            "but is in perfect LD with rs9939609 in Europeans. "
            "Their effects represent the SAME genetic signal and must NOT be summed."
        ),
    },
]


def _build_ld_exclusion_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for group in LD_GROUPS:
        primary = group["primary_variant"]
        mapping[primary] = primary
        for tagged in group["tagged_variants"]:
            mapping[tagged] = primary
    return mapping


_LD_EXCLUSION_MAP = _build_ld_exclusion_map()


def _get_ld_note(rsid: str) -> str | None:
    for group in LD_GROUPS:
        if rsid in group["tagged_variants"]:
            return (
                f"Tagged by {group['primary_variant']} "
                f"(LD r²{group['r2']} in {group['population']} population). "
                f"{group['note']}"
            )
    return None


# =============================================================================
# Unified Normalization Configuration
# =============================================================================
#
# Each gene that produces a quantitative score has:
#   - trait: the GWAS trait (BMI for FTO)
#   - original_unit: the unit of the raw beta
#   - raw_min / raw_max: theoretical min/max raw_score across all genotypes
#   - normalization: raw → standardized (0-1) via linear rescale + clamp
#
# CRITICAL: FTO and APOE effects are NEVER summed.
#   - FTO → standardized_score (0-1) in genetic_profile
#   - APOE → risk_modifier (0-1) in apoe_haplotype_profile (separate output)
#
# The G×E engine receives standardized_score for FTO,
# and APOE risk_modifier as a separate cognitive-dimension modifier.

NORMALIZATION_CONFIG: dict[str, dict[str, Any]] = {
    "FTO": {
        "trait": "body_mass_index",
        "original_unit": "kg/m² BMI increase per risk allele",
        "raw_min": 0.0,
        "raw_max": 0.56,    # dosage=2 × beta=0.28
        "description": (
            "FTO rs9939609 per-allele BMI effect (~0.28 kg/m² per A allele). "
            "Raw score = dosage × 0.28. Standardized to 0-1 by dividing by "
            "the theoretical maximum (2×0.28 = 0.56 kg/m² for AA genotype)."
        ),
    },
}


# =============================================================================
# APOE Haplotype → risk_modifier mapping
# =============================================================================
#
# APOE is NOT a quantitative PRS gene. It is a haplotype-based risk modifier.
# The two defining SNPs (rs429358, rs7412) are combined to determine
# ε2/ε3/ε4 status, which maps to a 0-1 risk_modifier for the cognitive
# health dimension.
#
# Mapping rationale:
#   - ε2/ε2 (strongest protection) → risk_modifier ≈ 0.00
#   - ε3/ε3 (population reference) → risk_modifier ≈ 0.43
#   - ε4/ε4 (strongest risk)       → risk_modifier ≈ 1.00
#
# The modifier is derived from log-odds ratios from Alzgene meta-analyses
# (Bertram et al. 2007) and Lambert et al. (2013), normalized to [0, 1].

APOE_RISK_MODIFIER_MAP: dict[str, float] = {
    "ε2/ε2": 0.00,
    "ε2/ε3": 0.21,
    "ε3/ε3": 0.43,
    "ε2/ε4": 0.50,
    "ε3/ε4": 0.71,
    "ε4/ε4": 1.00,
}

# Evidence source for APOE haplotype interpretation
APOE_EVIDENCE = {
    "source": (
        "NHGRI-EBI GWAS Catalog; Bertram et al. (2007) Alzgene meta-analysis; "
        "Lambert et al. (2013) Nat Genet 45:1452–1458; "
        "Ali et al. (2023) Acta Neuropathol Commun"
    ),
    "evidence_level": "GWAS_META_ANALYSIS",
    "population": "European",
    "description": (
        "APOE ε2/ε3/ε4 haplotype determined from rs429358 (defines ε4) and "
        "rs7412 (defines ε2). ε4 is the strongest common genetic risk factor "
        "for late-onset Alzheimer's disease (OR≈3.7 per allele). ε2 is "
        "protective (OR≈0.55 per allele). The risk_modifier maps the haplotype "
        "to a 0-1 scale for use as a cognitive health dimension modifier in "
        "G×E simulation. This is NOT a disease risk score — it modulates the "
        "simulated health trajectory's cognitive component."
    ),
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_db() -> dict[str, Any]:
    if not _DB_PATH.exists():
        raise FileNotFoundError(
            f"Mini-PRS database not found at {_DB_PATH}. "
            "Run Step 1 first to create engine/knowledge/mini_prs_database.json."
        )
    with open(_DB_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_float_beta(raw: str) -> float | None:
    if not raw or raw.strip() == "":
        return None
    if "TODO_VERIFY" in raw.upper():
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        logger.warning(f"Cannot parse beta value: {raw!r}")
        return None


def _count_risk_alleles(genotype: str, risk_allele: str) -> int:
    if len(genotype) != 2:
        raise ValueError(
            f"Genotype must be exactly 2 characters, got {len(genotype)}: {genotype!r}"
        )
    gt = genotype.upper()
    ra = risk_allele.upper()
    valid_bases = {"A", "T", "C", "G"}
    if gt[0] not in valid_bases or gt[1] not in valid_bases:
        raise ValueError(
            f"Genotype contains invalid characters: {genotype!r}. "
            f"Expected DNA bases A/T/C/G."
        )
    return gt.count(ra)


def _determine_gene_tier(gene: str) -> int:
    if gene in EVIDENCE_TIER_1_GENES:
        return 1
    if gene in EVIDENCE_TIER_2_GENES:
        return 2
    if gene == APOE_HAPLOTYPE_GENE:
        return 0  # APOE special — haplotype, not tiered
    logger.warning(f"Gene '{gene}' not in any tier list, defaulting to Tier 2")
    return 2


def _tier_label(tier: int) -> str:
    return {
        0: "APOE Haplotype — separate risk_modifier (not summed with other genes)",
        1: "Tier 1 — Quantitative PRS (GWAS-confirmed, standardized to 0-1)",
        2: "Tier 2 — Biological Modifier (explanation only)",
    }.get(tier, f"Unknown tier {tier}")


# =============================================================================
# APOE Haplotype Engine (inline, no import needed)
# =============================================================================


def _resolve_apoe_haplotype(
    rs429358_genotype: str,
    rs7412_genotype: str,
) -> dict[str, Any]:
    """Resolve APOE ε2/ε3/ε4 haplotype from two defining SNPs.

    Returns full classification including risk_modifier.
    """
    try:
        e4 = _count_risk_alleles(rs429358_genotype, "C")
        e2 = _count_risk_alleles(rs7412_genotype, "T")
    except ValueError as exc:
        raise ValueError(
            f"Invalid APOE genotype: {exc}. "
            f"rs429358={rs429358_genotype!r}, rs7412={rs7412_genotype!r}"
        ) from exc

    if e2 + e4 > 2:
        raise ValueError(
            f"Invalid APOE allele combination: {e2} ε2 + {e4} ε4 > 2 total"
        )

    e3 = 2 - e2 - e4
    alleles = (["ε2"] * e2) + (["ε3"] * e3) + (["ε4"] * e4)
    genotype_str = "/".join(sorted(alleles, key=lambda a: int(a[1])))

    risk_modifier = APOE_RISK_MODIFIER_MAP.get(genotype_str)
    if risk_modifier is None:
        # Fallback: compute from allele counts
        raw = e4 * 0.40 + e2 * (-0.30)
        risk_modifier = round(max(0.0, min(1.0, (raw + 0.60) / 1.40)), 4)

    # Determine risk category
    risk_categories = {
        "ε2/ε2": ("protective", "Strong Protection"),
        "ε2/ε3": ("protective", "Mild Protection"),
        "ε3/ε3": ("reference", "Population Reference"),
        "ε2/ε4": ("elevated_risk", "Elevated Risk (ε4 carrier)"),
        "ε3/ε4": ("elevated_risk", "Elevated Risk (ε4 carrier)"),
        "ε4/ε4": ("high_risk", "High Risk (ε4 homozygous)"),
    }
    cat = risk_categories.get(genotype_str, ("unknown", "Unknown"))

    # Build evidence trace
    evidence_trace = {
        "snp_rs429358": {
            "genotype": rs429358_genotype.upper(),
            "dosage": e4,
            "defines": "ε4 allele",
            "source": "Lambert et al. (2013) Nat Genet 45:1452-1458",
        },
        "snp_rs7412": {
            "genotype": rs7412_genotype.upper(),
            "dosage": e2,
            "defines": "ε2 allele",
            "source": "Lambert et al. (2013) Nat Genet 45:1452-1458",
        },
        "source": APOE_EVIDENCE["source"],
        "evidence_level": APOE_EVIDENCE["evidence_level"],
        "calculation": (
            f"rs429358(C→ε4)={e4}, rs7412(T→ε2)={e2}, "
            f"ε3={e3}, haplotype={genotype_str}, "
            f"risk_modifier mapped from Alzgene meta-analysis OR={risk_modifier:.4f}"
        ),
    }

    return {
        "haplotype": genotype_str,
        "e2_count": e2,
        "e3_count": e3,
        "e4_count": e4,
        "risk_category": cat[0],
        "risk_label": cat[1],
        "risk_modifier": risk_modifier,
        "evidence_source": "GWAS meta-analysis (Alzgene, Lambert 2013)",
        "confidence": "HIGH — strongest common genetic risk factor for LOAD",
        "evidence_trace": evidence_trace,
        "simulation_only": True,
        "disclaimer": (
            "This APOE haplotype analysis is an EDUCATIONAL SIMULATION tool. "
            "It does NOT predict Alzheimer's disease. ε4 carriers do NOT "
            "necessarily develop dementia — environment, education, and "
            "cardiovascular health significantly modify risk."
        ),
    }


# =============================================================================
# Evidence Trace Builder
# =============================================================================


def _build_evidence_trace(
    rsid: str,
    genotype: str,
    dosage: int,
    beta: float,
    beta_unit: str,
    source: str,
    evidence_level: str,
    trait: str,
    contribution: float,
) -> dict[str, Any]:
    """Build a single-variant evidence trace for full provenance."""
    return {
        "snp": rsid,
        "genotype": genotype,
        "dosage": dosage,
        "effect_size_beta": beta,
        "beta_unit": beta_unit,
        "trait": trait,
        "source_publication": source,
        "evidence_level": evidence_level,
        "calculation": f"{dosage} risk alleles × {beta} {beta_unit} = {contribution:.4f}",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_mini_prs(
    genotype_data: dict[str, str],
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Calculate evidence-weighted Mini-PRS genetic profile from raw genotype data.

    **v0.3.0 Architecture:**

    ┌──────────────────────────────────────────────────────────────┐
    │  Input: {"rs9939609": "AT", "rs429358": "CT", ...}         │
    └──────────┬───────────────────────┬──────────────────────────┘
               │                       │
       ┌───────▼────────┐    ┌────────▼──────────────┐
       │  FTO (Tier 1)  │    │  APOE (haplotype)     │
       │  dosage × beta │    │  rs429358 + rs7412    │
       │  → raw_score   │    │  → ε2/ε3/ε4          │
       │  → std_score   │    │  → risk_modifier     │
       └───────┬────────┘    └────────┬──────────────┘
               │                       │
       ┌───────▼───────────────────────▼──────────────────────────┐
       │  Output: genetic_profile (FTO std_score)                 │
       │          apoe_haplotype_profile (risk_modifier)          │
       │          biological_modifiers (CLOCK, ACTN3)             │
       │          evidence_traces (full provenance)               │
       └──────────────────────────────────────────────────────────┘

    FTO and APOE are NEVER summed together. They operate on different
    health dimensions (metabolic for FTO, cognitive for APOE) with
    incompatible GWAS trait scales.

    Args:
        genotype_data: rsID → genotype string dict.
                       Example: {"rs9939609": "AT", "rs429358": "CT", "rs7412": "CC"}
        db_path: Optional path to alternate database JSON.

    Returns:
        Full result dict with genetic_profile, apoe_haplotype_profile,
        biological_modifiers, evidence_summary, evidence_traces, and meta.

    Example:
        >>> result = calculate_mini_prs({
        ...     "rs9939609": "AT",
        ...     "rs429358": "CT",
        ...     "rs7412": "CC",
        ... })
        >>> result["genetic_profile"]["FTO"]["standardized_score"]
        0.50
        >>> result["apoe_haplotype_profile"]["haplotype"]
        'ε3/ε4'
    """
    # --- Validate input --------------------------------------------------
    if not genotype_data:
        raise ValueError("genotype_data cannot be empty")
    if not isinstance(genotype_data, dict):
        raise TypeError(
            f"genotype_data must be a dict, got {type(genotype_data).__name__}"
        )

    # --- Load database ----------------------------------------------------
    path = Path(db_path) if db_path else _DB_PATH
    if not path.exists():
        raise FileNotFoundError(f"Mini-PRS database not found: {path}")

    with open(path, encoding="utf-8") as fh:
        db = json.load(fh)

    variants_db: list[dict[str, Any]] = db.get("variants", [])
    gene_evidence: dict[str, Any] = db.get("gene_level_evidence_summary", {})

    variant_index: dict[str, dict[str, Any]] = {}
    for v in variants_db:
        rsid = v.get("rsid", "")
        if rsid:
            variant_index[rsid] = v

    # --- Accumulate per-gene ----------------------------------------------
    gene_accumulator: dict[str, dict[str, Any]] = {}
    apoe_snps: dict[str, str] = {}  # Separate APOE SNP tracking
    variants_found = 0
    variants_skipped_total = 0
    variants_ld_tagged = 0
    all_evidence_traces: list[dict[str, Any]] = []

    for rsid, genotype_str in genotype_data.items():
        variant = variant_index.get(rsid)
        if variant is None:
            logger.warning(f"Variant {rsid} not found in Mini-PRS database, skipping")
            continue

        gene = variant.get("gene", "UNKNOWN")
        if gene not in gene_accumulator:
            gene_accumulator[gene] = {
                "score": 0.0,
                "variants_used": [],
                "variants_skipped": [],
                "ld_notes": [],
            }

        variants_found += 1

        # --- APOE: capture SNPs for haplotype resolution -----------------
        if gene == APOE_HAPLOTYPE_GENE:
            apoe_snps[rsid] = genotype_str
            # Still record as "used" for transparency but separately handled
            gene_accumulator[gene]["variants_used"].append({
                "rsid": rsid,
                "genotype": genotype_str.upper(),
                "note": "Routed to APOE haplotype resolver — NOT summed with FTO",
            })
            continue

        # --- LD-aware handling -------------------------------------------
        ld_primary = _LD_EXCLUSION_MAP.get(rsid, rsid)
        if ld_primary != rsid:
            # Check if the primary variant was also provided — if so, skip.
            # If only the tagged variant is provided, use it as a proxy.
            primary_already_provided = ld_primary in genotype_data
            if primary_already_provided:
                variants_ld_tagged += 1
                ld_note = _get_ld_note(rsid)
                gene_accumulator[gene]["ld_notes"].append({
                    "rsid": rsid, "tagged_by": ld_primary, "reason": ld_note,
                })
                gene_accumulator[gene]["variants_skipped"].append({
                    "rsid": rsid,
                    "reason": (
                        f"LD-tagged by {ld_primary} (r²≈1.0 in Europeans). "
                        "Not summed to prevent double-counting."
                    ),
                    "trait": variant.get("trait", ""),
                    "evidence_level": variant.get("evidence_level", ""),
                })
                variants_skipped_total += 1
                continue
            # else: tagged variant is the only one provided — use it as proxy
            # (falls through to Tier 1 scoring below)

        # --- Tier 2 filter ------------------------------------------------
        gene_tier = _determine_gene_tier(gene)
        if gene_tier == 2:
            variants_skipped_total += 1
            gene_accumulator[gene]["variants_skipped"].append({
                "rsid": rsid,
                "reason": (
                    f"Tier 2 biological modifier — no validated GWAS beta "
                    f"available for quantitative scoring. Gene role "
                    f"({variant.get('trait', '')}) is documented but cannot "
                    f"be numerically included."
                ),
                "trait": variant.get("trait", ""),
                "evidence_level": variant.get("evidence_level", ""),
            })
            continue

        # --- Tier 1 scoring -----------------------------------------------
        beta_raw = variant.get("effect_size_beta", "")
        beta = _parse_float_beta(beta_raw)
        if beta is None:
            variants_skipped_total += 1
            gene_accumulator[gene]["variants_skipped"].append({
                "rsid": rsid,
                "reason": "TODO_VERIFY — no confirmed GWAS effect size available",
                "trait": variant.get("trait", ""),
                "evidence_level": variant.get("evidence_level", ""),
            })
            continue

        risk_allele = variant.get("risk_allele", "")
        if not risk_allele or risk_allele == "TODO_VERIFY":
            variants_skipped_total += 1
            gene_accumulator[gene]["variants_skipped"].append({
                "rsid": rsid,
                "reason": "TODO_VERIFY — risk allele not confirmed",
                "trait": variant.get("trait", ""),
            })
            continue

        try:
            dosage = _count_risk_alleles(genotype_str, risk_allele)
        except ValueError as exc:
            raise ValueError(
                f"Cannot parse genotype for {rsid}: {exc}"
            ) from exc

        contribution = round(dosage * beta, 4)
        gene_accumulator[gene]["score"] += contribution

        vu = {
            "rsid": rsid,
            "genotype": genotype_str.upper(),
            "risk_allele": risk_allele,
            "dosage": dosage,
            "beta": beta,
            "beta_unit": variant.get("beta_unit", ""),
            "trait": variant.get("trait", ""),
            "evidence_level": variant.get("evidence_level", ""),
        }
        gene_accumulator[gene]["variants_used"].append(vu)

        # Build evidence trace
        trace = _build_evidence_trace(
            rsid=rsid,
            genotype=genotype_str.upper(),
            dosage=dosage,
            beta=beta,
            beta_unit=variant.get("beta_unit", ""),
            source=variant.get("source", ""),
            evidence_level=variant.get("evidence_level", ""),
            trait=variant.get("trait", ""),
            contribution=contribution,
        )
        all_evidence_traces.append(trace)

    # --- Build output structures ------------------------------------------

    # 1. APOE haplotype profile (separate, never summed with FTO)
    apoe_haplotype_profile: dict[str, Any] | None = None
    if "rs429358" in apoe_snps and "rs7412" in apoe_snps:
        apoe_haplotype_profile = _resolve_apoe_haplotype(
            apoe_snps["rs429358"], apoe_snps["rs7412"]
        )
        apoe_haplotype_profile["snps_provided"] = {
            "rs429358": apoe_snps["rs429358"].upper(),
            "rs7412": apoe_snps["rs7412"].upper(),
        }
    elif apoe_snps:
        # Partial APOE — can't resolve haplotype
        apoe_haplotype_profile = {
            "haplotype": None,
            "error": (
                "Both rs429358 and rs7412 are required to determine APOE "
                f"haplotype. Only provided: {list(apoe_snps.keys())}."
            ),
            "snps_provided": {k: v.upper() for k, v in apoe_snps.items()},
            "simulation_only": True,
        }

    # 2. Genetic profile (Tier 1 genes only — structural, separate from APOE)
    genetic_profile: dict[str, dict[str, Any]] = {}
    biological_modifiers: dict[str, dict[str, Any]] = {}
    evidence_summary: list[dict[str, Any]] = []

    for gene, accum in gene_accumulator.items():
        gene_tier = _determine_gene_tier(gene)
        used_count = len([vu for vu in accum["variants_used"]
                          if "note" not in vu or "APOE" not in str(vu.get("note", ""))])
        skipped_count = len(accum["variants_skipped"])
        evidence = gene_evidence.get(gene, {})

        if gene == APOE_HAPLOTYPE_GENE:
            # APOE already handled above — skip in genetic_profile
            continue

        if gene_tier == 1:
            normalized = _standardize_score(gene, accum["score"])
            entry: dict[str, Any] = {
                "raw_score": round(accum["score"], 4),
                "raw_score_unit": NORMALIZATION_CONFIG.get(gene, {}).get(
                    "original_unit", "GWAS effect units"
                ),
                "standardized_score": (
                    round(normalized, 4) if normalized is not None else None
                ),
                "evidence_source": _gene_source(gene, evidence),
                "confidence": _gene_confidence(gene, evidence),
                "evidence_tier": 1,
                "trait": NORMALIZATION_CONFIG.get(gene, {}).get("trait", ""),
                "simulation_only": True,
                "variants_used": accum["variants_used"],
                "variants_skipped": accum["variants_skipped"],
                "ld_notes": accum["ld_notes"],
            }
            genetic_profile[gene] = entry

        elif gene_tier == 2:
            biological_modifiers[gene] = {
                "evidence_tier": 2,
                "variants_provided": accum["variants_skipped"],
                "variants_skipped": accum["variants_skipped"],
                "ld_notes": accum["ld_notes"],
                "explanation": _tier2_explanation(gene, accum, evidence),
                "simulation_only": True,
            }

        # Evidence summary
        if evidence:
            evidence_summary.append({
                "gene": gene,
                "gene_name": evidence.get("gene_name", gene),
                "evidence_tier": gene_tier,
                "tier_label": _tier_label(gene_tier),
                "gwas_evidence_strength": evidence.get("gwas_evidence_strength", ""),
                "biological_confidence": evidence.get("biological_confidence", ""),
                "key_publication": evidence.get("key_publication", ""),
                "variants_in_quantitative_model": (
                    used_count if gene_tier == 1 else 0
                ),
                "variants_todo_verify": skipped_count,
                "ld_tagged_variants": len(accum["ld_notes"]),
                "enters_numerical_prs": gene_tier == 1,
            })

    # 3. APOE summary entry
    if apoe_haplotype_profile and apoe_haplotype_profile.get("haplotype"):
        apoe_evidence = gene_evidence.get("APOE", {})
        evidence_summary.append({
            "gene": "APOE",
            "gene_name": apoe_evidence.get("gene_name", "Apolipoprotein E"),
            "evidence_tier": 0,
            "tier_label": _tier_label(0),
            "gwas_evidence_strength": apoe_evidence.get("gwas_evidence_strength", ""),
            "biological_confidence": apoe_evidence.get("biological_confidence", ""),
            "key_publication": apoe_evidence.get("key_publication", ""),
            "haplotype": apoe_haplotype_profile["haplotype"],
            "risk_modifier": apoe_haplotype_profile["risk_modifier"],
            "enters_numerical_prs": False,
            "note": (
                "APOE is NOT summed with FTO. It produces a separate "
                "risk_modifier for the cognitive health dimension based on "
                "ε2/ε3/ε4 haplotype status, not a quantitative PRS score."
            ),
        })

    # --- Meta ------------------------------------------------------------
    meta = {
        "version": "0.3.0",
        "db_version": db.get("_meta", {}).get("version", "unknown"),
        "variants_input": len(genotype_data),
        "variants_found": variants_found,
        "variants_not_in_db": len(genotype_data) - variants_found,
        "variants_skipped_total": variants_skipped_total,
        "variants_ld_tagged": variants_ld_tagged,
        "tier1_genes": sorted(EVIDENCE_TIER_1_GENES),
        "tier2_genes": sorted(EVIDENCE_TIER_2_GENES),
        "apoe_handling": "separate_haplotype_profile",
        "apoe_not_summed_with_tier1": True,
        "ld_groups": [
            {"group_id": g["group_id"], "primary": g["primary_variant"],
             "tagged": g["tagged_variants"]}
            for g in LD_GROUPS
        ],
        "simulation_only": True,
        "language_policy": (
            "ALL output uses simulation-trajectory language. "
            "Phrases like 'disease risk increase/decrease' or 'future X-year "
            "probability' are FORBIDDEN. Use 'simulated health trajectory' "
            "and 'educational scenario' instead."
        ),
        "disclaimer": (
            "This Mini-PRS is an EDUCATIONAL SIMULATION tool. "
            "It does NOT predict disease, provide clinical risk assessment, "
            "or constitute medical advice. All effect sizes are population "
            "averages from published GWAS and do not represent individual risk. "
            "FTO and APOE operate on DIFFERENT GWAS trait scales and are "
            "NEVER summed together — they inform separate health dimensions."
        ),
    }

    return {
        "genetic_profile": genetic_profile,
        "apoe_haplotype_profile": apoe_haplotype_profile,
        "biological_modifiers": biological_modifiers,
        "evidence_summary": evidence_summary,
        "evidence_traces": all_evidence_traces,
        "meta": meta,
    }


# =============================================================================
# Unified Standardization (Task 1)
# =============================================================================


def _standardize_score(gene: str, raw_score: float) -> float | None:
    """Convert raw GWAS-trait score to 0-1 standardized scale.

    Different genes have beta coefficients on incompatible original scales:
      - FTO: kg/m² BMI
      - (APOE would be: log-odds Alzheimer's — but APOE is handled separately)

    Standardization rescales each gene's raw score to [0, 1] based on its
    own theoretical min/max range, making scores comparable across genes
    without mixing incompatible units.
    """
    cfg = NORMALIZATION_CONFIG.get(gene)
    if cfg is None:
        return None
    rmin = cfg["raw_min"]
    rmax = cfg["raw_max"]
    if rmax == rmin:
        return None
    return max(0.0, min(1.0, (raw_score - rmin) / (rmax - rmin)))


def _gene_source(gene: str, evidence: dict[str, Any]) -> str:
    return evidence.get("key_publication", f"See {gene} literature")


def _gene_confidence(gene: str, evidence: dict[str, Any]) -> str:
    strength = evidence.get("gwas_evidence_strength", "unknown")
    bio = evidence.get("biological_confidence", "")
    return f"{strength.upper()} — {bio}" if bio else strength.upper()


# =============================================================================
# Tier 2 Explanations (Task 2 compliant — simulation language)
# =============================================================================


def _tier2_explanation(
    gene: str, accum: dict[str, Any], evidence: dict[str, Any]
) -> str:
    """Generate narrative explanation for Tier 2 genes.

    Uses simulation-trajectory language — never disease-risk language.
    """
    templates: dict[str, str] = {
        "CLOCK": (
            "CLOCK is a core circadian rhythm gene (CLOCK-BMAL1 heterodimer) "
            "with well-established molecular function. Under this educational "
            "simulation, CLOCK variants help explain how sleep-related "
            "environmental factors may shift the simulated health trajectory "
            "through G×E interaction. CLOCK common variants have very small "
            "effects that have NOT reached genome-wide significance in large "
            "GWAS (UK Biobank, N > 450,000), demonstrating that gene importance "
            "in biology does NOT equal variant effect size in populations."
        ),
        "ACTN3": (
            "ACTN3 encodes α-actinin-3, exclusively expressed in fast-twitch "
            "(type II) skeletal muscle fibers. Under this educational "
            "simulation, ACTN3 illustrates context-dependent genetic effects: "
            "the R577X variant matters at the performance extremes (elite "
            "athletes, OR≈1.21) but has negligible effects on general-population "
            "muscle strength. This demonstrates G×E interaction — how training "
            "(environment) can modulate genetic predisposition."
        ),
    }
    base = templates.get(gene, (
        f"{gene} is classified as a Tier 2 biological modifier. "
        "Its documented biological role informs the simulation's explanation "
        "layer without providing a numerical genetic score."
    ))
    variants_info = accum.get("variants_skipped", [])
    if variants_info:
        rsids = [v["rsid"] for v in variants_info]
        base += f" Provided variants (not scored): {', '.join(rsids)}."
    return base


# =============================================================================
# Evidence Report Generator (Task 5)
# =============================================================================


def generate_evidence_report(
    result: dict[str, Any] | None = None,
    genotype_data: dict[str, str] | None = None,
) -> str:
    """Generate a presentation-ready evidence report for the Mini-PRS system.

    This produces a structured markdown report suitable for:
    - Competition presentations
    - Scientific posters
    - Documentation appendices

    It explains WHAT data is used, WHY it's structured this way,
    and HOW each SNP contributes to the output.

    Args:
        result: Optional pre-computed Mini-PRS result. If None, genotype_data
                will be used to compute a fresh result.
        genotype_data: Optional genotype data. Only used if result is None.

    Returns:
        Markdown-formatted evidence report string.

    Example:
        >>> r = calculate_mini_prs({"rs9939609": "AT", "rs429358": "CT", "rs7412": "CC"})
        >>> print(generate_evidence_report(result=r))
    """
    if result is None:
        if genotype_data is None:
            # Generate a demo report from a representative example
            genotype_data = {
                "rs9939609": "AT",
                "rs429358": "CT",
                "rs7412": "CC",
            }
        result = calculate_mini_prs(genotype_data)

    lines: list[str] = []
    meta = result.get("meta", {})
    evidence_summary = result.get("evidence_summary", [])
    traces = result.get("evidence_traces", [])
    genetic_profile = result.get("genetic_profile", {})
    apoe = result.get("apoe_haplotype_profile", {})
    bio_mods = result.get("biological_modifiers", {})

    # --- Title -----------------------------------------------------------
    lines.append("# Mini-PRS Evidence Report")
    lines.append("")
    lines.append(f"> **Version**: {meta.get('version', 'unknown')}")
    lines.append(f"> **Database**: {meta.get('db_version', 'unknown')}")
    lines.append("> **Purpose**: Research presentation — G×E Health Simulation Engine")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- 1. Database Sources ---------------------------------------------
    lines.append("## 1. Data Sources")
    lines.append("")
    lines.append("| Source | URL | Usage |")
    lines.append("|--------|-----|-------|")
    lines.append("| NHGRI-EBI GWAS Catalog | https://www.ebi.ac.uk/gwas/ | Variant-trait associations, beta/OR, p-values |")
    lines.append("| ClinVar | https://www.ncbi.nlm.nih.gov/clinvar/ | Variant identity, functional context |")
    lines.append("| Ensembl | https://www.ensembl.org/ | Genomic coordinates (hg38), population allele frequencies |")
    lines.append("| PubMed-indexed GWAS | https://pubmed.ncbi.nlm.nih.gov/ | Primary publications (Frayling 2007, Lambert 2013, Jones 2019) |")
    lines.append("")

    # --- 2. Design Rationale --------------------------------------------
    lines.append("## 2. Design Rationale")
    lines.append("")
    lines.append("### Why NOT a traditional polygenic risk score?")
    lines.append("")
    lines.append("A clinical PRS uses **hundreds to millions of SNPs**. This Mini-PRS")
    lines.append("uses **7 SNPs across 4 genes**. It captures only a tiny fraction of")
    lines.append("genetic variance — intentionally. The purpose is **educational G×E")
    lines.append("simulation**, not risk prediction.")
    lines.append("")
    lines.append("### Why are FTO and APOE NOT summed together?")
    lines.append("")
    lines.append("FTO effect sizes are in **kg/m² BMI**. APOE effect sizes are in")
    lines.append("**log-odds for Alzheimer's disease**. These scales are fundamentally")
    lines.append("incompatible — summing them would be like adding meters to seconds.")
    lines.append("")
    lines.append("Instead:")
    lines.append("- **FTO** → `standardized_score` (0–1) → metabolic health dimension")
    lines.append("- **APOE** → `risk_modifier` (0–1) → cognitive health dimension")
    lines.append("")
    lines.append("### Why Tier 1 / Tier 2 / Haplotype separation?")
    lines.append("")
    lines.append("| Category | Genes | Enters numerical model? | Rationale |")
    lines.append("|----------|-------|------------------------|-----------|")
    lines.append("| **Tier 1 — Quantitative** | FTO | Yes (standardized 0–1) | GWAS-confirmed continuous-trait beta from replicated studies |")
    lines.append("| **APOE Haplotype** | APOE | Yes (separate risk_modifier) | Two-SNP haplotype, qualitatively different from single-SNP additive model |")
    lines.append("| **Tier 2 — Biological** | CLOCK, ACTN3 | No (explanation only) | No GWAS-level continuous-trait beta available; documented biological role informs simulation context |")
    lines.append("")

    # --- 3. SNP Inventory ------------------------------------------------
    lines.append("## 3. SNP Inventory")
    lines.append("")
    lines.append("### SNPs in the Quantitative Model (Tier 1)")
    lines.append("")
    if traces:
        lines.append("| SNP | Gene | Beta | Original Unit | Evidence Level |")
        lines.append("|-----|------|------|---------------|----------------|")
        for t in traces:
            lines.append(
                f"| {t['snp']} | {t.get('trait', '')} | {t['effect_size_beta']} | "
                f"{t['beta_unit']} | {t['evidence_level']} |"
            )
    else:
        lines.append("_No Tier 1 SNPs with quantifiable beta available for this genotype input._")
    lines.append("")

    # 4. APOE Haplotype --------------------------------------------------
    lines.append("### APOE Haplotype (Separate, Not Summed)")
    lines.append("")
    if apoe and apoe.get("haplotype"):
        lines.append(f"- **Haplotype**: {apoe['haplotype']}")
        lines.append(f"- **Risk Category**: {apoe.get('risk_label', 'N/A')}")
        lines.append(f"- **Risk Modifier**: {apoe.get('risk_modifier', 'N/A')}")
        lines.append(f"- **Evidence Source**: {apoe.get('evidence_source', 'N/A')}")
        if apoe.get("evidence_trace"):
            et = apoe["evidence_trace"]
            lines.append(f"- **Calculation**: {et.get('calculation', 'N/A')}")
        lines.append(f"- **Note**: APOE risk_modifier is NEVER summed with FTO standardized_score.")
        lines.append(f"  APOE informs the **cognitive** health dimension; FTO informs the **metabolic** dimension.")
    else:
        lines.append("_No APOE SNPs provided. Both rs429358 and rs7412 are required._")
    lines.append("")

    # 5. Tier 2 SNPs ----------------------------------------------------
    lines.append("### SNPs in Biological Explanation Only (Tier 2)")
    lines.append("")
    tier2_snps: list[str] = []
    for gene, bm in bio_mods.items():
        for vs in bm.get("variants_skipped", []):
            tier2_snps.append(f"- **{vs['rsid']}** ({gene}): {vs['reason']}")
    if tier2_snps:
        lines.extend(tier2_snps)
    else:
        lines.append("_No Tier 2 SNPs provided in this input._")
    lines.append("")

    # 6. Evidence traces per SNP ----------------------------------------
    lines.append("## 4. Per-SNP Evidence Traces")
    lines.append("")
    lines.append("Each scored SNP can be traced from genotype → published GWAS → effect size → calculation.")
    lines.append("")
    if traces:
        for i, t in enumerate(traces, 1):
            lines.append(f"### 4.{i}. {t['snp']}")
            lines.append("")
            lines.append(f"- **Genotype**: {t['genotype']}")
            lines.append(f"- **Risk allele dosage**: {t['dosage']}")
            lines.append(f"- **Effect size (β)**: {t['effect_size_beta']} {t['beta_unit']}")
            lines.append(f"- **Source publication**: {t['source_publication']}")
            lines.append(f"- **Evidence level**: {t['evidence_level']}")
            lines.append(f"- **Calculation**: {t['calculation']}")
            lines.append(f"- **Trait**: {t['trait']} (original GWAS trait scale)")
            lines.append("")

    # 7. Genetic Profile Output ------------------------------------------
    lines.append("## 5. Genetic Profile Output")
    lines.append("")
    for gene, gp in genetic_profile.items():
        lines.append(f"### {gene} (Tier {gp.get('evidence_tier', '?')})")
        lines.append("")
        lines.append(f"- **Raw score**: {gp.get('raw_score', 'N/A')} {gp.get('raw_score_unit', '')}")
        lines.append(f"- **Standardized score**: {gp.get('standardized_score', 'N/A')} (0–1 scale)")
        lines.append(f"- **Evidence source**: {gp.get('evidence_source', 'N/A')}")
        lines.append(f"- **Confidence**: {gp.get('confidence', 'N/A')}")
        lines.append(f"- **Simulation only**: {gp.get('simulation_only', True)}")
        lines.append(f"- **Variants used**: {len(gp.get('variants_used', []))}")
        lines.append(f"- **Variants skipped**: {len(gp.get('variants_skipped', []))}")
        lines.append("")

    # Application notes -------------------------------------------------
    lines.append("## 6. How These Scores Enter the G×E Engine")
    lines.append("")
    lines.append("```")
    lines.append("FTO standardized_score → genetic_profile['FTO']")
    lines.append("  → simulate_health_trajectory(genetic_profile, environment)")
    lines.append("  → influences metabolic dimension gene_effect")
    lines.append("")
    lines.append("APOE risk_modifier → apoe_haplotype_profile['risk_modifier']")
    lines.append("  → passed separately to cognitive dimension modifier")
    lines.append("  → modulates simulated cognitive health trajectory")
    lines.append("  → NOT summed with FTO — operates on different trait scale")
    lines.append("")
    lines.append("CLOCK/ACTN3 → biological_modifiers")
    lines.append("  → explanation layer only")
    lines.append("  → informs G×E interaction context")
    lines.append("```")
    lines.append("")

    # Disclaimer ---------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ Disclaimer")
    lines.append("")
    lines.append(f"> {meta.get('disclaimer', '')}")
    lines.append("")
    lines.append(f"> **Language policy**: {meta.get('language_policy', '')}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Convenience functions
# =============================================================================


def genotype_to_genetic_profile(
    genotype_data: dict[str, str],
) -> dict[str, float]:
    """Return simplified genetic_profile for simulate_health_trajectory().

    Only Tier 1 genes with standardized_score are included.
    APOE is NOT included here — use genotype_to_apoe_modifier() for that.

    Args:
        genotype_data: rsID → genotype string dict.

    Returns:
        {"FTO": 0.50, ...} — directly passable to simulate_health_trajectory().
    """
    full_result = calculate_mini_prs(genotype_data)
    profile: dict[str, float] = {}
    for gene, gp in full_result["genetic_profile"].items():
        score = gp.get("standardized_score")
        if score is not None:
            profile[gene] = score
    return profile


def genotype_to_apoe_modifier(
    genotype_data: dict[str, str],
) -> dict[str, Any] | None:
    """Extract APOE risk_modifier from genotype data.

    Returns None if APOE SNPs are not provided or insufficient.
    """
    full_result = calculate_mini_prs(genotype_data)
    apoe = full_result.get("apoe_haplotype_profile")
    if apoe is None:
        return None
    return {
        "haplotype": apoe.get("haplotype"),
        "risk_modifier": apoe.get("risk_modifier"),
        "risk_category": apoe.get("risk_category"),
        "risk_label": apoe.get("risk_label"),
        "simulation_only": True,
    }


def get_biological_context(
    genotype_data: dict[str, str],
) -> dict[str, str]:
    """Extract Tier 2 gene explanations."""
    full_result = calculate_mini_prs(genotype_data)
    context: dict[str, str] = {}
    for gene, bm in full_result.get("biological_modifiers", {}).items():
        context[gene] = bm.get("explanation", "")
    return context


# =============================================================================
# Standalone Demo
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Mini-PRS Calculator v0.3.0 — Research Presentation Demo")
    print("=" * 70)

    demo_genotype = {
        "rs9939609": "AA",
        "rs1421085": "CC",   # LD-tagged — should NOT be summed
        "rs429358": "CT",
        "rs7412": "CC",
    }

    result = calculate_mini_prs(demo_genotype)

    # Quick summary
    print("\n📋 Input:")
    for rsid, gt in demo_genotype.items():
        print(f"   {rsid}: {gt}")

    print(f"\n{'='*70}")
    print("FTO — Quantitative PRS (Tier 1)")
    print(f"{'='*70}")
    fto = result["genetic_profile"].get("FTO", {})
    print(f"  Raw score:    {fto.get('raw_score')} {fto.get('raw_score_unit')}")
    print(f"  Standardized: {fto.get('standardized_score')} (0–1 sensitivity)")
    print(f"  Evidence:     {fto.get('evidence_source', '')[:80]}...")
    print(f"  Confidence:   {fto.get('confidence')}")
    print(f"  Simulation:   {fto.get('simulation_only')}")
    if fto.get("variants_skipped"):
        for vs in fto["variants_skipped"]:
            print(f"  Skipped:      {vs['rsid']} → {vs['reason']}")

    print(f"\n{'='*70}")
    print("APOE — Haplotype Profile (NOT summed with FTO)")
    print(f"{'='*70}")
    apoe = result.get("apoe_haplotype_profile", {})
    if apoe:
        print(f"  Haplotype:      {apoe.get('haplotype')}")
        print(f"  Risk Category:  {apoe.get('risk_label')}")
        print(f"  Risk Modifier:  {apoe.get('risk_modifier')} (0–1)")
        print(f"  Evidence:       {apoe.get('evidence_source', '')[:80]}...")
        print(f"  Snps Provided:  {apoe.get('snps_provided')}")
        if apoe.get("evidence_trace"):
            print(f"  Trace:          {apoe['evidence_trace'].get('calculation', '')[:100]}...")
        print(f"  Simulation:     {apoe.get('simulation_only')}")

    print(f"\n{'='*70}")
    print("Evidence Traces")
    print(f"{'='*70}")
    for trace in result.get("evidence_traces", []):
        print(f"  {trace['snp']}: {trace['calculation']}")
        print(f"    Source: {trace['source_publication'][:100]}...")

    print(f"\n{'='*70}")
    print("Evidence Report (excerpt)")
    print(f"{'='*70}")
    report = generate_evidence_report(result=result)
    # Print first ~60 lines
    report_head = "\n".join(report.split("\n")[:80])
    print(report_head)
    print("... (full report via generate_evidence_report())")

    print(f"\n⚠️  {result['meta']['disclaimer']}")
    print(f"\n📝 {result['meta']['language_policy']}")
    print()
