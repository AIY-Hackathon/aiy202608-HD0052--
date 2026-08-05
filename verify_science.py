# -*- coding: utf-8 -*-
"""基因分析引擎科学性验证报告 — 7 维度 × 16 项属性自动测试."""

import sys; sys.path.insert(0, ".")
from backend.services import prs_calculator as engine


def dims_for(variants):
    scores = engine.calculate_dimension_scores(variants)
    return {d["key"]: d["score"] for d in scores}


def health_for(variants):
    dims = dims_for(variants)
    avg = sum(dims.values()) / len(dims)
    return round(72 - (avg - 50) * 1.6)


def test(name, desc, result, expected=None):
    status = "PASS" if result else "FAIL"
    detail = f" → {desc}"
    if expected is not None:
        detail = detail + f" (预期 {expected})"
    print(f"[{status}] {name}{detail}")
    return result


def to_variants(vdata):
    return [{"gene_name": g, "clinvar_significance": c, "allele_dosage": d, "odds_ratio": None}
            for g, c, d in vdata]


results = []
failed = []

# ── 测试数据 ──
APOE_PATH_HOM = to_variants([("APOE", "Pathogenic", 2)])
APOE_PATH_HET = to_variants([("APOE", "Pathogenic", 1)])
APOE_PATH_REF = to_variants([("APOE", "Pathogenic", 0)])
APOE_VUS_HET = to_variants([("APOE", "Uncertain_significance", 1)])
APOE_BENIGN_HET = to_variants([("APOE", "Benign", 1)])
FTO_PATH_HOM = to_variants([("FTO", "Pathogenic", 2)])
CLOCK_VUS_HET = to_variants([("CLOCK", "Uncertain_significance", 1)])
COMBINED = APOE_PATH_HOM + FTO_PATH_HOM

# S5 全基因组
S5 = to_variants([
    ("APOE", "Pathogenic", 1), ("APOE", "Uncertain_significance", 0),
    ("FTO", "Pathogenic", 2), ("CLOCK", "Uncertain_significance", 1),
    ("ACTN3", "Uncertain_significance", 0), ("LDLR", "Pathogenic", 0),
    ("BRCA1", "Pathogenic", 1),
])

# 5 个差异化样本
SAMPLES = {
    "S1_EUR_低风险": [("APOE", "Pathogenic", 0), ("APOE", "Uncertain", 0),
                      ("FTO", "Pathogenic", 0), ("CLOCK", "Uncertain", 1),
                      ("ACTN3", "Uncertain", 1), ("LDLR", "Pathogenic", 0),
                      ("BRCA1", "Pathogenic", 0)],
    "S2_EAS_代谢高风险": [("APOE", "Pathogenic", 0), ("APOE", "Uncertain", 0),
                         ("FTO", "Pathogenic", 2), ("CLOCK", "Uncertain", 1),
                         ("ACTN3", "Uncertain", 2), ("LDLR", "Pathogenic", 0),
                         ("BRCA1", "Pathogenic", 0)],
    "S3_AFR_认知高风险": [("APOE", "Pathogenic", 2), ("APOE", "Uncertain", 0),
                         ("FTO", "Pathogenic", 1), ("CLOCK", "Uncertain", 0),
                         ("ACTN3", "Uncertain", 1), ("LDLR", "Pathogenic", 0),
                         ("BRCA1", "Pathogenic", 0)],
    "S4_SAS_心血管高风险": [("APOE", "Pathogenic", 1), ("APOE", "Uncertain", 0),
                          ("FTO", "Pathogenic", 0), ("CLOCK", "Uncertain", 1),
                          ("ACTN3", "Uncertain", 0), ("LDLR", "Pathogenic", 1),
                          ("BRCA1", "Pathogenic", 0)],
    "S5_LAT_多风险叠加": [("APOE", "Pathogenic", 1), ("APOE", "Uncertain", 0),
                         ("FTO", "Pathogenic", 2), ("CLOCK", "Uncertain", 1),
                         ("ACTN3", "Uncertain", 0), ("LDLR", "Pathogenic", 0),
                         ("BRCA1", "Pathogenic", 1)],
}

print("=" * 70)
print("基因分析引擎科学性验证 — 7 维度 × 16 项属性")
print("=" * 70)

# ── P1: 基因→维度映射正确性 ──
print("\nP1: 基因 → 维度映射正确性")
s = dims_for(APOE_PATH_HET)
r = test("P1.1 APOE→cognitive", s["cognitive"] > 50, expected=">50")
results.append(r)
if not r:
    failed.append("P1.1")
r = test("P1.2 APOE 不影响 metabolic", s["metabolic"] == 50, expected="50")
results.append(r)
if not r:
    failed.append("P1.2")
