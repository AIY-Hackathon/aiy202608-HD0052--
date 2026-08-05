# Mini-PRS Implementation Documentation

> **Date**: 2026-08-05
> **Version**: 0.1.0
> **Step**: 2 — Integration of Evidence Layer
> **Module**: `engine/mini_prs.py`

---

## 1. Purpose

The Mini-PRS calculator converts raw genotype data (rsID + allele pairs) into an evidence-weighted genetic profile compatible with the existing G×E Health Simulation Engine. It serves as a **bridge** between real genetic data and the `genetic_profile` input that `simulate_health_trajectory()` expects.

The module does NOT modify:
- `engine/gxe_model.py` (HTI formula unchanged)
- `engine/config.py` (weights unchanged)
- `backend/api/*` (API endpoints unchanged)

---

## 2. Mathematical Formula

### 2.1 Core Calculation

For each gene $g$, the raw Mini-PRS score is:

$$\text{score}_g = \sum_{i \in \text{variants}(g)} \text{dosage}_i \times \beta_i$$

Where:
- $\text{dosage}_i \in \{0, 1, 2\}$ is the count of risk alleles for variant $i$ in the individual's genotype
- $\beta_i$ is the per-allele effect size from published GWAS (continuous trait change or log-odds)

### 2.2 Allele Dosage

Given a genotype string $G$ of length 2 (e.g., "AA", "AT", "CC") and a risk allele $R$:

$$\text{dosage}(G, R) = \text{count of } R \text{ in } \text{upper}(G)$$

| Genotype | Risk Allele | Dosage |
|----------|-------------|--------|
| AA | A | 2 |
| AT | A | 1 |
| TT | A | 0 |

### 2.3 Normalization to Sensitivity

The raw gene score is normalized to a 0–1 range for compatibility with `simulate_health_trajectory()`'s `genetic_profile` parameter:

$$\text{sensitivity}_g = \text{clamp}\left(\frac{\text{score}_g - \min_g}{\max_g - \min_g}, 0, 1\right)$$

Where $\min_g$ and $\max_g$ are the theoretical minimum and maximum scores for gene $g$ based on extreme genotypes at all included variants.

**Reference ranges:**

| Gene | $\min$ | $\max$ | Basis |
|------|--------|--------|-------|
| FTO | 0.00 | 0.56 | rs9939609: dosage 0→0.0, dosage 2→0.56 |
| APOE | −0.60 | 0.80 | ε2/ε2: 2×(−0.30)=−0.60, ε4/ε4: 2×0.40=0.80 |
| CLOCK | — | — | All betas TODO_VERIFY; normalization not possible |
| ACTN3 | — | — | Beta TODO_VERIFY; normalization not possible |

### 2.4 Worked Examples

**Example 1: FTO rs9939609 AA (homozygous risk)**
```
score_FTO = dosage(AA, A) × 0.28 = 2 × 0.28 = 0.56
sensitivity = clamp((0.56 − 0.00) / (0.56 − 0.00), 0, 1) = 1.00
```
→ Passes `{"FTO": 1.0}` to `simulate_health_trajectory()` — maximum genetic contribution.

**Example 2: FTO rs9939609 TT (homozygous reference)**
```
score_FTO = dosage(TT, A) × 0.28 = 0 × 0.28 = 0.00
sensitivity = clamp((0.00 − 0.00) / (0.56 − 0.00), 0, 1) = 0.00
```
→ Passes `{"FTO": 0.0}` — no elevated genetic contribution.

**Example 3: APOE ε3/ε4 (rs429358=CT, rs7412=CC)**
```
score_APOE = dosage(CT, C) × 0.40 + dosage(CC, T) × (−0.30)
           = 1 × 0.40 + 0 × (−0.30)
           = 0.40
sensitivity = clamp((0.40 − (−0.60)) / (0.80 − (−0.60)), 0, 1)
            = clamp(1.00 / 1.40, 0, 1)
            = 0.714
```
→ Passes `{"APOE": 0.714}` — elevated cognitive genetic risk.

**Example 4: APOE ε2/ε3 (rs429358=TT, rs7412=CT)**
```
score_APOE = dosage(TT, C) × 0.40 + dosage(CT, T) × (−0.30)
           = 0 × 0.40 + 1 × (−0.30)
           = −0.30
sensitivity = clamp((−0.30 − (−0.60)) / (0.80 − (−0.60)), 0, 1)
            = clamp(0.30 / 1.40, 0, 1)
            = 0.214
```
→ Passes `{"APOE": 0.214}` — protective effect reduces genetic sensitivity.

---

## 3. APOE Genotype Resolution

APOE genotype (ε2/ε3/ε4) is determined by the combination of two SNPs:

| rs429358 (defines ε4) | rs7412 (defines ε2) | APOE Allele |
|------------------------|---------------------|-------------|
| C (risk) | C (reference) | **ε4** |
| T (reference) | C (reference) | **ε3** |
| T (reference) | T (risk/protective) | **ε2** |

The allele at each position is counted independently:
- rs429358 dosage = number of C alleles = ε4 count
- rs7412 dosage = number of T alleles = ε2 count
- Remaining alleles (up to 2 total) = ε3 count

