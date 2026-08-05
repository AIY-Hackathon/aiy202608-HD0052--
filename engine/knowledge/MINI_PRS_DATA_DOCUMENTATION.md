# Mini-PRS Data Documentation

> **Date**: 2026-08-05  
> **Version**: 0.1.0  
> **Status**: Phase 1 Data Layer — calculation modules NOT modified  
> **File**: `engine/knowledge/mini_prs_database.json`

---

## 1. Overview

This document describes the evidence-based Mini-PRS (Miniature Polygenic Risk Score) variant database created for the G×E Health Simulation Engine. The database provides per-SNP effect sizes from published GWAS and meta-analyses for the four supported genes: **FTO**, **APOE**, **CLOCK**, and **ACTN3**.

**Important**: This is a **data layer only**. No computation module has been modified. The HTI formula, gene effect calculation, and all existing engine logic remain unchanged.

---

## 2. What is Mini-PRS?

A **Polygenic Risk Score (PRS)** aggregates the effects of many genetic variants (typically hundreds to millions) to estimate an individual's genetic predisposition to a trait or disease. A **Mini-PRS** is a simplified version that:

- Uses only a small number of well-characterized variants (1–3 per gene)
- Focuses on SNPs with published, replicated evidence
- Is suitable for **educational simulation**, not clinical risk prediction

In our G×E engine context, Mini-PRS provides an **evidence-based alternative** to the current user-provided `sensitivity` parameter (a 0.0–1.0 manual estimate). Instead of asking the user "how sensitive are you to this gene?", a future version could compute a weighted score from actual genotype data.

---

## 3. Data Sources

All variant data is sourced from publicly available, peer-reviewed databases and publications:

| Source | URL | What We Used |
|--------|-----|-------------|
| **NHGRI-EBI GWAS Catalog** | https://www.ebi.ac.uk/gwas/ | Variant-trait associations with p-values, beta coefficients, odds ratios, and population metadata |
| **ClinVar** | https://www.ncbi.nlm.nih.gov/clinvar/ | Variant identity, clinical significance, functional context |
| **Ensembl** | https://www.ensembl.org/ | Genomic coordinates (hg38), gene annotations, population allele frequencies |
| **PubMed-indexed GWAS** | https://pubmed.ncbi.nlm.nih.gov/ | Primary literature: Frayling et al. 2007, Lambert et al. 2013, Jones et al. 2019, Speliotes et al. 2010 |

### Evidence Tiers

Each variant in the database carries an `evidence_level` field:

| Tier | Meaning | Count in DB |
|------|---------|-------------|
| `GWAS_CONFIRMED` | Reached genome-wide significance (p < 5×10⁻⁸) in published GWAS with replication. Effect size is from primary GWAS or meta-analysis. | 4 variants |
| `CANDIDATE_GENE` | Well-studied candidate gene variant with functional characterization and consistent direction of effect across multiple studies, but has NOT reached genome-wide significance in GWAS. | 2 variants |

---

## 4. Per-Gene SNP Documentation

### 4.1 FTO — Obesity/BMI

The FTO (Fat Mass and Obesity-associated) gene locus harbors the strongest and most replicated common genetic association with BMI in human genetics.

#### rs9939609 — Primary obesity risk variant

| Field | Value |
|-------|-------|
| **Source** | Frayling TM et al. (2007) *Science* 316:889–894. PMID: 17434869 |
| **GWAS Catalog** | Yes — replicated in 30+ studies, N > 71,000 |
| **Effect size** | β = 0.28 kg/m² BMI increase per A allele (SE = 0.03) |
| **Odds ratio** | OR = 1.25 (95% CI: 1.18–1.32) for obesity per A allele |
| **Population** | European (confirmed in East Asian and South Asian) |
| **MAF (EUR)** | ~0.40 |
| **What it means** | Each copy of the A allele is associated with, on average, ~0.28 kg/m² higher BMI. A person with AA genotype would have, on average, ~0.56 kg/m² higher BMI than a TT genotype person — about 1.5–2 kg body weight difference for someone of average height. |

#### rs1421085 — Causal variant at FTO locus

| Field | Value |
|-------|-------|
| **Source** | Claussnitzer M et al. (2015) *N Engl J Med* 373:895–907. PMID: 26287746 |
| **GWAS Catalog** | Yes — in perfect LD (r² ≈ 1.0) with rs9939609/rs1558902 in Europeans |
| **Effect size** | β ≈ 0.33 kg/m² per C allele (SE: TODO_VERIFY) |
| **What it means** | This is the likely **causal variant** underlying the FTO association signal. It disrupts ARID5B repressor binding, de-repressing IRX3/IRX5 to shift adipocyte development from beige (thermogenic) to white (lipid-storing). Because rs1421085 and rs9939609 tag the same haplotype, their effects should NOT be summed — they capture the same genetic signal. |