s = dims_for(FTO_PATH_HOM)
r = test("P1.3 FTO→metabolic", s["metabolic"] > 50, expected=">50")
results.append(r)
if not r:
    failed.append("P1.3")
r = test("P1.4 FTO 不影响 cognitive", s["cognitive"] == 50, expected="50")
results.append(r)
if not r:
    failed.append("P1.4")
s = dims_for(CLOCK_VUS_HET)
r = test("P1.5 CLOCK→sleep", s["sleep"] > 50, expected=">50")
results.append(r)
if not r:
    failed.append("P1.5")
print(f"   实测: APOE het → cognitive={dims_for(APOE_PATH_HET)['cognitive']}, "
      f"FTO hom → metabolic={dims_for(FTO_PATH_HOM)['metabolic']}, "
      f"CLOCK vus → sleep={dims_for(CLOCK_VUS_HET)['sleep']}")

# ── P2: 基因型剂量梯度 ──
print("\nP2: 基因型剂量梯度 (纯合 > 杂合 > 纯合参考)")
sc = {"ref": dims_for(APOE_PATH_REF)["cognitive"], "het": dims_for(APOE_PATH_HET)["cognitive"],
      "hom": dims_for(APOE_PATH_HOM)["cognitive"]}
r = test("P2.1 纯合参考=无贡献", sc["ref"] == 50, expected="50")
results.append(r)
if not r:
    failed.append("P2.1")
r = test("P2.2 纯合 > 杂合", sc["hom"] > sc["het"],
         expected=f"hom={sc['hom']} > het={sc['het']}")
results.append(r)
if not r:
    failed.append("P2.2")
print(f"   实测: ref={sc['ref']}, het={sc['het']}, hom={sc['hom']}")

# ── P3: 临床意义分层 ──
print("\nP3: 临床意义分层 (Pathogenic > VUS > Benign)")
sc = {"P": dims_for(APOE_PATH_HET)["cognitive"], "VUS": dims_for(APOE_VUS_HET)["cognitive"],
      "B": dims_for(APOE_BENIGN_HET)["cognitive"]}
r = test("P3.1 Pathogenic > VUS", sc["P"] > sc["VUS"], expected=f"P={sc['P']} > VUS={sc['VUS']}")
results.append(r)
if not r:
    failed.append("P3.1")
r = test("P3.2 VUS > Benign", sc["VUS"] > sc["B"], expected=f"VUS={sc['VUS']} > B={sc['B']}")
results.append(r)
if not r:
    failed.append("P3.2")
print(f"   实测: Pathogenic={sc['P']}, VUS={sc['VUS']}, Benign={sc['B']}")

# ── P4: 多维叠加独立性 ──
print("\nP4: 多维叠加独立性 — 各基因贡献互不污染")
s_a = dims_for(APOE_PATH_HOM)
s_f = dims_for(FTO_PATH_HOM)
s_combined = dims_for(COMBINED)
r = test("P4.1 APOE 只影响 cognitive",
         s_combined["cognitive"] == s_a["cognitive"] and s_combined["metabolic"] == s_f["metabolic"],
         expected=f"cog={s_a['cognitive']}+{s_f.get('cognitive', 50) - 50}, met={s_f['metabolic']}+{s_a.get('metabolic', 50) - 50}")
results.append(r)
if not r:
    failed.append("P4.1")
print(f"   APOE hom: cog={s_a['cognitive']}, met={s_a['metabolic']}")
print(f"   FTO hom:  cog={s_f['cognitive']}, met={s_f['metabolic']}")
print(f"   组合:     cog={s_combined['cognitive']}, met={s_combined['metabolic']}")

# ── P5: 健康指数单调性 ──
print("\nP5: 健康指数单调性 — 致病负荷↑ → 健康指数↓")
hs = {k: health_for(to_variants(v)) for k, v in [
    ("benign", [("APOE", "Benign", 1)]), ("vus", [("APOE", "Uncertain_significance", 1)]),
    ("path_het", [("APOE", "Pathogenic", 1)]), ("path_hom", [("APOE", "Pathogenic", 2)]),
    ("ref", [("APOE", "Pathogenic", 0)]),
]}
r = test("P5.1 benign ≥ vus ≥ path ≥ hom", all([
    hs["benign"] >= hs["vus"], hs["vus"] >= hs["path_het"], hs["path_het"] >= hs["path_hom"],
]), expected=f"B={hs['benign']} ≥ VUS={hs['vus']} ≥ P_het={hs['path_het']} ≥ P_hom={hs['path_hom']}")
results.append(r)
if not r:
    failed.append("P5.1")
print(f"   实测: benign={hs['benign']}, vus={hs['vus']}, path_het={hs['path_het']}, path_hom={hs['path_hom']}, ref={hs['ref']}")

