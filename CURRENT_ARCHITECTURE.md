# CURRENT_ARCHITECTURE — Part C G×E Health Simulation Engine

> **Date**: 2026-08-05  
> **Branch analyzed**: `part-c-engine` (commit `1398fdc`)  
> **Status**: As-is analysis — no modifications made.  
> **Purpose**: Understand current system before adding evidence-based Mini-PRS weight layer.

---

## 1. File Layout

```
AIY-Program/
├── engine/                              # [Part C] G×E Engine (branch: part-c-engine)
│   ├── __init__.py                      # Package entry, exposes public API
│   ├── config.py                        # ★ All weights & parameters live here
│   ├── gxe_model.py                     # ★ Core HTI simulation engine
│   ├── counterfactual.py                # What-If + Scenario Comparison
│   ├── ai_interpreter.py                # 6-field explainable AI output
│   ├── recommendation_engine.py         # Personalized recommendations
│   ├── report_generator.py              # HTML/PDF report generation
│   ├── knowledge/
│   │   └── gene_database.json           # Gene knowledge base (4 genes)
│   └── tests/
│       └── test_gxe.py                  # 32 unit tests
│
├── backend/                             # [Part A] FastAPI (on main branch)
│   ├── api/
│   │   ├── simulate.py                  # POST /api/simulate → calls prs_calculator
│   │   └── recommendations.py           # GET /api/recommendations → calls prs_calculator
│   ├── services/
│   │   └── prs_calculator.py            # ★ Legacy engine (Part A's own calculator)
│   └── schemas.py                       # Pydantic request/response models
│
└── genolife-ai/                         # [Part B] React Frontend
    └── src/api/client.js                # Frontend API client (auto-mock fallback)
```

---

## 2. Where Everything Is Defined

### 2.1 Gene Weights

| File | Variable | Lines | Description |
|------|----------|-------|-------------|
| `engine/config.py` | `GENE_WEIGHTS` | 20–62 | 4 genes × 7 fields each. Each gene has 5 dimension weights (cognitive/cardiovascular/metabolic/athletic/sleep) + overall_health + base_effect + time_multiplier |
| `backend/services/prs_calculator.py` | `DIMENSION_GENE_MAP` | 22–28 | Gene→dimension classification (which gene maps to which health dimension). Separate, simpler system. |
| `backend/services/prs_calculator.py` | `GENE_CARD_META` | 49–59 | Display metadata for UI gene cards |

**Key observation**: There are TWO gene weight systems:
- `engine/config.py::GENE_WEIGHTS` — Used by Part C engine. Each gene has per-dimension float weights.
- `backend/services/prs_calculator.py::DIMENSION_GENE_MAP` — Used by Part A backend. Simple set-based classification (gene belongs to dimensions {metabolic, cognitive, ...}).

These two systems are **NOT connected**. The `/api/simulate` endpoint calls `prs_calculator`, NOT `engine/gxe_model.py`.

### 2.2 Environment Weights

| File | Variable | Lines | Description |
|------|----------|-------|-------------|
| `engine/config.py` | `ENVIRONMENT_WEIGHTS` | 68–118 | 5 factors × per-dimension weights + overall_health + description + reference |
| `engine/config.py` | `ENVIRONMENT_RANGES` | 257–263 | Valid ranges, optimal values, units for each factor |

### 2.3 G×E Interaction Coefficients

| File | Variable | Lines | Description |
|------|----------|-------|-------------|
| `engine/config.py` | `INTERACTION_COEFFICIENTS` | 126–159 | 4×5 matrix (gene × factor) with per-pair float coefficients |

The interaction matrix:

| Gene | exercise | sleep | diet | stress | smoking |
|------|----------|-------|------|--------|---------|
| APOE | +0.20 | +0.15 | +0.18 | +0.12 | **-0.05** |
| FTO | +0.25 | +0.10 | +0.22 | +0.08 | +0.05 |
| CLOCK | +0.12 | +0.30 | +0.10 | +0.20 | +0.08 |
| ACTN3 | +0.35 | +0.08 | +0.10 | +0.05 | +0.03 |

Plus = beneficial interaction, Minus = adverse interaction.

### 2.4 HTI Formula

**Where**: `engine/gxe_model.py` lines 210–225 (`_compute_baseline_hti`)

