"""
ClinVar 查询客户端单元测试 — A1.4
==================================
用真实 ClinVar VCF 文件验证本地查询。

运行方式：
    CLINVAR_PATH=... pytest backend/tests/test_clinvar.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.clinvar_client import ClinVarClient, ClinVarIndex  # noqa: E402

# ClinVar 数据路径（环境变量可覆盖）
CLINVAR_PATH = os.environ.get(
    "CLINVAR_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "clinvar", "clinvar_grch38.vcf.gz",
    ),
)

HAS_CLINVAR = os.path.exists(CLINVAR_PATH)


@pytest.fixture(scope="module")
def index():
    """共享索引（模块级，只加载一次）。"""
    idx = ClinVarIndex(CLINVAR_PATH)
    if HAS_CLINVAR:
        idx.load()
    return idx


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_index_loads(index):
    assert index.is_loaded


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_query_known_variant(index):
    """查询已知位点：chr1 上游位置（ClinVar 第一个变异）。"""
    # 从 VCF 文件确认第一个变异的真实坐标
    import gzip
    with gzip.open(CLINVAR_PATH, "rt", errors="ignore") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            chrom, pos = parts[0].replace("chr", ""), int(parts[1])
            break

    results = index.query(chrom, pos)
    assert len(results) >= 1
    v = results[0]
    assert v.chromosome == chrom
    assert v.position == pos
    # ClinVar 应有临床意义注释
    assert v.clinical_significance is not None


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_query_unknown_position(index):
    """查询不存在的位点应返回空。"""
    results = index.query("X", 999999999)  # 超出范围
    assert results == []


@pytest.mark.skipif(not HAS_CLINVAR, reason="ClinVar 数据未下载")
def test_client_annotate(index):
    """客户端 annotate 接口应返回字典。"""
    client = ClinVarClient(use_cache=False)
    client._index = index  # 复用已加载的索引

    # 查询第一个变异
    import gzip
    with gzip.open(CLINVAR_PATH, "rt", errors="ignore") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            chrom, pos = parts[0].replace("chr", ""), int(parts[1])
            break

    result = client.annotate(chrom, pos)
    assert result is not None
    assert "chromosome" in result
    assert "clinical_significance" in result


def test_client_returns_none_without_data(monkeypatch):
    """本地数据缺失 + 在线查询失败时应返回 None（不崩溃）。"""
    client = ClinVarClient(use_cache=False)
    # 手动覆盖 index 为不存在路径
    client._index = ClinVarIndex("/nonexistent/clinvar.vcf.gz")
    # 模拟在线查询也失败
    monkeypatch.setattr(client, "_query_online", lambda c, p: None)
    result = client.annotate("1", 100)
    assert result is None
