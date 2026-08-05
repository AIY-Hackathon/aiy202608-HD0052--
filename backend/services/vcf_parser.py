"""
VCF 文件解析器 — A1.3
======================
将 VCF（Variant Call Format）基因报告解析为结构化变异列表。

支持两种解析方案：
  1. pandas（推荐，快速）—— 读取全量数据
  2. pysam（标准）—— 若已安装，支持索引查询

ClinVar VCF 格式说明：
  - 以 ## 开头的行是元数据注释
  - #CHROM 行是列头
  - 数据行：CHROM  POS  ID  REF  ALT  QUAL  FILTER  INFO  FORMAT  ...
  - INFO 字段用 ; 分隔的 key=value，如 GENEINFO=CFTR;CLNSIG=Pathogenic

依赖：pandas（已安装）
"""
from __future__ import annotations

import gzip
import os
from typing import Iterator

import pandas as pd

# ClinVar VCF 的固定列名（9 个标准列 + 样本列）
VCF_COLUMNS = [
    "CHROM", "POS", "ID", "REF", "ALT",
    "QUAL", "FILTER", "INFO", "FORMAT",
]

# 可能包含路径的列名（用引号包裹防止 pandas 误判）
INFO_KEYS = {"GENEINFO", "CLNSIG", "CLNREVSTAT"}


class VCFParseError(Exception):
    """VCF 解析错误。"""


def is_vcf(filepath: str) -> bool:
    """检测文件是否为 VCF 格式（检查文件头，支持 gzip/普通文本）。"""
    try:
        with open_maybe_gzip(filepath) as f:
            for line in f:
                if line.startswith("##fileformat=VCF"):
                    return True
                if line.startswith("#CHROM"):
                    return True
                if line.startswith("##"):
                    continue
                break
    except Exception:
        pass
    return False


def open_maybe_gzip(filepath: str):
    """透明打开 gzip 或普通文件。"""
    if filepath.endswith(".gz"):
        return gzip.open(filepath, "rt", errors="ignore")
    return open(filepath, "rt", errors="ignore")


def parse_info(info_str: str) -> dict:
    """解析 INFO 字段（分号分隔的 key=value）。"""
    result: dict = {}
    if not info_str or info_str == ".":
        return result
    for item in info_str.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            result[k] = v
        else:
            result[item] = True  # 无值标志
    return result


