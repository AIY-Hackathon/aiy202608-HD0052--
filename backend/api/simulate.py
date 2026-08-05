"""
POST /api/simulate — 生活方式模拟
===================================
使用 Part C 的 G×E 引擎（engine.gxe_model）替换简化公式。

引擎入口：
  simulate_health_trajectory(genetic_profile, environment)
  → {baseline_hti, trajectory, dimension_scores, factor_analysis, summary}

科学增强：
  - 个性化遗传基线（从用户真实基因档案构建，替代固定 72）
  - 基因 × 环境交互效应（HTI = 基因 + 环境 + 交互）
  - 置信区间（不确定性量化）
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter

from backend.schemas import ApiResponse, SimulateRequest

router = APIRouter(prefix="/api", tags=["simulate"])

# 优化后的理想生活因素
OPTIMIZED_FACTORS = {"exercise": 8, "sleep": 8, "diet": 8, "stress": 2, "smoking": 0}

# 环境因素默认值
DEFAULT_ENV = {"exercise": 3, "sleep": 6, "diet": 5, "stress": 6, "smoking": 0}


def _environment_from_factors(factors: dict) -> dict[str, float]:
    """将前端 factors 映射到引擎 environment 格式。"""
    return {
        "exercise": float(factors.get("exercise", DEFAULT_ENV["exercise"])),
        "sleep": float(factors.get("sleep", DEFAULT_ENV["sleep"])),
        "diet": float(factors.get("diet", DEFAULT_ENV["diet"])),
        "stress": float(factors.get("stress", DEFAULT_ENV["stress"])),
        "smoking": float(factors.get("smoking", 0)),
    }


def _load_genetic_profile() -> dict[str, float]:
    """从用户最近上传的真实基因报告构建遗传基线。"""
    try:
        from backend.database import SessionLocal
        from backend.models import GeneticReport, GeneticVariant
        from sqlalchemy import select, desc
        import asyncio

        async def _query():
            async with SessionLocal() as session:
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
    """默认基因 sensitivity（无用户数据时）。"""
    return {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}


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

        # 优化环境轨迹（若提供）：同一基因档案 + 优化环境
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
    genetic = _load_genetic_profile()
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