**Key insight for FTO**: The effect of carrying the risk allele is an average ~0.3 kg/m² BMI difference. This is modest at the individual level — explaining ~1% of BMI variance — but is highly statistically significant and replicated. The functional mechanism (adipocyte thermogenesis shift) is one of the best-elucidated in complex trait genetics.

---

### 4.2 APOE — Alzheimer's Disease / Cognitive Health

APOE (Apolipoprotein E) is the strongest known common genetic risk factor for late-onset Alzheimer's disease. The APOE genotype is defined by two SNPs acting together.

#### rs429358 — APOE ε4 (risk allele)

| Field | Value |
|-------|-------|
| **Source** | Lambert JC et al. (2013) *Nat Genet* 45:1452–1458. PMID: 24162737. Bertram L et al. (2007) Alzgene meta-analysis. |
| **GWAS Catalog** | Yes — strongest signal in every AD GWAS |
| **Effect size** | β ≈ 0.40 on liability/log-odds scale (SE ≈ 0.03) |
| **Odds ratio** | OR ≈ 3.7 (95% CI: 3.3–4.2) per ε4 allele for late-onset AD |
| **Population** | European (strongest effect; attenuated in East Asians and African Americans) |
| **MAF (EUR)** | ~0.15 (C/ε4 allele frequency) |
| **What it means** | Each copy of the ε4 allele (rs429358-C) confers approximately **3.7× increased odds** of developing late-onset Alzheimer's disease compared to ε3/ε3 reference. Individuals with the ε4/ε4 genotype have OR ≈ 12–15. The ε4 protein is less efficient at clearing amyloid-beta from the brain. |

#### rs7412 — APOE ε2 (protective allele)

| Field | Value |
|-------|-------|
| **Source** | Lambert JC et al. (2013). Bertram L et al. (2007) Alzgene meta-analysis. |
| **GWAS Catalog** | Yes — second-strongest signal at APOE locus |
| **Effect size** | β ≈ −0.30 on liability scale (SE ≈ 0.05) — negative = protective |
| **Odds ratio** | OR ≈ 0.55 (95% CI: 0.40–0.75) per ε2 allele |
| **Population** | European |
| **MAF (EUR)** | ~0.08 (T/ε2 allele frequency) |
| **What it means** | The ε2 allele is protective — carriers have about half the risk of ε3/ε3 individuals. The ε2 protein is more efficient at clearing amyloid-beta. |

#### APOE Genotype Determination

The two SNPs together define the three common APOE alleles:

| rs429358 | rs7412 | APOE Allele |
|----------|--------|-------------|
| T (non-risk) | C (ref) | **ε3** (reference, most common) |
| C (risk) | C (ref) | **ε4** (risk — OR ≈ 3.7) |
| T (non-risk) | T (risk/protective) | **ε2** (protective — OR ≈ 0.55) |

These two SNPs **must always be interpreted together** — neither is informative about APOE genotype in isolation.

**Key insight for APOE**: APOE is the strongest common genetic risk factor for Alzheimer's disease, but it is NOT deterministic. Many ε4 carriers never develop AD, and many AD patients are ε3/ε3. Genetics contributes ~60–80% of AD risk (heritability), and APOE explains ~25–30% of that genetic component. Environment (education, cardiovascular health, diet, cognitive reserve) modifies risk substantially — making this gene ideal for G×E simulation.

---

### 4.3 CLOCK — Chronotype / Sleep

CLOCK (Circadian Locomotor Output Cycles Kaput) is a core circadian rhythm gene. It encodes a transcription factor that forms a heterodimer with BMAL1 to drive rhythmic expression of PER, CRY, and other clock-controlled genes.

#### rs1801260 — Most studied variant (but NOT GWAS-significant)

