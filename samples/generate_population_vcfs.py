# -*- coding: utf-8 -*-
"""
生成多人种 × 多年龄段 真实基因测序演示报告
============================================
基于真实 SNP 位点（GRCh38 坐标）+ 文献报道的人群等位基因频率，
为每个人种生成符合其真实基因型分布的个人测序 VCF。

数据依据：
  - SNP 位置：Ensembl GRCh38
  - 人群频率：已发表的 GWAS / 人群遗传学研究
    * APOE ε4: 全球~20%，非洲裔~25-30%，欧洲裔~15%，东亚裔~8-10%，拉丁裔~12%
    * FTO rs9939609 A: 欧洲裔~40%，非洲裔~45%，东亚裔~15-20%
    * CLOCK rs1801260 G: 全球~40%
    * ACTN3 R577X T: 全球~45%，非洲裔~20%（TT ~18%全球）
"""
import json
import os
import random
import math

random.seed(42)

# 真实 SNP 数据库（GRCh38）
SNP_DB = [
    {"rs": "rs429358", "chr": "19", "pos": 44908684, "ref": "T", "alt": "C",
     "gene": "APOE", "impact": "APOE ε4 等位基因", "clinsig": "Uncertain_significance"},
    {"rs": "rs7412", "chr": "19", "pos": 44908822, "ref": "C", "alt": "T",
     "gene": "APOE", "impact": "APOE 单倍型", "clinsig": "Uncertain_significance"},
    {"rs": "rs9939609", "chr": "16", "pos": 53786615, "ref": "T", "alt": "A",
     "gene": "FTO", "impact": "BMI 相关", "clinsig": "Uncertain_significance"},
    {"rs": "rs1801260", "chr": "4", "pos": 55435202, "ref": "A", "alt": "G",
     "gene": "CLOCK", "impact": "昼夜节律", "clinsig": "Uncertain_significance"},
    {"rs": "rs1815739", "chr": "11", "pos": 66560624, "ref": "C", "alt": "T",
     "gene": "ACTN3", "impact": "肌肉类型", "clinsig": "Uncertain_significance"},
]

# 各人种的风险等位基因频率（文献报道的真实频率）
# 每个 SNP: {人种: 风险等位基因频率}
POPULATION_FREQ = {
    # rs429358 (C = ε4)
    "rs429358": {"afr": 0.28, "eur": 0.15, "eas": 0.09, "sas": 0.12, "lat": 0.13},
    # rs7412 (T = ε2)
    "rs7412": {"afr": 0.10, "eur": 0.08, "eas": 0.06, "sas": 0.05, "lat": 0.05},
    # rs9939609 (A = risk)
    "rs9939609": {"afr": 0.45, "eur": 0.40, "eas": 0.18, "sas": 0.30, "lat": 0.35},
    # rs1801260 (G)
    "rs1801260": {"afr": 0.35, "eur": 0.40, "eas": 0.38, "sas": 0.36, "lat": 0.37},
    # rs1815739 (T = R577X)
    "rs1815739": {"afr": 0.20, "eur": 0.45, "eas": 0.40, "sas": 0.35, "lat": 0.38},
}

POPULATION_INFO = {
    "afr": {"name": "African", "cn_name": "非洲裔", "country": "Nigeria"},
    "eur": {"name": "European", "cn_name": "欧洲裔", "country": "United Kingdom"},
    "eas": {"name": "East Asian", "cn_name": "东亚裔", "country": "China"},
    "sas": {"name": "South Asian", "cn_name": "南亚裔", "country": "India"},
    "lat": {"name": "Latino", "cn_name": "拉丁裔", "country": "Mexico"},
}

AGE_GROUPS = [8, 25, 45, 65]


def sample_genotype(freq):
    """按频率采样基因型 (0/0, 0/1, 1/1)。"""
    # 哈代-温伯格平衡
    p = 1 - freq  # 参考等位基因
    q = freq      # 风险等位基因
    r = random.random()
    if r < p * p:
        return "0/0"
    elif r < p * p + 2 * p * q:
        return "0/1"
    else:
        return "1/1"


def generate_vcf(pop, age, sex):
    """生成一个人的 VCF。"""
    header = f"""##fileformat=VCFv4.2
##source=GenoLifeAI_genome
##reference=GRCh38
##contig=<ID=4>
##contig=<ID=11>
##contig=<ID=16>
##contig=<ID=19>
##INFO=<ID=GENEINFO,Number=1,Type=String,Description="Gene Name:Gene ID">
##INFO=<ID=CLNSIG,Number=1,Type=String,Description="Clinical Significance">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE
"""
    lines = []
    for snp in SNP_DB:
        freq = POPULATION_FREQ[snp["rs"]][pop]
        gt = sample_genotype(freq)
        info = f"GENEINFO={snp['gene']}:1000;CLNSIG={snp['clinsig']}"
        lines.append(f"{snp['chr']}\t{snp['pos']}\t{snp['rs']}\t{snp['ref']}\t{snp['alt']}\t.\tPASS\t{info}\tGT\t{gt}")

    return header + "\n".join(lines) + "\n"


def main():
    os.makedirs("samples/populations", exist_ok=True)
    manifest = []

    for pop, pop_info in POPULATION_INFO.items():
        for age in AGE_GROUPS:
            for sex in ["M", "F"]:
                vcf = generate_vcf(pop, age, sex)
                filename = f"{pop}_{age}_{sex}.vcf"
                path = f"samples/populations/{filename}"
                with open(path, "w") as f:
                    f.write(vcf)
                manifest.append({
                    "file": filename,
                    "population": pop_info["name"],
                    "cn_population": pop_info["cn_name"],
                    "country": pop_info["country"],
                    "age": age,
                    "sex": sex,
                })
                print(f"✓ {filename}")

    # 生成清单
    with open("samples/populations/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n生成 {len(manifest)} 份报告（5 人种 × 4 年龄 × 2 性别）")


if __name__ == "__main__":
    main()
