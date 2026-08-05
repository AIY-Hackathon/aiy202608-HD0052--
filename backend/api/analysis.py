"""
GET /api/analysis/{report_id} — 分析结果
==========================================
根据报告 ID 返回基因分析结果。

返回内容：
  - report: 报告元信息
  - variants: 变异列表（含 ClinVar 注释 + 风险评分）
  - risk_scores: 疾病风险倍数（PRS）
  - profile: 基因分析档案（geneCards / riskDimensions，对齐前端）

关联需求：R1.3 / R1.4 / R1.5
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, HTTPException, Query

from backend.api.profile import build_profile
from backend.schemas import ApiResponse
from backend.services import prs_calculator as engine

router = APIRouter(prefix="/api", tags=["analysis"])


async def _load_report(report_id: str):
    """从数据库加载报告及其变异。"""
    from backend.database import SessionLocal
    from backend.models import GeneticReport, GeneticVariant
    from sqlalchemy import select

    async with SessionLocal() as session:
        report = await session.get(GeneticReport, report_id)
        if not report:
            return None, []
        result = await session.execute(
            select(GeneticVariant).where(GeneticVariant.report_id == report_id)
        )
        variants = result.scalars().all()
        return report, variants


def _variants_to_dicts(variants) -> list[dict]:
    """ORM 变异对象 → 字典。"""
    return [
        {
            "id": v.id,
            "chromosome": v.chromosome,
            "position": v.position,
            "reference": v.reference,
            "alternative": v.alternative,
            "rs_id": v.rs_id,
            "gene_name": v.gene_name,
            "clinvar_significance": v.clinvar_significance,
            "clinvar_review_status": v.clinvar_review_status,
            "odds_ratio": v.odds_ratio,
            "population_frequency": v.population_frequency,
            "risk_score": v.risk_score,
            "genotype": v.genotype,
            "allele_dosage": v.allele_dosage,
        }
        for v in variants
    ]


@router.get("/analysis/{report_id}", response_model=ApiResponse)
async def get_analysis(report_id: str, population: str | None = Query(None)):
    """获取基因分析结果。

    Args:
        report_id: 报告 ID
        population: 可选，用户人群（东亚/欧洲/非洲/南亚/拉丁 或 EAS/EUR/AFR/SAS/LAT）。
                    传入时关键基因选择会按人群频率校准。
    """
    report, variants = await _load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"报告 {report_id} 不存在")

    variant_dicts = _variants_to_dicts(variants)

    # 疾病风险（PRS）
    prs = engine.calculate_prs(variant_dicts)

    # 基因分析档案（支持人群参数）
    profile = build_profile(variant_dicts, population=population)

    # 祖先推断（辅助参考）
    ancestry = _infer_ancestry(variant_dicts)

    return ApiResponse.ok({
        "report": {
            "id": report.id,
            "filename": report.original_filename,
            "format": report.file_format,
            "status": report.parsing_status,
            "variant_count": report.variant_count,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        },
        "variants": variant_dicts[:200],  # 前端只显示前 200 条
        "risk_scores": prs["risk_scores"],
        "overall_risk_level": prs["overall_risk_level"],
        "confidence_intervals": prs["confidence_intervals"],
        "profile": profile,
        "ancestry": ancestry,
    })


def _infer_ancestry(variant_dicts: list[dict]) -> dict | None:
    """调用祖先推断引擎（尽力而为，失败返回 None）。"""
    try:
        from engine.ancestry import infer_ancestry
        return infer_ancestry(variant_dicts)
    except Exception as e:
        print(f"[analysis] 祖先推断失败: {e}")
        return None


@router.get("/analysis/{report_id}/ancestry", response_model=ApiResponse)
async def get_ancestry(report_id: str):
    """获取人群祖先推断结果（辅助参考，低置信度时提示用户手动确认）。"""
    report, variants = await _load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"报告 {report_id} 不存在")

    variant_dicts = _variants_to_dicts(variants)
    result = _infer_ancestry(variant_dicts)
    return ApiResponse.ok(result)