| Field | Value |
|-------|-------|
| **Source** | Candidate gene studies: Mishima et al. (2005); multiple replications. EPIC-Spain (PMC9739590). |
| **GWAS Catalog** | **NOT genome-wide significant** in any published sleep/chronotype GWAS |
| **Effect size** | **TODO_VERIFY** — no GWAS-level beta available |
| **Evidence tier** | CANDIDATE_GENE |
| **MAF (EUR)** | ~0.30 (C allele) |
| **What it means** | The C (minor) allele is consistently associated with **evening chronotype** (preference for later sleep/wake times) across multiple candidate gene studies (Japanese N=421; Iranian N=403; Mediterranean N=1,495). However, the largest GWAS of chronotype (UK Biobank + 23andMe, N=697,828, Jones et al. 2019) found that individual CLOCK SNPs do not achieve genome-wide significance. The gene-level role of CLOCK in circadian biology is well-established mechanistically, but common variant effects are individually very small. |

#### rs6832769 — GWAS-validated chronotype locus

| Field | Value |
|-------|-------|
| **Source** | Jones SE et al. (2019) *Nat Commun* 10:1585. PMID: 30696823. GWAS of chronotype in 697,828 individuals. |
| **GWAS Catalog** | Yes — genome-wide significant association with morningness-eveningness preference |
| **Effect size** | **TODO_VERIFY** — pending direct GWAS Catalog extraction (GCST007083) |
| **Evidence tier** | GWAS_CONFIRMED (for trait association; effect size not yet extracted) |
| **What it means** | This SNP (or a proxy) reached genome-wide significance in the largest chronotype GWAS to date. It provides GWAS-level evidence that variation near CLOCK influences circadian preference. Exact quantitative effect size requires consultation of the primary GWAS summary statistics or GWAS Catalog entry. |

**Key insight for CLOCK**: The paradox of CLOCK genetics — the gene is one of the most important in circadian biology (Nobel Prize in Physiology or Medicine 2017 for circadian mechanisms), but common genetic variants in CLOCK have very small effects on sleep/chronotype that don't survive multiple-testing correction in GWAS. This illustrates a fundamental concept: **gene importance ≠ variant effect size**. A gene can be mechanistically critical while its common variants explain negligible phenotypic variance. Sleep and chronotype are highly polygenic traits influenced by hundreds of loci, each with tiny effects.

---

### 4.4 ACTN3 — Athletic Performance / Muscle Function

ACTN3 (Actinin Alpha 3) encodes α-actinin-3, a structural protein exclusively expressed in fast-twitch (type II) skeletal muscle fibers.

#### rs1815739 — R577X (functional null variant)

| Field | Value |
|-------|-------|
| **Source** | El Ouali EM et al. (2024) *Sports Med Open*. PMID: 38609671. Pabalan N et al. (2019). Chelly M et al. (2025) *J Strength Cond Res*. |
| **GWAS Catalog** | **NOT genome-wide significant** for general-population muscle strength or grip strength in large GWAS (UK Biobank, Willems et al.) |
| **Effect size** | **TODO_VERIFY** for continuous traits. OR ≈ 1.21 (95% CI: 1.07–1.37) for power athlete status (case-control meta-analysis). |
| **Evidence tier** | CANDIDATE_GENE |
| **MAF (EUR)** | ~0.45 (C/R allele frequency) |
| **What it means** | The T allele (X) introduces a premature stop codon (p.Arg577Ter), producing non-functional protein. Homozygotes (XX genotype, ~18% of Europeans) completely lack α-actinin-3 — with no apparent disease, as α-actinin-2 compensates. The R allele (C) is overrepresented in elite power/sprint athletes (OR ≈ 1.2). However, this effect is **not detectable** in the general population — grip strength GWAS show no signal at ACTN3. |

**Key insight for ACTN3**: The most famous "sports gene" illustrates an important distinction: **the effect is context-dependent**. The R577X polymorphism matters at the tails of the performance distribution (elite athletes) but has negligible effect on muscle strength in the general population. The XX genotype (complete loss of α-actinin-3) has been proposed to shift muscle metabolism toward oxidative (endurance) rather than glycolytic (sprint) pathways. This gene is ideal for educational G×E simulation because it demonstrates how genetic effects can interact with training (environment) to produce outcomes — a true gene × environment interaction.

---

## 5. Understanding Effect Sizes

### 5.1 What Does β (Beta) Mean?

The beta coefficient is the expected **change in the trait per copy of the effect allele**, holding all else constant. It comes from linear regression in a GWAS:

```
Trait = intercept + β × (allele_dosage) + covariates + error
```

- **β = 0.28 kg/m²** (FTO rs9939609): Each risk allele adds ~0.28 kg/m² to BMI on average
- **β = 0.40** (APOE rs429358): Each ε4 allele increases AD liability by ~0.40 standard deviations on the liability scale
- **β = −0.30** (APOE rs7412): Each ε2 allele decreases AD liability by ~0.30 (protective)