```
HTI = baseline_hti (72)
    + gene_effect_clipped      # max ±40 (gene_contribution_ceiling = 0.40)
    + environment_effect_clipped  # max ±60 (environment_contribution_ceiling = 0.60)
    + interaction_effect_clipped  # max ±15 (interaction_contribution_range = ±0.15)
```

**Gene effect** (line 123–146): `sensitivity × avg_dim_weight × base_effect × 100`

**Environment effect** (line 152–181): `deviation × overall_weight × 100`
- Forward factors (exercise/sleep/diet): `deviation = (value - optimal) / range`
- Reverse factors (stress/smoking): `deviation = (optimal - value) / range`

**Interaction effect** (line 179–203): `sensitivity × env_deviation × interaction_coefficient × 50`

**Time trajectory** (line 232–283):
```
trajectory[t] = HTI - net_decay
annual_decay_rate = 0.5 × (1 + gene_time_risk) × env_amplifier
recovery = env_buffer × total_decay × 0.25
```

### 2.5 API Endpoints

| Endpoint | File | What it calls | Current Status |
|----------|------|---------------|----------------|
| `POST /api/simulate` | `backend/api/simulate.py` | `prs_calculator.calculate_health_score()` | Uses old engine (Part A) |
| `GET /api/recommendations` | `backend/api/recommendations.py` | `prs_calculator.generate_recommendations()` | Uses old engine (Part A) |

**Critical finding**: The FastAPI endpoints do NOT call `engine/gxe_model.py`. They call `backend/services/prs_calculator.py`, which is a completely separate calculation system with its own simpler formulas (linear health score based on 4 factors, no G×E interaction, no time trajectory).

The Part C engine (`engine/gxe_model.py`) has a `calculate_gxe()` collaboration interface ready (line 494–513), but it is **not yet wired** into the API endpoints.

---

## 3. Data Flow (Current)

```
User Input (React Frontend)
    │
    ▼
POST /api/simulate (backend/api/simulate.py)
    │
    ├─→ prs_calculator.calculate_health_score(factors)     ← OLD engine
    ├─→ prs_calculator.calculate_dimension_scores_with_factors([], factors)
    ├─→ prs_calculator.generate_trend_data([], factors)
    └─→ prs_calculator.generate_recommendations(factors)
            │
            ▼
    JSON Response → Frontend renders chart

NOTE: engine/gxe_model.py is NEVER called in the API flow.
      It exists as a standalone importable module only.
```

```
Developer/CLI
    │
    ▼
engine/gxe_model.simulate_health_trajectory(genetic_profile, environment)
    │
    ├─→ _compute_gene_effects()      ← uses GENE_WEIGHTS
    ├─→ _compute_environment_effects()  ← uses ENVIRONMENT_WEIGHTS
    ├─→ _compute_interaction_effects()  ← uses INTERACTION_COEFFICIENTS
    ├─→ _compute_baseline_hti()      ← HTI formula
    └─→ _compute_trajectory()        ← Time decay
            │
            ▼
    Dict with HTI, trajectory, dimension_scores, factor_analysis
    → consumed by ai_interpreter.py, counterfactual.py, recommendation_engine.py
```

---

## 4. Module Dependency Graph

```
engine/config.py
    ├── ← engine/gxe_model.py (imports all config constants)
    ├── ← engine/counterfactual.py (imports COUNTERFACTUAL_CONFIG, ENVIRONMENT_RANGES)
    ├── ← engine/ai_interpreter.py (reads gene_database.json separately)
    └── ← engine/recommendation_engine.py (imports GENE_WEIGHTS, ENVIRONMENT_WEIGHTS, etc.)

engine/gxe_model.py
    ├── ← engine/counterfactual.py (imports simulate_health_trajectory)
    ├── ← engine/ai_interpreter.py (imports simulate_health_trajectory in __main__)
    └── ← engine/recommendation_engine.py (imports simulate_health_trajectory in __main__)

engine/knowledge/gene_database.json
    └── ← engine/ai_interpreter.py (reads via _load_gene_db())

backend/api/simulate.py
    └── ← backend/services/prs_calculator.py (NOT engine/gxe_model.py)
```

---

## 5. What Modules Should Be PRESERVED (No Changes Needed)

