"""
上传与分析端点单元测试 — A2.1 / A2.2
======================================
验证 POST /api/upload + GET /api/analysis 的完整链路。

运行方式：
    pytest backend/tests/test_upload.py -v
"""
from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

# 测试前初始化数据库表
@pytest.fixture(scope="module", autouse=True)
def _init_db():
    import asyncio
    from backend.database import init_db

    asyncio.run(init_db())
    yield
    # 清理测试数据库文件（Windows 文件锁忽略）
    for db in ["test_gene_assistant.db", "gene_assistant.db"]:
        try:
            if os.path.exists(db):
                os.remove(db)
        except PermissionError:
            pass

# 测试用 VCF 内容（最小有效格式）
VALID_VCF = """##fileformat=VCFv4.1
##source=test
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
1\t100\trs123\tA\tG\t.\t.\tGENEINFO=APOE;CLNSIG=Pathogenic
7\t117149150\trs113993960\tCTT\tC\t.\t.\tGENEINFO=CFTR;CLNSIG=Pathogenic
17\t43092900\trs80357906\tT\tC\t.\t.\tGENEINFO=BRCA1;CLNSIG=Uncertain_significance
"""

INVALID_VCF = "this is not a vcf file\njust plain text\n"


def test_upload_valid_vcf():
    """上传有效 VCF 应返回 report_id。"""
    r = client.post(
        "/api/upload",
        files={"file": ("test.vcf", io.BytesIO(VALID_VCF.encode()), "text/plain")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    assert "report_id" in data
    assert data["variant_count"] == 3
    assert data["status"] == "completed"


def test_upload_invalid_format():
    """上传非 VCF 应返回 422。"""
    r = client.post(
        "/api/upload",
        files={"file": ("bad.txt", io.BytesIO(INVALID_VCF.encode()), "text/plain")},
    )
    assert r.status_code == 422
    assert "VCF" in r.json()["detail"]


def test_upload_unsupported_extension():
    """不支持的扩展名应返回 422。"""
    r = client.post(
        "/api/upload",
        files={"file": ("data.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert r.status_code == 422
    assert "不支持" in r.json()["detail"]


def test_upload_then_analysis_flow():
    """上传 → 分析 完整闭环。"""
    # 上传
    r = client.post(
        "/api/upload",
        files={"file": ("test.vcf", io.BytesIO(VALID_VCF.encode()), "text/plain")},
    )
    report_id = r.json()["data"]["report_id"]

    # 分析
    r = client.get(f"/api/analysis/{report_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]

    # 报告信息
    assert data["report"]["id"] == report_id
    assert data["report"]["status"] == "completed"
    assert data["report"]["variant_count"] == 3

    # 变异列表
    assert len(data["variants"]) == 3
    first = data["variants"][0]
    assert "chromosome" in first and "position" in first
    assert "gene_name" in first and "clinvar_significance" in first

    # 风险评分
    assert "risk_scores" in data
    assert "overall_risk_level" in data

    # 基因分析档案
    assert "profile" in data
    assert "geneCards" in data["profile"]
    assert "riskDimensions" in data["profile"]


def test_analysis_not_found():
    """不存在的报告应返回 404。"""
    r = client.get("/api/analysis/nonexistent123")
    assert r.status_code == 404


def test_analysis_after_upload_has_annotations():
    """上传的变异应带有 ClinVar 注释。"""
    r = client.post(
        "/api/upload",
        files={"file": ("test.vcf", io.BytesIO(VALID_VCF.encode()), "text/plain")},
    )
    report_id = r.json()["data"]["report_id"]

    r = client.get(f"/api/analysis/{report_id}")
    variants = r.json()["data"]["variants"]

    # APOE / CFTR / BRCA1 应保留基因名
    gene_names = {v["gene_name"] for v in variants}
    assert "APOE" in gene_names
    assert "CFTR" in gene_names
    assert "BRCA1" in gene_names