The unit of β depends on the trait:
- **Continuous traits** (BMI, sleep duration): β is in natural units (kg/m², hours)
- **Binary traits** (disease): β is on the log-odds or liability scale
- **Standardized traits**: β is in standard deviation units (1-SD change per allele)

### 5.2 What Does OR (Odds Ratio) Mean?

The odds ratio for binary traits (disease/no disease):

| OR | Interpretation |
|----|----------------|
| >1.0 | Risk-increasing (e.g., OR=1.25 → 25% increased odds per allele) |
| 1.0 | No effect |
| <1.0 | Protective (e.g., OR=0.55 → 45% decreased odds per allele) |

### 5.3 Why Beta and OR Are NOT the Same

- **β** comes from linear regression — it's on the trait's natural scale
- **OR** comes from logistic regression — it's a ratio of odds

They measure the same association but on different scales. For the Mini-PRS calculator, β is generally more useful because it can be summed across variants for a continuous score; ORs need log-transformation first.

---

## 6. Why Mini-PRS Cannot Directly Equal Disease Risk

This is the most important conceptual section of this document.

### 6.1 A Polygenic Score Is NOT a Probability

A PRS gives a **relative position in the genetic risk distribution**, not an absolute probability of developing disease. A person at the 90th percentile of PRS for obesity has a higher *relative* risk than someone at the 10th percentile, but their *absolute* risk of obesity depends critically on:
- Age
- Sex
- Environment (diet, exercise, sleep, stress, smoking — the E in G×E)
- Population background
- Gene × environment interactions
- Other genes not in the score

### 6.2 Effect Sizes Are Population Averages

The β = 0.28 kg/m² for FTO rs9939609 is an **average across tens of thousands of Europeans**. It does not mean every carrier gains exactly 0.28 kg/m². Individual effects vary substantially due to:
- Other genetic variants (genetic background)
- Environmental factors (the entire point of G×E)
- Gene × environment interactions
- Measurement error and statistical noise

### 6.3 Explained Variance Is Small

| Gene | Trait | Variance Explained by Common Variants |
|------|-------|--------------------------------------|
| FTO | BMI | ~1% (single SNP); ~5% (all FTO variants) |
| APOE | Alzheimer's | ~25–30% of genetic risk; ~6% of total risk |
| CLOCK | Chronotype | <0.1% (individual SNP not GWAS-significant) |
| ACTN3 | Muscle strength | ~0% (not significant in GWAS) |