def _extract_gene_name(info: dict) -> str | None:
    """从多种 INFO 字段来源提取基因名。

    优先级：
      1. ClinVar VCF: GENEINFO=PAH:5053
      2. ANNOVAR: Gene.refGene, Gene.ensGene
      3. VEP: SYMBOL, Gene
      4. 通用: GENE
    """
    # ClinVar VCF
    geneinfo = info.get("GENEINFO") or info.get("geneinfo")
    if geneinfo and isinstance(geneinfo, str):
        gene = geneinfo.split(":")[0].strip()
        if gene:
            return gene

    # ANNOVAR 格式
    for key in ("Gene.refGene", "Gene.ensGene", "Gene.refgene", "Gene.ensgene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()

    # VEP / Ensembl VEP 格式
    for key in ("SYMBOL", "GENE", "Gene", "gene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()

    return None


def variant_to_dict(row: pd.Series) -> dict:
    """将一行 VCF 数据转换为标准变异字典（对齐 schemas.VariantOut）。

    额外解析 GT 基因型字段（FORMAT=GT，样本列为 0/0、0/1、1/1 等）：
      - genotype: 原始 GT 字符串，如 "0/1"
      - allele_dosage: 风险/变异等位基因剂量（0/1/2），纯合变异=2，杂合=1
      - homozygous: 是否纯合变异（1/1）
    """
    info = parse_info(str(row.get("INFO", "")))

    # 解析 GT：FORMAT 列在倒数第 2 列，样本列在最后一列
    result = {
        "chromosome": str(row["CHROM"]).replace("chr", ""),
        "position": int(row["POS"]),
        "rs_id": None if row["ID"] in (".", "") else str(row["ID"]),
        "reference": str(row["REF"]),
        "alternative": str(row["ALT"]),
        # INFO 中提取的注释（多来源 gene_name）
        "gene_name": _extract_gene_name(info),
        "clinvar_significance": info.get("CLNSIG") or None,
        "clinvar_review_status": info.get("CLNREVSTAT") or None,
    }

    # GT 基因型：最后一列是样本列（如 0/1），倒数第 2 列是 FORMAT（含 GT）
    sample = row.get("SAMPLE") or row.get("FORMAT")
    gt = None
    if sample is not None:
        sample_str = str(sample).strip()
        # GT 通常是 "0/1"、"1/1"、"./.", 或 "0|1"（phased）
        if "/" in sample_str or "|" in sample_str:
            gt = sample_str
    if gt is None:
        # 尝试从 FORMAT 定位 GT 位置
        fmt = str(row.get("FORMAT", "")).split(":")
        if "GT" in fmt and sample is not None:
            idx = fmt.index("GT")
            fields = str(sample).split(":")
            if idx < len(fields):
                gt = fields[idx]

    if gt:
        result["genotype"] = gt.replace("|", "/")
        allele = gt.replace("|", "/").split("/")
        # 计算变异等位基因剂量（非 0 即为变异等位基因）
        try:
            dosage = sum(1 for a in allele if a not in ("0", "."))
            result["allele_dosage"] = dosage
            result["homozygous"] = dosage == 2
        except (ValueError, TypeError):
            pass

    return result


def parse_vcf_pandas(filepath: str, max_variants: int | None = None) -> pd.DataFrame:
    """使用 pandas 解析 VCF 文件。

    Args:
        filepath: VCF 文件路径（支持 .gz）
        max_variants: 最多读取的变异数（None = 全部）

    Returns:
        包含 VCF 标准列的 DataFrame
    """
    if not os.path.exists(filepath):
        raise VCFParseError(f"文件不存在: {filepath}")

    # 确认是 VCF
    if not is_vcf(filepath):
        raise VCFParseError(f"不是有效的 VCF 文件: {filepath}")

    # pandas 读取：跳过 ## 注释行，用 #CHROM 行做列头
    # comment="#" 会跳过所有 # 开头的行，但也会跳过列头。
    # 所以用 header=None 手动指定列名。
    try:
        df = pd.read_csv(
            filepath,
            sep="\t",
            comment="#",
            header=None,
            dtype=str,
            nrows=max_variants,
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=VCF_COLUMNS)

    # 只保留有数据的行
    if df.empty or df.shape[1] < 8:
        return pd.DataFrame(columns=VCF_COLUMNS)

    # 赋值列名（取前 10 列：9 标准列 + 样本列；若有多样本取第一个）
    # 赋值列名（取前 10 列：9 标准列 + 样本列；若列数不足则只赋存在的列名）
    n_cols = min(df.shape[1], 10)
    df = df.iloc[:, :n_cols]
    cols = VCF_COLUMNS[:n_cols]
    if n_cols == 10:
        cols = VCF_COLUMNS[:9] + ["SAMPLE"]
    df.columns = cols

    # 过滤变异行（POS 必须是数字）
    df["POS"] = pd.to_numeric(df["POS"], errors="coerce")
    df = df.dropna(subset=["POS"])
    return df


def parse_vcf_records(filepath: str, max_variants: int | None = None) -> list[dict]:
    """解析 VCF 文件为变异字典列表（对齐 schemas.VariantOut）。"""
    df = parse_vcf_pandas(filepath, max_variants)
    return [variant_to_dict(row) for _, row in df.iterrows()]


def count_variants(filepath: str, max_lines: int | None = None) -> int:
    """快速统计变异数量（不构建 DataFrame，节省内存）。"""
    count = 0
    with open_maybe_gzip(filepath) as f:
        for line in f:
            if line.startswith("#"):
                continue
            count += 1
            if max_lines and count >= max_lines:
                break
    return count


def iter_variant_records(filepath: str, chunk: int = 10000) -> Iterator[list[dict]]:
    """分批迭代解析 VCF（适合大文件，避免一次加载全部到内存）。"""
    reader = pd.read_csv(
        filepath,
        sep="\t",
        comment="#",
        header=None,
        dtype=str,
        chunksize=chunk,
    )
    for df in reader:
        if df.empty or df.shape[1] < 8:
            continue
        n_cols = min(df.shape[1], 10)
        df = df.iloc[:, :n_cols]
        cols = VCF_COLUMNS[:n_cols]
        if n_cols == 10:
            cols = VCF_COLUMNS[:9] + ["SAMPLE"]
        df.columns = cols
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce")
        df = df.dropna(subset=["POS"])
        yield [variant_to_dict(row) for _, row in df.iterrows()]