The CC/CT/TT notation at rs7412 follows the reference genome, where C is the reference allele. The protective ε2 allele is defined by the T (alternate) allele at rs7412.

---

## 4. TODO_VERIFY Handling

Variants whose `effect_size_beta` field contains `"TODO_VERIFY"` (or where the risk allele is unconfirmed) are **skipped** in score calculation. They are recorded in the output under `variants_skipped` with the reason and evidence level.

**Currently affected:**
- **CLOCK rs1801260**: Most-studied CLOCK variant, but NO GWAS-level significance for sleep/chronotype. C allele consistently associated with evening chronotype in candidate gene studies, but quantitative per-allele beta not available.
- **CLOCK rs6832769**: GWAS-confirmed chronotype locus (Jones et al. 2019, N=697,828), but exact beta/risk allele pending direct GWAS Catalog extraction.
- **ACTN3 rs1815739**: Well-characterized functional variant (R577X nonsense), but no GWAS-significant association with continuous muscle strength traits in general population. OR≈1.21 from case-control athlete meta-analyses, but continuous-trait beta not available.

When all variants for a gene are TODO_VERIFY, the gene's `status` is set to `"TODO_VERIFY"` and `score` is `null`.

---

## 5. Limitations

### 5.1 Not a Clinical PRS

This Mini-PRS uses **7 variants across 4 genes**. A real clinical PRS uses hundreds to millions of variants. Our score captures only a tiny fraction of genetic variance:

| Gene | Variance Captured | Missing |
|------|-------------------|---------|
| FTO | ~1% of BMI variance | Hundreds of other BMI-associated loci |
| APOE | ~25–30% of AD genetic risk | 70–75% of genetic risk from other loci + non-genetic factors |
| CLOCK | <0.01% of sleep/chronotype variance | Sleep is highly polygenic (hundreds of loci) |
| ACTN3 | ~0% of general-population muscle strength | Strength is highly polygenic |

### 5.2 Population Specificity

Effect sizes are from **European-ancestry GWAS**. Beta estimates may not transfer to other populations due to:
- Different linkage disequilibrium (LD) patterns
- Different allele frequencies
- Different environmental exposures
- Gene × environment interactions that differ across populations

### 5.3 Effect Size Is Not Individual Risk

The β coefficients represent **population-level average effects**. An individual with a high Mini-PRS score does not necessarily have the associated trait — just as someone with a low score is not protected from it. Genetic effects operate probabilistically, not deterministically.

### 5.4 Normalization Is Approximate

The 0–1 normalization uses theoretical min/max scores. Real biological distributions are continuous and overlapping. A sensitivity of 0.5 for FTO does not mean "50% risk" — it means the individual's genotype-based score falls at the midpoint of the theoretical range for the variants included.

### 5.5 Missing Gene × Environment Information

The Mini-PRS captures **marginal genetic effects** (averaged across all environments in the GWAS study population). True G×E interaction — how genetic effects differ by environment — is captured separately by the `gxe_model.py` interaction layer, not by this module.

### 5.6 Linkage Disequilibrium

Variants in high LD (e.g., FTO rs9939609 and rs1421085, r²≈1.0 in Europeans) tag the same genetic signal. Including both without LD pruning would **double-count** the effect. The current implementation includes both in the database (with rs1421085 marked as tagging the same haplotype as rs9939609) but does not automatically prune for LD — users should provide only one FTO variant for meaningful scores.

---

## 6. Why This Is Not Disease Prediction

The Mini-PRS is an **educational simulation tool**, not a clinical risk predictor. Here are the critical distinctions:

| Aspect | Clinical Disease Prediction | This Mini-PRS |
|--------|---------------------------|---------------|
| **Variant count** | 100s–1,000,000s of SNPs | 7 SNPs across 4 genes |
| **Calibration** | Calibrated against incidence data in target population | Not calibrated |
| **Absolute risk** | Estimates absolute disease probability | Estimates relative position in theoretical range |
| **Validation** | Validated in independent cohorts with AUC/reclassification metrics | Not validated |
| **Regulatory oversight** | Some PRS are FDA-recognized; laboratories require CLIA certification | Research/educational use only |
| **Clinical actionability** | May inform screening intervals or preventive interventions | No clinical actionability |
| **Time-to-event** | Some PRS incorporate age-specific risk | No time component; static score |
| **Environmental modifiers** | Sometimes included as covariates | Deliberately separated — G×E modeled downstream |

The core educational value of this module is demonstrating **how** genetic information can be quantified and combined with environmental data — not predicting **what** will happen to any specific individual. The HTI score that ultimately emerges from `simulate_health_trajectory()` is explicitly an educational simulation metric, not a health forecast.

---

## 7. Integration with G×E Engine