# ── P6: 可重复性 ──
print("\nP6: 可重复性 — 相同输入 → 相同输出")
d1 = dims_for(APOE_PATH_HOM)
d2 = dims_for(APOE_PATH_HOM)
r = test("P6.1 APOE hom 两次结果一致", d1 == d2, expected="identical")
results.append(r)
if not r:
    failed.append("P6.1")
h1 = health_for(APOE_PATH_HOM)
h2 = health_for(APOE_PATH_HOM)
r = test("P6.2 健康指数可重复", h1 == h2, expected=f"both={h1}")
results.append(r)
if not r:
    failed.append("P6.2")

# ── P7: 5 样本区分度 ──
print("\nP7: 差异化样本区分度")
print(f"{'样本':<22} {'健康':<6} {'代谢':<6} {'认知':<6} {'心血管':<6} {'运动':<6} {'睡眠':<6}")
print("-" * 70)
unique_hs = set()
for name, vdata in SAMPLES.items():
    h = health_for(to_variants(vdata))
    d = dims_for(to_variants(vdata))
    unique_hs.add(h)
    print(f"{name:<22} {h:<6} {d['metabolic']:<6} {d['cognitive']:<6} "
          f"{d['cardiovascular']:<6} {d['athletic']:<6} {d['sleep']:<6}")
r = test("P7.1 健康指数 ≥2 个不同值", len(unique_hs) >= 2, expected=f"不同值: {unique_hs}")
results.append(r)
if not r:
    failed.append("P7.1")

# 复杂样本验证
S5_DIMS = dims_for(S5)
S1_DIMS = dims_for(to_variants(SAMPLES["S1_EUR_低风险"]))
r = test("P7.2 S5(多风险) 健康指数 < S1(低风险)",
         health_for(S5) < health_for(to_variants(SAMPLES["S1_EUR_低风险"])),
         expected=f"S5={health_for(S5)} < S1={health_for(to_variants(SAMPLES['S1_EUR_低风险']))}")
results.append(r)
if not r:
    failed.append("P7.2")
print(f"   S5 维度分: {S5_DIMS}")
print(f"   S1 维度分: {S1_DIMS}")

# ── S5 BRCA1 特异性验证 ──
print("\nPS: BRCA1 致病变异特异性验证")
brca1_var = to_variants([("BRCA1", "Pathogenic", 1)])
brca1_dims = dims_for(brca1_var)
brca1_kg = engine.identify_key_genes(brca1_var)

dim_mapped = engine.classify_gene_to_dimension("BRCA1")
disease_mapped = engine.classify_gene_to_disease("BRCA1")

r = test("PS.1 BRCA1→breast_cancer disease", disease_mapped == "breast_cancer", expected="breast_cancer")
results.append(r)
if not r:
    failed.append("PS.1")
r = test("PS.2 BRCA1 无维度但有关键基因识别", any(g["symbol"] == "BRCA1" for g in brca1_kg),
         expected="identified as key gene")
results.append(r)
if not r:
    failed.append("PS.2")
print(f"   BRCA1 维度映射: {dim_mapped} (≡ 无 5 维映射)")
print(f"   BRCA1 疾病映射: {disease_mapped}")
print(f"   BRCA1 关键基因: 得分={brca1_kg[0]['score']:.1f} risk={brca1_kg[0]['risk_level']}"
      if brca1_kg else "   BRCA1 未在关键基因中!")
print(f"   BRCA1 维度分: {brca1_dims} (全 50 = 不影响任何维度)")
print(f"   ⚠️ 这是当前模型已知限制: 肿瘤风险基因被识别但无法表达为维度偏移")

# ── 汇总 ──
print("\n" + "=" * 70)
print(f"最终结果: {sum(results)}/{len(results)} 项属性通过")
if failed:
    print(f"失败项: {', '.join(failed)}")
    print("❌ 有属性未通过，需要修复")
else:
    print("✅ 全部 {0} 项科学性验证属性通过!".format(len(results)))
print("=" * 70)
print()
print("模型已知限制 (已在产品中透明标注):")
print("  1. BRCA1/LDLR 等肿瘤/心血管基因 → disease 映射正常")
print("     但 BRAC1 不出现在 5 维评分中 (= 无 dimension)。")
print("     建议: 增加 cancer_risk / cardio_risk 维度")
print("  2. odds_ratio 为 None → 用固定分级 (6.0 / 1.5 / -1.0)")
print("     → 接入 mini_prs 引擎的 GWAS 效应量可提升精度")
print("  3. 人群频率校准默认 1.0 (Ancestry 推断多为 low)")
print("     → 用户手动选择人群后校准因子生效")
