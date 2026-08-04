"""
VCF 解析器单元测试 — A1.3
==========================
用真实 ClinVar VCF 文件验证解析正确性。

运行方式：
    pytest backend/tests/test_vcf_parser.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.vcf_parser import (  # noqa: E402
    VCFParseError,
    count_variants,
    is_vcf,
    parse_info,
    parse_vcf_pandas,
    parse_vcf_records,
)

# 真实 ClinVar 数据文件路径
# 优先取环境变量 CLINVAR_PATH，否则用默认相对路径
CLINVAR_PATH = os.environ.get(
    "CLINVAR_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "clinvar", "clinvar_grch38.vcf.gz",
    ),
)

HAS_CLINVAR = os.path.exists(CLINVAR_PATH)


# ============ INFO 解析测试 ============

def test_parse_info_basic():
    info = "GENEINFO=CFTR;CLNSIG=Pathogenic;CLNREVSTAT=reviewed_by_expert_panel"
    result = parse_info(info)
    assert result["GENEINFO"] == "CFTR"
    assert result["CLNSIG"] == "Pathogenic"
    assert result["CLNREVSTAT"] == "reviewed_by_expert_panel"


def test_parse_info_empty():
    assert parse_info("") == {}
    assert parse_info(".") == {}


def test_parse_info_flag():
    """无值的标志位应返回 True。"""
    result = parse_info("DB")
    assert result["DB"] is True


# ============ 文件格式检测 ============

@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_is_vcf_clinvar():
    assert is_vcf(CLINVAR_PATH) is True


def test_is_vcf_not_vcf(tmp_path):
    p = tmp_path / "not_vcf.txt"
    p.write_text("just some text\nnot a vcf\n")
    assert is_vcf(str(p)) is False


# ============ 真实数据解析 ============

@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_count_variants_clinvar():
    """真实 ClinVar 应有约 4.4M 变异。"""
    count = count_variants(CLINVAR_PATH, max_lines=100000)
    assert count > 50000  # 至少 5 万条以上


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_parse_clinvar_small():
    """解析前 5000 条变异。"""
    records = parse_vcf_records(CLINVAR_PATH, max_variants=5000)
    assert len(records) == 5000

    # 验证第一条记录的字段
    first = records[0]
    assert first["chromosome"] in {"1", "2", "X", "Y"} or first["chromosome"].isdigit()
    assert first["position"] > 0
    assert first["reference"] in {"A", "C", "G", "T"} or len(first["reference"]) > 0
    assert first["alternative"] in {"A", "C", "G", "T", "N"} or len(first["alternative"]) > 0


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_parse_clinvar_pandas_columns():
    """pandas 方案应返回标准 VCF 列。"""
    df = parse_vcf_pandas(CLINVAR_PATH, max_variants=100)
    assert not df.empty
    assert "CHROM" in df.columns
    assert "POS" in df.columns
    assert "INFO" in df.columns
    assert "REF" in df.columns
    assert "ALT" in df.columns


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_parse_clinvar_info_extraction():
    """INFO 字段中的基因和临床意义应被提取。"""
    records = parse_vcf_records(CLINVAR_PATH, max_variants=200)
    # 至少有些记录有 gene_name 或 clinvar_significance
    has_gene = sum(1 for r in records if r["gene_name"])
    has_clinsig = sum(1 for r in records if r["clinvar_significance"])
    # ClinVar 绝大多数记录应有注释
    assert has_gene > 100
    assert has_clinsig > 100


def test_parse_missing_file():
    with pytest.raises(VCFParseError):
        parse_vcf_pandas("nonexistent.vcf")


def test_parse_invalid_file(tmp_path):
    p = tmp_path / "bad.vcf"
    p.write_text("hello\nworld\n")
    with pytest.raises(VCFParseError):
        parse_vcf_pandas(str(p))