```
┌─────────────────────────────────────────────────────────────┐
│                    Current Flow (unchanged)                   │
│                                                              │
│  genetic_profile = {"FTO": 0.5, "APOE": 0.7, ...}           │
│                          │                                   │
│                          ▼                                   │
│  simulate_health_trajectory(genetic_profile, environment)    │
│                          │                                   │
│                          ▼                                   │
│  HTI = 72 + gene_effect + env_effect + G×E_interaction      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              New Flow (with Mini-PRS bridge)                 │
│                                                              │
│  genotype_data = {"rs9939609": "AT", "rs429358": "CT", ...} │
│                          │                                   │
│                          ▼                                   │
│  calculate_mini_prs(genotype_data)                           │
│                          │                                   │
│                          ▼                                   │
│  genetic_profile = {"FTO": 0.50, "APOE": 0.71, ...}         │
│                          │                                   │
│                          ▼                                   │
│  simulate_health_trajectory(genetic_profile, environment)    │
│  ↑                                                           │
│  └── HTI formula and all downstream modules UNCHANGED        │
└─────────────────────────────────────────────────────────────┘
```

The Mini-PRS module is a **pre-processor** — it transforms genotype data into the format the engine expects. The engine itself is never touched.

### Convenience Function

```python
from engine.mini_prs import genotype_to_genetic_profile
from engine.gxe_model import simulate_health_trajectory

# One-line bridge:
result = simulate_health_trajectory(
    genotype_to_genetic_profile({
        "rs9939609": "AT",
        "rs429358": "CT",
        "rs7412": "CC",
    }),
    environment={"exercise": 7, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}
)
```

---

## 8. Module API Reference

### `calculate_mini_prs(genotype_data, db_path=None) → dict`

Main entry point. Computes complete Mini-PRS from genotype data.

**Input:**
- `genotype_data: dict[str, str]` — rsID → genotype string (e.g., `{"rs9939609": "AT"}`)
- `db_path: str | Path | None` — optional custom database path

**Output structure:**
```python
{
    "genetic_profile": {
        "FTO": {
            "score": 0.28,                    # float | None
            "normalized_sensitivity": 0.50,   # float | None (0-1 range)
            "variants_used": [...],           # list of variant contributions
            "variants_skipped": [...],        # list of skipped TODO_VERIFY variants
        },
        "APOE": {
            "score": 0.40,
            "normalized_sensitivity": 0.714,
            "apoe_genotype": "ε3/ε4",        # APOE only
            "variants_used": [...],
            "variants_skipped": [...],
        },
    },
    "evidence_summary": [...],   # per-gene GWAS evidence summary
    "meta": {
        "db_version": "0.1.0",
        "variants_input": 3,
        "variants_found": 3,
        "variants_not_in_db": 0,
        "variants_skipped_total": 0,
        "disclaimer": "...",
    },
}
```

### `genotype_to_genetic_profile(genotype_data) → dict[str, float]`

Convenience wrapper. Returns a simple `{"GENE": sensitivity_float}` dict ready for `simulate_health_trajectory()`.

**Example:**
```python
>>> genotype_to_genetic_profile({"rs9939609": "AT", "rs429358": "CT", "rs7412": "CC"})
{"FTO": 0.50, "APOE": 0.714}
```

---

## 9. Test Coverage

32 tests in `engine/tests/test_mini_prs.py`:

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestCountRiskAlleles` | 11 | Allele counting: homo/het/ref, case insensitivity, error handling |
| `TestParseFloatBeta` | 7 | Beta parsing: positive, negative, TODO_VERIFY, invalid |
| `TestResolveApoeGenotype` | 7 | APOE genotype resolution: all 6 common genotypes + error case |
| `TestCalculateMiniPrs` | 18 | FTO AA/AT/TT, APOE ε4/ε4 through ε2/ε2, combined, TODO_VERIFY handling, error cases |
| `TestGenotypeToGeneticProfile` | 3 | Convenience wrapper, sensitivity bounds, TODO_VERIFY exclusion |

**Key scenarios tested:**
- FTO AA vs TT: risk homozygote score (0.56) >> reference homozygote (0.00)
- APOE ε4 carrier vs ε3/ε3: ε4 carrier normalized sensitivity (0.714) > reference (0.429)
- APOE ε2 carrier: protective genotype produces lowest normalized sensitivity (0.214)
- CLOCK/ACTN3 variants with TODO_VERIFY: correctly skipped, status reported
- Unknown rsIDs: gracefully skipped without crash
- Invalid genotypes: ValueError raised with informative message

---

## 10. Files Modified/Created

| File | Action | Lines |
|------|--------|-------|
| `engine/mini_prs.py` | **Created** | 330 |
| `engine/tests/test_mini_prs.py` | **Created** | 280 |
| `engine/knowledge/MINI_PRS_IMPLEMENTATION.md` | **Created** | this file |

| File | Status |
|------|--------|
| `engine/gxe_model.py` | **Unchanged** |
| `engine/config.py` | **Unchanged** |
| `engine/knowledge/mini_prs_database.json` | **Unchanged** (Step 1 artifact) |
| `engine/knowledge/MINI_PRS_DATA_DOCUMENTATION.md` | **Unchanged** (Step 1 artifact) |
| `backend/api/simulate.py` | **Unchanged** |
| `backend/api/recommendations.py` | **Unchanged** |
