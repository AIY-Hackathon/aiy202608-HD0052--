"""
POST /api/upload — 基因报告上传
================================
接收 VCF 文件，解析变异，ClinVar 注释，写入数据库。

流程：
  1. 校验文件格式（VCF）
  2. 保存文件到 uploads/
  3. 解析变异（vcf_parser）
  4. ClinVar 注释（clinvar_client，本地优先）
  5. 写入 genetic_reports + genetic_variants 表
  6. 返回 report_id

关联需求：R1.1 / R1.2 / R1.7
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.schemas import ApiResponse
from backend.services import prs_calculator as engine
from backend.services.clinvar_client import ClinVarClient
from backend.services.vcf_parser import VCFParseError, is_vcf, parse_vcf_records

router = APIRouter(prefix="/api", tags=["upload"])

# 上传目录（gitignore 排除）
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件格式
ALLOWED_EXTENSIONS = {".vcf", ".vcf.gz", ".tsv", ".txt"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# ClinVar 客户端（模块级单例，索引只加载一次）
_clinvar_client: ClinVarClient | None = None


def _get_clinvar_client() -> ClinVarClient:
    global _clinvar_client
    if _clinvar_client is None:
        _clinvar_client = ClinVarClient(use_cache=True)
    return _clinvar_client


def _save_upload(file: UploadFile) -> tuple[str, str, int]:
    """保存上传文件，返回 (文件路径, 原始文件名, 大小)。"""
    filename = file.filename or "upload"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"不支持的文件格式 {ext}，支持: {ALLOWED_EXTENSIONS}",
        )

    # 读取并检查大小
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件超过 100MB 限制")

    # 保存（用 uuid 前缀避免文件名冲突）
    safe_name = f"{uuid.uuid4().hex[:8]}_{os.path.basename(filename)}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    with open(filepath, "wb") as f:
        f.write(content)

    return filepath, filename, len(content)


def _annotate_variants(variants: list[dict]) -> list[dict]:
    """为每个变异添加 ClinVar 注释（本地优先）。"""
    client = _get_clinvar_client()
    for v in variants:
        try:
            annotation = client.annotate(
                v["chromosome"], v["position"], v["reference"], v["alternative"]
            )
            if annotation:
                if not v.get("gene_name"):
                    v["gene_name"] = annotation.get("gene_name")
                if not v.get("clinvar_significance"):
                    v["clinvar_significance"] = annotation.get("clinical_significance")
                if not v.get("clinvar_review_status"):
                    v["clinvar_review_status"] = annotation.get("review_status")
                if not v.get("rs_id"):
                    v["rs_id"] = annotation.get("rs_id")
        except Exception as e:
            print(f"[upload] 变异 {v['chromosome']}:{v['position']} 注释失败: {e}")
    return variants


async def _save_to_db(variants: list[dict], original_filename: str, file_format: str, file_size: int) -> str:
    """异步写入数据库，返回 report_id。"""
    from backend.database import SessionLocal
    from backend.models import GeneticReport, GeneticVariant

    async with SessionLocal() as session:
        report = GeneticReport(
            original_filename=original_filename,
            file_format=file_format,
            file_size=file_size,
            parsing_status="completed",
            variant_count=len(variants),
            processed_at=datetime.now(timezone.utc),
        )
        session.add(report)
        await session.flush()

        for v in variants:
            variant = GeneticVariant(
                report_id=report.id,
                chromosome=v.get("chromosome", ""),
                position=v.get("position", 0),
                reference=v.get("reference", ""),
                alternative=v.get("alternative", ""),
                rs_id=v.get("rs_id"),
                gene_name=v.get("gene_name"),
                clinvar_significance=v.get("clinvar_significance"),
                clinvar_review_status=v.get("clinvar_review_status"),
                odds_ratio=v.get("odds_ratio"),
                population_frequency=v.get("population_frequency"),
                genotype=v.get("genotype"),
                allele_dosage=v.get("allele_dosage"),
                risk_score=engine.risk_score_for_variant(
                    v.get("clinvar_significance"), v.get("odds_ratio")
                ),
            )
            session.add(variant)

        await session.commit()
        return report.id


@router.post("/upload", response_model=ApiResponse)
async def upload_report(file: UploadFile = File(...)):
    """上传基因报告文件（VCF/TSV），解析并分析。"""
    # 1. 保存文件
    try:
        filepath, original_filename, file_size = _save_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {e}")

    file_format = "vcf" if original_filename.lower().endswith((".vcf", ".vcf.gz")) else "tsv"

    # 2. 校验 VCF 格式
    if file_format == "vcf" and not is_vcf(filepath):
        raise HTTPException(status_code=422, detail="不是有效的 VCF 文件（缺少 ##fileformat=VCF 头）")

    # 3. 解析变异
    try:
        variants = parse_vcf_records(filepath, max_variants=50000)
    except VCFParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {e}")

    if not variants:
        raise HTTPException(status_code=422, detail="未解析到任何变异，请检查文件内容")

    # 4. ClinVar 注释
    variants = _annotate_variants(variants)

    # 5. 入库
    try:
        report_id = await _save_to_db(variants, original_filename, file_format, file_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {e}")

    return ApiResponse.ok({
        "report_id": report_id,
        "variant_count": len(variants),
        "status": "completed",
        "original_filename": original_filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
