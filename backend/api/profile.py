"""
GET /api/profile — 基因分析档案
=================================
返回健康概览、基因卡片、风险维度（对齐前端 mockData 结构）。

真实数据流程：
  1. 从数据库读取用户最近的基因报告变异（若存在）
  2. 调用基因分析引擎生成 geneCards / riskDimensions / healthSummary
  3. 若无真实数据，返回基于默认基因的演示档案
"""
from __future__ import annotations

import os
import sys

# 确保能导入 backend 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter

from backend.schemas import (
    ApiResponse,
    GeneticProfile,
    GeneCard,
    HealthSummary,
    RiskDimension,
    UserProfile,
)
from backend.services import prs_calculator as engine

router = APIRouter(prefix="/api", tags=["profile"])


def _load_variants_from_db():
    """从数据库加载最近报告的变异（真实分析）。

    返回变异字典列表；无数据时返回空列表。
    """
    try:
        from backend.database import SessionLocal
        from backend.models import GeneticReport, GeneticVariant
        from sqlalchemy import select, desc

        # 异步会话
        import asyncio

        async def _query():
            async with SessionLocal() as session:
                # 找最近的报告
                result = await session.execute(
                    select(GeneticReport)
                    .where(GeneticReport.parsing_status == "completed")
                    .order_by(desc(GeneticReport.created_at))
                    .limit(1)
                )
                report = result.scalars().first()
                if not report:
                    return []

                # 加载其变异
                result = await session.execute(
                    select(GeneticVariant).where(GeneticVariant.report_id == report.id)
                )
                variants = result.scalars().all()
                return [
                    {
                        "id": v.id,
                        "gene_name": v.gene_name,
                        "chromosome": v.chromosome,
                        "position": v.position,
                        "clinvar_significance": v.clinvar_significance,
                        "odds_ratio": v.odds_ratio,
                        "risk_score": v.risk_score,
                        "rs_id": v.rs_id,
                    }
                    for v in variants
                ]

        return asyncio.run(_query())
    except Exception as e:
        print(f"[profile] 数据库读取失败（使用演示数据）: {e}")
        return []


def _run_mini_prs(variants: list[dict]) -> dict | None:
    """调用 Mini-PRS 引擎（GWAS 证据权重），从变异提取 genotype 计算。

    引擎需要 {"rsID": "genotype"} 格式。从变异中提取 rsID 和参考/替代等位基因，
    构造 genotype（简化：有变异记录视为杂合，缺失视为纯合参考）。
    """
    try:
        from engine.mini_prs import calculate_mini_prs

        # 从变异提取 rsID → genotype
        genotype_data: dict[str, str] = {}
        for v in variants:
            rs = v.get("rs_id")
            if rs and rs not in genotype_data:
                ref = v.get("reference") or "A"
                alt = v.get("alternative") or "G"
                # 简化：变异存在记为杂合（ref/alt），实际应结合 GT 字段
                genotype_data[rs] = f"{ref}{alt}"

        if not genotype_data:
            return None

        result = calculate_mini_prs(genotype_data)

        # 精简返回（避免过大）
        return {
            "version": result.get("meta", {}).get("version"),
            "genetic_profile": result.get("genetic_profile"),
            "apoe_haplotype": result.get("apoe_haplotype_profile", {}).get("haplotype"),
            "apoe_risk_category": result.get("apoe_haplotype_profile", {}).get("risk_category"),
            "biological_modifiers": result.get("biological_modifiers"),
            "evidence_summary": result.get("evidence_summary"),
            "variants_found": result.get("meta", {}).get("variants_found"),
        }
    except Exception as e:
        print(f"[profile] Mini-PRS 引擎调用失败: {e}")
        return None


def build_profile(variants: list[dict] | None = None, population: str | None = None) -> dict:
    """构建完整基因档案（可复用，便于测试）。

    Args:
        variants: 变异列表
        population: 可选，用户人群。传入时关键基因按人群频率校准。
    """
    variants = variants or []

    # 1. 基因卡片
    gene_cards = engine.generate_gene_cards(variants)

    # 2. 风险维度
    risk_dimensions = engine.calculate_dimension_scores(variants)

    # 3. 关键基因抓取 + 科学分析（支持人群维度）
    scientific = engine.generate_scientific_analysis(variants, population=population)

    # 4. Mini-PRS 科学引擎增强（GWAS 证据权重）
    mini_prs = _run_mini_prs(variants)

    # 5. 健康概览
    # 健康指数基于样本实际携带的变异贡献（72 基线 ± 变异影响），
    # 让不同基因型样本产生明显差异。
    if variants:
        dims_avg = sum(d["score"] for d in risk_dimensions) / len(risk_dimensions)
        # 维度分相对基线 50 的偏移 → 风险方向（>50 = 风险升）
        risk_deviation = dims_avg - 50
        health_score = round(72 - risk_deviation * 1.6)
        health_score = max(35, min(98, health_score))
    else:
        health_score = 72
    if health_score >= 80:
        level, level_label = "low", "Low Genetic Risk"
    elif health_score >= 60:
        level, level_label = "moderate", "Moderate Genetic Risk"
    else:
        level, level_label = "high", "Elevated Genetic Risk"

    # 有科学分析时用真实总结
    summary_text = scientific.get("summary") if variants else (
        "正在分析您的基因数据。当前展示为基于常见基因位点的参考档案。"
    )

    # 5. 组装
    return {
        "user": {"name": "用户", "healthScore": health_score, "geneticAge": 0, "chronologicalAge": 0},
        "summary": {
            "score": health_score,
            "level": level,
            "levelLabel": level_label,
            "aiSummary": summary_text,
        },
        "geneCards": gene_cards,
        "riskDimensions": risk_dimensions,
        "scientificAnalysis": scientific,
        "miniPrs": mini_prs,
    }


@router.get("/profile", response_model=ApiResponse)
def get_profile():
    """获取基因分析档案（概览 + 基因卡片 + 风险维度）。"""
    variants = _load_variants_from_db()
    profile = build_profile(variants)
    return ApiResponse.ok(profile)
