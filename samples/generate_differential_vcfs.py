# -*- coding: utf-8 -*-
"""
生成 5 个高风险差异样本 VCF（展示 Pathogenic / VUS 风险区分度）
================================================================
每个样本刻意设计为不同的遗传风险画像 + 不同人群背景：

  S1 欧洲裔 · 低风险   — 全部良性/参考基因型
  S2 东亚裔 · 代谢高风险 — FTO Pathogenic 纯合 + CLOCK VUS
  S3 非洲裔 · 认知高风险 — APOE ε4 Pathogenic 纯合
  S4 南亚裔 · 心血管高风险 — LDLR Pathogenic 杂合 + APOE ε4 携带
  S5 拉丁裔 · 多风险叠加 — BRCA1 Pathogenic 杂合 + FTO VUS 纯合

坐标基于 GRCh38（Ensembl）。Pathogenic 位点取自 ClinVar 常见致病变异：
  - FTO rs9939609       chr16:53786615  (Intron 1, BMI 关联)
  - APOE rs429358       chr19:44908684  (ε4 定义 SNP)
  - LDLR rs121908025    chr19:11216260  (家族性高胆固醇血症致病变异)
  - BRCA1 rs80357906    chr17:43092900  (乳腺癌/卵巢癌致病变异)
  - CLOCK rs1801260     chr4:55435202   (昼夜节律 VUS)
  - ACTN3 rs1815739     chr11:66560624  (运动表现多态性)
  - APOE rs7412         chr19:44908822  (ε2 定义 SNP)
"""
import os

# (rs_id, chr, pos, ref, alt, gene, clinsig, impact)
SNP_DB = [
    ("rs429358",   "19", 44908684, "T", "C", "APOE",   "Pathogenic",            "APOE ε4 等位基因"),
    ("rs7412",     "19", 44908822, "C", "T", "APOE",   "Uncertain_significance", "APOE 单倍型"),
    ("rs9939609",  "16", 53786615, "T", "A", "FTO",    "Pathogenic",            "BMI 关联致病变异"),
    ("rs1801260",  "4",  55435202, "A", "G", "CLOCK",  "Uncertain_significance", "昼夜节律 VUS"),
    ("rs1815739",  "11", 66560624, "C", "T", "ACTN3",  "Uncertain_significance", "运动表现多态性"),
    ("rs121908025","19", 11216260, "G", "A", "LDLR",   "Pathogenic",            "家族性高胆固醇血症"),
    ("rs80357906", "17", 43092900, "T", "C", "BRCA1",  "Pathogenic",            "乳腺癌/卵巢癌风险"),
]

# 每个样本: 基因型映射 {rs_id: "0/0"|"0/1"|"1/1"}
SAMPLES = [
    {
        "file": "s1_eur_low_risk.vcf",
        "population": "European",
        "cn": "欧洲裔",
        "risk": "低风险",
        "genotypes": {
            "rs429358": "0/0", "rs7412": "0/0",   # APOE ε3/ε3 常见
            "rs9939609": "0/0",                    # FTO 无风险等位基因
            "rs1801260": "0/1", "rs1815739": "0/1",
            "rs121908025": "0/0", "rs80357906": "0/0",
        },
    },
    {
        "file": "s2_eas_metabolic_high.vcf",
        "population": "East Asian",
        "cn": "东亚裔",
        "risk": "代谢高风险",
        "genotypes": {
            "rs429358": "0/0", "rs7412": "0/0",
            "rs9939609": "1/1",                    # FTO 纯合风险 → 代谢维度显著升高
            "rs1801260": "0/1",                    # CLOCK VUS 杂合
            "rs1815739": "1/1",
            "rs121908025": "0/0", "rs80357906": "0/0",
        },
    },
    {
        "file": "s3_afr_cognitive_high.vcf",
        "population": "African",
        "cn": "非洲裔",
        "risk": "认知高风险",
        "genotypes": {
            "rs429358": "1/1",                    # APOE ε4 纯合 → 认知维度显著升高
            "rs7412": "0/0",
            "rs9939609": "0/1",
            "rs1801260": "0/0",
            "rs1815739": "0/1",
            "rs121908025": "0/0", "rs80357906": "0/0",
        },
    },
    {
        "file": "s4_sas_cardio_high.vcf",
        "population": "South Asian",
        "cn": "南亚裔",
        "risk": "心血管高风险",
        "genotypes": {
            "rs429358": "0/1",                    # APOE ε4 杂合
            "rs7412": "0/0",
            "rs9939609": "0/0",
            "rs1801260": "0/1",
            "rs1815739": "0/0",
            "rs121908025": "0/1",                 # LDLR 杂合致病 → 心血管升高
            "rs80357906": "0/0",
        },
    },
    {
        "file": "s5_lat_multirisk.vcf",
        "population": "Latino",
        "cn": "拉丁裔",
        "risk": "多风险叠加",
        "genotypes": {
            "rs429358": "0/1",                    # APOE ε4 杂合
            "rs7412": "0/0",
            "rs9939609": "1/1",                   # FTO 纯合风险
            "rs1801260": "0/1",
            "rs1815739": "0/0",
            "rs121908025": "0/0",
            "rs80357906": "0/1",                  # BRCA1 杂合致病 → 肿瘤风险
        },
    },
]


def generate_vcf(sample: dict) -> str:
    header = f"""##fileformat=VCFv4.2
##source=GenoLifeAI_genome
##reference=GRCh38
##contig=<ID=4>
##contig=<ID=11>
##contig=<ID=16>
##contig=<ID=17>
##contig=<ID=19>
##INFO=<ID=GENEINFO,Number=1,Type=String,Description="Gene Name:Gene ID">
##INFO=<ID=CLNSIG,Number=1,Type=String,Description="Clinical Significance">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE
"""
    lines = []
    for rs, chr_, pos, ref, alt, gene, clinsig, impact in SNP_DB:
        gt = sample["genotypes"].get(rs, "0/0")
        info = f"GENEINFO={gene}:1000;CLNSIG={clinsig}"
        lines.append(f"{chr_}\t{pos}\t{rs}\t{ref}\t{alt}\t.\tPASS\t{info}\tGT\t{gt}")
    return header + "\n".join(lines) + "\n"


def main():
    os.makedirs("samples/differential", exist_ok=True)
    manifest = []
    for s in SAMPLES:
        path = os.path.join("samples/differential", s["file"])
        with open(path, "w") as f:
            f.write(generate_vcf(s))
        manifest.append({
            "file": s["file"],
            "population": s["population"],
            "cn_population": s["cn"],
            "risk_profile": s["risk"],
        })
        print(f"✓ {s['file']}  [{s['cn']} · {s['risk']}]")

    import json
    with open(os.path.join("samples/differential/manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n生成 {len(SAMPLES)} 份差异化样本")


if __name__ == "__main__":
    main()
