"""
POST /api/simulate — 婴儿早期成长环境模拟
===========================================
使用 Part C 的 G×E 引擎（engine.gxe_model）替换简化公式。

引擎入口：
  simulate_health_trajectory(genetic_profile, environment)
  → {baseline_hti, trajectory, dimension_scores, factor_analysis, summary}

科学增强：
  - 个性化遗传基线（从用户真实基因档案构建，替代固定 72）
  - 基因 × 早期成长环境交互效应（HTI = 基因 + 环境 + 交互）
  - 置信区间（不确定性量化）
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter

from backend.schemas import ApiResponse, SimulateRequest

router = APIRouter(prefix="/api", tags=["simulate"])

# 优化后的理想婴儿成长因素
OPTIMIZED_FACTORS = {
    "nutrition_type": 8,
    "sleep_quality": 9,
    "development_stimulation": 8,
    "medical_adherence": 10,
    "environmental_safety": 9,
}

# 婴儿成长环境因素默认值
DEFAULT_ENV = {
    "nutrition_type": 7,
    "sleep_quality": 7,
    "development_stimulation": 6,
    "medical_adherence": 9,
    "environmental_safety": 8,
}


def _environment_from_factors(factors: dict) -> dict[str, float]:
    """将前端 factors 映射到引擎 environment 格式。"""
    return {
        "nutrition_type": float(factors.get("nutrition_type", DEFAULT_ENV["nutrition_type"])),
        "sleep_quality": float(factors.get("sleep_quality", DEFAULT_ENV["sleep_quality"])),
        "development_stimulation": float(factors.get("development_stimulation", DEFAULT_ENV["development_stimulation"])),
        "medical_adherence": float(factors.get("medical_adherence", DEFAULT_ENV["medical_adherence"])),
        "environmental_safety": float(factors.get("environmental_safety", DEFAULT_ENV["environmental_safety"])),
    }


def _load_genetic_profile(report_id: str | None = None) -> dict[str, float]:
    """从用户上传的真实基因报告构建遗传基线。

    Args:
        report_id: 可选，指定报告 ID。未传时使用最近完成的报告。
    """
    try:
        from backend.database import SessionLocal
        from backend.models import GeneticReport, GeneticVariant
        from sqlalchemy import select, desc
        import asyncio

        async def _query():
            async with SessionLocal() as session:
                if report_id:
                    report = await session.get(GeneticReport, report_id)
                    if not report or report.parsing_status != "completed":
                        # 指定报告不存在或未完成，回退到最新完成报告
                        result = await session.execute(
                            select(GeneticReport)
                            .where(GeneticReport.parsing_status == "completed")
                            .order_by(desc(GeneticReport.created_at))
                            .limit(1)
                        )
                        report = result.scalars().first()
                else:
                    result = await session.execute(
                        select(GeneticReport)
                        .where(GeneticReport.parsing_status == "completed")
                        .order_by(desc(GeneticReport.created_at))
                        .limit(1)
                    )
                    report = result.scalars().first()
                if not report:
                    return []
                result = await session.execute(
                    select(GeneticVariant).where(GeneticVariant.report_id == report.id)
                )
                variants = result.scalars().all()
                return [
                    {
                        "gene_name": v.gene_name,
                        "clinvar_significance": v.clinvar_significance,
                        "risk_score": v.risk_score,
                    }
                    for v in variants
                ]

        variants = asyncio.run(_query())
        if not variants:
            return _default_profile()

        profile: dict[str, float] = {}
        for v in variants:
            gene = v.get("gene_name")
            if not gene:
                continue
            sig = (v.get("clinvar_significance") or "").lower()
            if "pathogenic" in sig:
                sens = 0.8
            elif "uncertain" in sig:
                sens = 0.5
            elif "benign" in sig:
                sens = 0.2
            else:
                sens = 0.3 + min(v.get("risk_score") or 0.3, 0.5)
            profile[gene] = round(min(sens, 1.0), 2)

        return profile if profile else _default_profile()
    except Exception as e:
        print(f"[simulate] 遗传基线加载失败（用默认）: {e}")
        return _default_profile()


def _default_profile() -> dict[str, float]:
    """默认基因 sensitivity — 儿科核心基因（无用户数据时）。"""
    return {
        "PAH": 0.4, "G6PD": 0.3, "CYP21A2": 0.4,
        "SMN1": 0.5, "GJB2": 0.35, "SLC26A4": 0.3,
        "CHD7": 0.35, "IL2RG": 0.5, "CFTR": 0.35,
        "HBB": 0.4, "SCN1A": 0.4, "FMR1": 0.4,
    }


def _run_gxe(genetic: dict[str, float], env: dict[str, float], optimized_env: dict[str, float] | None = None) -> dict | None:
    """调用 G×E 引擎，失败时返回 None。

    Args:
        genetic: 基因灵敏度档案
        env: 当前环境
        optimized_env: 优化环境。传入时 trendData.optimized 使用优化环境的真实轨迹，
                       否则 optimized 与 current 相同。
    """
    try:
        from engine.gxe_model import simulate_health_trajectory
        from engine.recommendation_engine import generate_from_simulation

        sim = simulate_health_trajectory(genetic, env)
        recs = generate_from_simulation(sim, genetic, env)

        opt_sim = None
        if optimized_env:
            opt_sim = simulate_health_trajectory(genetic, optimized_env)

        risk_dimensions = [
            {
                "key": dim["key"],
                "label": dim["label"],
                "score": dim["score"],
                "baseline": 50,
                "gene_contribution": dim.get("gene_contribution"),
                "environment_contribution": dim.get("environment_contribution"),
                "interaction_contribution": dim.get("interaction_contribution"),
            }
            for dim in sim["dimension_scores"].values()
        ]

        trend_data = [
            {
                "year": t["year"],
                "current": t["hti"],
                "optimized": opt_sim["trajectory"][i]["hti"] if opt_sim else t["hti"],
                "confidence": t.get("confidence"),
            }
            for i, t in enumerate(sim["trajectory"])
        ]

        recommendations = [
            {
                "id": r["title"].replace(" ", "_").lower()[:20],
                "pillar": r.get("pillar", "general"),
                "icon": r.get("icon", "🎯"),
                "title": r["title"],
                "description": r["description"],
                "why_for_this_user": r.get("why_for_this_user", ""),
                "related_gene": r.get("related_gene", []),
                "trigger_factor": r.get("trigger_factor", ""),
                "evidence_level": r.get("evidence_level", "moderate"),
                "confidence": r.get("confidence", {}),
                "difficulty": r.get("difficulty", "moderate"),
                "impact": r.get("impact", 3),
                "time": r.get("time", ""),
            }
            for r in recs[:6]
        ]

        return {
            "healthScore": sim["baseline_hti"],
            "optimizedScore": opt_sim["baseline_hti"] if opt_sim else sim["baseline_hti"],
            "riskDimensions": risk_dimensions,
            "trendData": trend_data,
            "recommendations": recommendations,
            "gene_effect": sim["summary"].get("gene_effect"),
            "environment_effect": sim["summary"].get("environment_effect"),
            "interaction_effect": sim["summary"].get("interaction_effect"),
            "source": "gxe_engine",
        }
    except Exception as e:
        print(f"[simulate] G×E 引擎失败: {e}")
        return None


@router.post("/simulate", response_model=ApiResponse)
def simulate(req: SimulateRequest):
    """运行 G×E 健康模拟，返回健康评分与风险维度。"""
    factors = req.factors or {}
    genetic = _load_genetic_profile(req.report_id)
    env = _environment_from_factors(factors)
    optimized_env = _environment_from_factors(OPTIMIZED_FACTORS)

    result = _run_gxe(genetic, env, optimized_env)
    if result:
        return ApiResponse.ok(result)

    # 降级：prs_calculator 简化公式
    from backend.services import prs_calculator as fallback

    health_score = fallback.calculate_health_score(factors)
    optimized_score = fallback.calculate_health_score(OPTIMIZED_FACTORS)
    risk_dimensions = fallback.calculate_dimension_scores_with_factors([], factors)
    trend_data = fallback.generate_trend_data([], factors)
    recommendations = fallback.generate_recommendations(factors)

    return ApiResponse.ok({
        "healthScore": health_score,
        "optimizedScore": optimized_score,
        "riskDimensions": risk_dimensions,
        "trendData": trend_data,
        "recommendations": recommendations,
        "source": "fallback",
    })
