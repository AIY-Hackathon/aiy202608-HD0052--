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


def build_profile(variants: list[dict] | None = None) -> dict:
    """构建完整基因档案（可复用，便于测试）。"""
    variants = variants or []

    # 1. 基因卡片
    gene_cards = engine.generate_gene_cards(variants)

    # 2. 风险维度
    risk_dimensions = engine.calculate_dimension_scores(variants)

    # 3. 健康概览
    avg_score = int(round(sum(d["score"] for d in risk_dimensions) / len(risk_dimensions)))
    # 平均风险分映射到健康分（分数越高 = 风险越低 = 健康越好）
    health_score = max(35, min(98, 100 - avg_score + 20))
    if health_score >= 80:
        level, level_label = "low", "Low Genetic Risk"
    elif health_score >= 60:
        level, level_label = "moderate", "Moderate Genetic Risk"
    else:
        level, level_label = "high", "Elevated Genetic Risk"

    summary_text = (
        "您的基因档案显示整体健康倾向良好。"
        "生活方式因素对健康轨迹有显著影响，积极调整可改善长期结果。"
        if variants
        else "正在分析您的基因数据。当前展示为基于常见基因位点的参考档案。"
    )

    # 4. 组装
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
    }


@router.get("/profile", response_model=ApiResponse)
def get_profile():
    """获取基因分析档案（概览 + 基因卡片 + 风险维度）。"""
    variants = _load_variants_from_db()
    profile = build_profile(variants)
    return ApiResponse.ok(profile)