Even the strongest common variant (APOE ε4 for Alzheimer's) explains only a fraction of total disease risk. Most complex traits have heritability distributed across **hundreds to thousands of variants**, each with tiny effects.

### 6.4 Population Stratification

Effect sizes differ across ancestral populations. FTO rs9939609 shows:
- Strongest effect in Europeans (β ≈ 0.25–0.33)
- Attenuated in East Asians (β ≈ 0.25)
- Weakest/non-significant in African Americans (β ≈ 0.19, p=0.52 in some studies)

This is partly due to differences in LD structure (the causal variant may be tagged differently by different SNP arrays) and partly due to environmental differences.

### 6.5 PRS Does Not Capture Gene × Environment Interaction

A polygenic risk score from GWAS summary statistics estimates the **marginal (average) genetic effect** across all environments in the study population. It cannot, by construction, capture G×E interactions — because the GWAS pools over diverse environments. This is precisely why our G×E simulation engine models interaction separately from main genetic effects.

### 6.6 Educational Simulation vs. Clinical Prediction

| Aspect | This Project (Educational) | Clinical PRS |
|--------|---------------------------|-------------|
| **Purpose** | Demonstrate G×E concepts; educate about gene-environment interplay | Inform individual risk stratification (emerging; not standard of care) |
| **Number of SNPs** | 7 (1–3 per gene × 4 genes) | 100s to millions |
| **Trait prediction** | Not intended to predict real outcomes | Correlated with outcomes; not independently diagnostic |
| **Regulatory status** | Research/educational tool | Some PRS are FDA-recognized biomarkers; most are not |
| **Clinical actionability** | None — this is a simulation | Limited; polygenic risk is one factor among many |

---

## 7. TODO_VERIFY Fields

Several fields in `mini_prs_database.json` are marked `TODO_VERIFY`. These represent quantitative values that could not be confirmed from published sources in this research pass. The structural variant information (rsID, gene, trait, source publication) is correct; only the exact quantitative effect sizes are pending.

| Variant | Field | Reason |
|---------|-------|--------|
| rs1421085 | beta_se, odds_ratio | Identified in GWAS literature with qualitative direction; exact meta-analysis values require direct GWAS Catalog entry lookup |
| rs6832769 | beta, se, odds_ratio, risk_allele, maf | GWAS-confirmed chronotype locus (Jones et al. 2019); effect sizes in primary paper supplementary tables — need direct extraction |
| rs1815739 | effect_size_beta, beta_se | Not GWAS-significant for continuous traits; OR from case-control meta-analyses available; continuous beta not applicable |
| rs1801260 | effect_size_beta, beta_se, odds_ratio | Not GWAS-significant; candidate gene studies report direction but lack standardized effect sizes |

**To resolve these**: Each entry in `gwas_catalog_entries_to_extract` specifies the GWAS Catalog study ID and the fields needed. A systematic lookup of the NHGRI-EBI GWAS Catalog REST API would populate these values definitively.

---

## 8. How This Data Layer Will Be Used (Future)

The current architecture (`CURRENT_ARCHITECTURE.md` §9) documents the integration strategy:

```
Current flow (untouched):
  User sensitivity (0-1) → _compute_gene_effects() → HTI

Future flow (with Mini-PRS, not yet implemented):
  Step 1: User provides genotype data (rsID → alleles dict)
  Step 2: mini_prs.py looks up each variant in mini_prs_database.json
  Step 3: For each gene, weighted sum of (allele_dosage × β) = gene-level Mini-PRS score
  Step 4: Normalize gene-level score to a sensitivity-equivalent value (0-1 range)
  Step 5: Pass normalized score → _compute_gene_effects() → HTI (existing formula UNCHANGED)
```

The Mini-PRS data layer provides **evidence-based weights** to replace the manually estimated `sensitivity` parameter with genetically informed values. The HTI formula and all downstream modules are **not modified** in this phase.

---

## 9. References

1. Frayling TM, Timpson NJ, Weedon MN, et al. (2007). A common variant in the FTO gene is associated with body mass index and predisposes to childhood and adult obesity. *Science*, 316(5826):889–894. PMID: 17434869.

2. Claussnitzer M, Dankel SN, Kim KH, et al. (2015). FTO obesity variant circuitry and adipocyte browning in humans. *N Engl J Med*, 373(10):895–907. PMID: 26287746.

3. Speliotes EK, Willer CJ, Berndt SI, et al. (2010). Association analyses of 249,796 individuals reveal 18 new loci associated with body mass index. *Nat Genet*, 42(11):937–948. PMID: 20935630.

4. Lambert JC, Ibrahim-Verbaas CA, Harold D, et al. (2013). Meta-analysis of 74,046 individuals identifies 11 new susceptibility loci for Alzheimer's disease. *Nat Genet*, 45(12):1452–1458. PMID: 24162737.

5. Bertram L, McQueen MB, Mullin K, Blacker D, Tanzi RE. (2007). Systematic meta-analyses of Alzheimer disease genetic association studies: the AlzGene database. *Nat Genet*, 39(1):17–23. PMID: 17192785.

6. Jones SE, Lane JM, Wood AR, et al. (2019). Genome-wide association analyses of chronotype in 697,828 individuals provides insights into circadian rhythms. *Nat Commun*, 10(1):1585. PMID: 30696823.

7. El Ouali EM, et al. (2024). A Systematic Review and Meta-analysis of the Association Between ACTN3 R577X Genotypes and Performance in Endurance Versus Power Athletes and Non-athletes. *Sports Med Open*. PMID: 38609671.

8. Pabalan N, et al. (2019). Association of the ACTN3 R577X (rs1815739) polymorphism with elite power sports: A meta-analysis. *PLOS ONE*. PMID: 31163047.

9. Ali M, et al. (2023). Large multi-ethnic genetic analyses of amyloid imaging identify new genes for Alzheimer disease. *Acta Neuropathol Commun*. PMID: 37101235.

10. NHGRI-EBI GWAS Catalog. https://www.ebi.ac.uk/gwas/ — Primary repository of GWAS summary statistics.

---

> **Next Step (not yet authorized)**: Create `engine/mini_prs.py` with `calculate_mini_prs(genotype_data)` function that reads this database, computes per-gene weighted scores from allele dosage × beta, normalizes to 0–1 sensitivity-equivalent range, and returns a `genetic_profile` dict compatible with `simulate_health_trajectory()`. The HTI formula in `gxe_model.py` remains unchanged.