| Module | Reason |
|--------|--------|
| `engine/counterfactual.py` | Works correctly as-is. Calls `simulate_health_trajectory()`. If HTI formula changes, it automatically picks up the new calculation. |
| `engine/ai_interpreter.py` | Mock mode works. Reads simulation output dict keys. If new keys are added to output, interpreter can be extended without breaking existing fields. |
| `engine/report_generator.py` | Pure rendering. Generates HTML from whatever data dict it receives. No calculation logic. |
| `engine/knowledge/gene_database.json` | Reference data. Can be extended with Mini-PRS fields without breaking existing structure. |
| `engine/tests/test_gxe.py` | Tests should pass after additions. New tests will be added for Mini-PRS. |
| `backend/schemas.py` | API contract. Should not change unless new endpoints are needed. |

## 6. What Modules Should Be EXTENDED (Add Mini-PRS Layer)

| Module | What to add |
|--------|-------------|
| `engine/config.py` | New section: `MINI_PRS_WEIGHTS` — per-gene, per-SNP evidence-based weights from GWAS Catalog. New section: `SNP_TO_GENE_MAP` — rsID → gene mapping for genotype parsing. |
| `engine/gxe_model.py` | New function: `_compute_mini_prs(genotype_data)` — calculate PRS from SNP-level data. Optionally override/replace `_compute_gene_effects()` with evidence-weighted version. |
| `engine/knowledge/gene_database.json` | Add `prs_variants` array to each gene: list of rsIDs with effect sizes (OR/β), population frequency, and GWAS study references. |

## 7. What Modules Are REDUNDANT (Dual Systems)

| System | File | Role |
|--------|------|------|
| **Old engine** | `backend/services/prs_calculator.py` | Simple linear formula. No G×E, no time trajectory. Used by API endpoints. |
| **New engine** | `engine/gxe_model.py` | Full G×E + time + dimension decomposition. NOT wired to API. |

**Recommendation**: Do NOT delete `prs_calculator.py` (it serves the API). Instead, add Mini-PRS to `engine/` and later wire `engine/gxe_model.py` to the API as an alternative endpoint or a new `/api/simulate/v2` endpoint.

---

## 8. Summary of Current Formulas

### Gene Effect
```
effect[gene] = sensitivity × avg(dimension_weights) × base_effect × 100
```
- `avg(dimension_weights)` = mean of 5 non-zero dimension weights for that gene
- `base_effect` = fixed per-gene scalar (0.20–0.35)
- `sensitivity` = user input 0.0–1.0

### Environment Effect
```
effect[factor] = ((value - optimal) / range) × overall_health_weight × 100
```
- Reverse for stress/smoking: `(optimal - value) / range`

### G×E Interaction Effect
```
effect[gene×factor] = sensitivity × ((env_value - optimal) / range) × interaction_coef × 50
```

### Baseline HTI
```
HTI = clamp(72 + gene_total + env_total + interaction_total, 20, 95)
```

### Time Trajectory
```
annual_decay = 0.5 × (1 + Σ(sensitivity × (time_multiplier - 1))) × env_amplifier
env_amplifier = 1.0 + (1.0 - env_buffer) × 1.5
trajectory[t] = HTI - (annual_decay × t) + (env_buffer × annual_decay × t × 0.25)
```
- `env_buffer` ∈ [0,1]: 1 = perfect environment, 0 = worst

---

## 9. Mini-PRS Integration Strategy

The Mini-PRS layer should be ADDED (not replace):

```
Current flow:
  User sensitivity (0-1) → _compute_gene_effects() → HTI

Future flow (with Mini-PRS):
  User genotype (rsID + alleles) → _compute_mini_prs() → gene-level risk score
    → _compute_gene_effects(mini_prs_scores) → HTI

OR: Keep current flow, ADD parallel path:
  User genotype → _compute_mini_prs() → evidence_weighted_profile
  └→ _compute_gene_effects(weighted_profile) → HTI with evidence annotation
```

The key insight: current `genetic_profile` is a dict of `{gene_name: sensitivity_float}`. Mini-PRS can enhance this by COMPUTING the sensitivity from actual SNP data using GWAS effect sizes, rather than using manually estimated values. This adds scientific rigor without breaking any existing functionality.

---

> **Next step**: Add `engine/mini_prs.py` with SNP→gene→weight calculation, extend `engine/config.py` with GWAS-derived SNP weight tables, and extend `engine/gxe_model.py` to accept genotype data alongside or instead of sensitivity profiles.
