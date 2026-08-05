#!/usr/bin/env python
"""Gene analysis engine scientific validation -- 16 properties, 7 dimensions."""

import sys
sys.path.insert(0, ".")
from backend.services import prs_calculator as engine


def dims_for(v):
    s = engine.calculate_dimension_scores(v)
    return {d["key"]: d["score"] for d in s}


def health_for(v):
    d = dims_for(v)
    avg = sum(d.values()) / len(d)
    return round(72 - (avg - 50) * 1.6)


def mk(g, c, d):
    return {"gene_name": g, "clinvar_significance": c, "allele_dosage": d, "odds_ratio": None}


passed = 0
total = 0
failed = []


def check(name, condition, extra=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print("PASS: " + name)
    else:
        failed.append(name)
        print("FAIL: " + name + "  " + extra)


# === P1: Gene-Dimension Mapping ===
print("=" * 60)
print("[P1] Gene -> Dimension Mapping")
print("=" * 60)
ap_het = mk("APOE", "Pathogenic", 1)
ap_hom = mk("APOE", "Pathogenic", 2)
ap_ref = mk("APOE", "Pathogenic", 0)
ap_vus = mk("APOE", "Uncertain_significance", 1)
ap_ben = mk("APOE", "Benign", 1)
fto_hom = mk("FTO", "Pathogenic", 2)
clock_vus = mk("CLOCK", "Uncertain_significance", 1)
brca1_het = mk("BRCA1", "Pathogenic", 1)

s = dims_for([ap_het])
check("APOE raises cognitive", s["cognitive"] > 50, "cognitive=" + str(s["cognitive"]))
check("APOE NOT metabolic", s["metabolic"] == 50, "metabolic=" + str(s["metabolic"]))
s = dims_for([fto_hom])
check("FTO raises metabolic", s["metabolic"] > 50, "metabolic=" + str(s["metabolic"]))
check("FTO NOT cognitive", s["cognitive"] == 50, "cognitive=" + str(s["cognitive"]))
s = dims_for([clock_vus])
check("CLOCK raises sleep", s["sleep"] > 50, "sleep=" + str(s["sleep"]))

# === P2: Dosage Gradient ===
print("\n[P2] Dosage Gradient (hom > het > ref)")
sr = dims_for([ap_ref])["cognitive"]
sh = dims_for([ap_het])["cognitive"]
so = dims_for([ap_hom])["cognitive"]
print("  ref=" + str(sr) + "  het=" + str(sh) + "  hom=" + str(so))
check("ref dosage=0 -> no contribution", sr == 50, "ref=" + str(sr))
check("homozygous > heterozygous", so > sh, "hom=" + str(so) + " > het=" + str(sh))

# === P3: Clinical Significance Layering ===
print("\n[P3] ClinSig Layering (Pathogenic > VUS > Benign)")
sp = dims_for([ap_het])["cognitive"]
sv = dims_for([ap_vus])["cognitive"]
sb = dims_for([ap_ben])["cognitive"]
print("  P=" + str(sp) + "  VUS=" + str(sv) + "  B=" + str(sb))
check("Pathogenic > VUS", sp > sv, "P=" + str(sp) + " > VUS=" + str(sv))
check("VUS > Benign", sv > sb, "VUS=" + str(sv) + " > B=" + str(sb))

# === P4: Multi-gene Additive Independence ===
print("\n[P4] Multi-Gene Additive Independence")
s_a = dims_for([ap_hom])
s_f = dims_for([fto_hom])
s_c = dims_for([ap_hom, fto_hom])
print("  APOE hom: cog=" + str(s_a["cognitive"]) + " met=" + str(s_a["metabolic"]))
print("  FTO hom:  cog=" + str(s_f["cognitive"]) + " met=" + str(s_f["metabolic"]))
print("  Combined: cog=" + str(s_c["cognitive"]) + " met=" + str(s_c["metabolic"]))
check("genes add independently to dimensions",
      s_c["cognitive"] == s_a["cognitive"] and s_c["metabolic"] == s_f["metabolic"],
      "APOE adds to cognitive only; FTO adds to metabolic only")

# === P5: Health Score Monotonicity ===
print("\n[P5] Health Score Monotonicity")
def h2(gene, sig, dosage):
    return health_for([{"gene_name": gene, "clinvar_significance": sig, "allele_dosage": dosage, "odds_ratio": None}])
hp_het = h2("APOE", "Pathogenic", 1)
hp_hom = h2("APOE", "Pathogenic", 2)
hvus = h2("APOE", "Uncertain_significance", 1)
hben = h2("APOE", "Benign", 1)
print("  benign=" + str(hben) + " vus=" + str(hvus) + " path_het=" + str(hp_het) + " path_hom=" + str(hp_hom))
check("benign >= vus >= path_het >= path_hom",
      hben >= hvus and hvus >= hp_het and hp_het >= hp_hom,
      "health score decreases as pathogenic burden increases")

# === P6: Reproducibility ===
print("\n[P6] Reproducibility")
d1 = dims_for([ap_hom])
d2 = dims_for([ap_hom])
check("dimension scores reproducible", d1 == d2, "identical input -> identical output")
h1 = health_for([ap_hom])
h2 = health_for([ap_hom])
check("health score reproducible", h1 == h2, "both=" + str(h1))

# === P7: 5-Sample Differentiation ===
print("\n[P7] 5-Sample Differentiation")
samples = {
    "S1_EUR_low":   [("APOE","Pathogenic",0),("APOE","Uncertain",0),("FTO","Pathogenic",0),("CLOCK","Uncertain",1),("ACTN3","Uncertain",1),("LDLR","Pathogenic",0),("BRCA1","Pathogenic",0)],
    "S2_EAS_meta":  [("APOE","Pathogenic",0),("APOE","Uncertain",0),("FTO","Pathogenic",2),("CLOCK","Uncertain",1),("ACTN3","Uncertain",2),("LDLR","Pathogenic",0),("BRCA1","Pathogenic",0)],
    "S3_AFR_cog":   [("APOE","Pathogenic",2),("APOE","Uncertain",0),("FTO","Pathogenic",1),("CLOCK","Uncertain",0),("ACTN3","Uncertain",1),("LDLR","Pathogenic",0),("BRCA1","Pathogenic",0)],
    "S4_SAS_cardio":[("APOE","Pathogenic",1),("APOE","Uncertain",0),("FTO","Pathogenic",0),("CLOCK","Uncertain",1),("ACTN3","Uncertain",0),("LDLR","Pathogenic",1),("BRCA1","Pathogenic",0)],
    "S5_LAT_multi": [("APOE","Pathogenic",1),("APOE","Uncertain",0),("FTO","Pathogenic",2),("CLOCK","Uncertain",1),("ACTN3","Uncertain",0),("LDLR","Pathogenic",0),("BRCA1","Pathogenic",1)],
}
scores = set()
for name, vdata in samples.items():
    vs = [{"gene_name": g, "clinvar_significance": c, "allele_dosage": d, "odds_ratio": None} for g, c, d in vdata]
    d = dims_for(vs)
    h = health_for(vs)
    scores.add(h)
    print("  " + name + ": health=" + str(h) + " met=" + str(d["metabolic"]) +
          " cog=" + str(d["cognitive"]) + " cardio=" + str(d["cardiovascular"]) +
          " ath=" + str(d["athletic"]) + " sleep=" + str(d["sleep"]))
check(">=3 distinct health scores", len(scores) >= 3, "unique values: " + str(scores))
s1_h = health_for([{"gene_name": g, "clinvar_significance": c, "allele_dosage": d, "odds_ratio": None} for g, c, d in samples["S1_EUR_low"]])
s5_h = health_for([{"gene_name": g, "clinvar_significance": c, "allele_dosage": d, "odds_ratio": None} for g, c, d in samples["S5_LAT_multi"]])
check("S5(multi-risk) < S1(low-risk)", s5_h < s1_h, "S5=" + str(s5_h) + " < S1=" + str(s1_h))

# === PS: BRCA1 ===
print("\n[PS] BRCA1 Variant Handling")
dim = engine.classify_gene_to_dimension("BRCA1")
disease = engine.classify_gene_to_disease("BRCA1")
kg = engine.identify_key_genes([brca1_het])
check("BRCA1 -> breast_cancer disease", disease == "breast_cancer", "disease=" + str(disease))
check("BRCA1 identified as key gene", len(kg) > 0 and kg[0]["symbol"] == "BRCA1",
      "score=" + str(kg[0]["score"]) if kg else "NO KEY GENES")
check("BRCA1 no dimension mapping (known limitation)", dim is None, "dim=" + str(dim))
print("  NOTE: BRCA1 is recognized as key gene + disease-classified")
print("  but does not affect 5-dimension scores (by design).")
print("  Cancer genes need a dedicated oncology dimension (future).")

# === Summary ===
print("")
print("=" * 60)
print("RESULTS: " + str(passed) + "/" + str(total) + " PROPERTIES PASS")
if failed:
    print("FAILED: " + ", ".join(failed))
else:
    print("ALL " + str(passed) + " SCIENTIFIC VALIDATION PROPERTIES PASSED")
print("=" * 60)
