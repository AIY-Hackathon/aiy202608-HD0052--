"""
POST /api/simulate — 生活方式模拟
===================================
接收生活因素，返回健康评分、风险维度、趋势、建议。
对齐前端 LifeSimulation 页面的数据需求。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter

from backend.schemas import ApiResponse, SimulateRequest
from backend.services import prs_calculator as engine

router = APIRouter(prefix="/api", tags=["simulate"])

# 优化后的理想生活因素
OPTIMIZED_FACTORS = {"sleep": 8, "exercise": 5, "diet": 8, "stress": 3}


@router.post("/simulate", response_model=ApiResponse)
def simulate(req: SimulateRequest):
    """运行生活方式模拟，返回健康评分与风险维度。"""
    factors = req.factors or {}

    # 1. 健康评分（当前）
    health_score = engine.calculate_health_score(factors)

    # 2. 优化后健康评分
    optimized_score = engine.calculate_health_score(OPTIMIZED_FACTORS)

    # 3. 风险维度（当前）
    risk_dimensions = engine.calculate_dimension_scores_with_factors([], factors)

    # 4. 趋势数据
    trend_data = engine.generate_trend_data([], factors)

    # 5. 建议
    recommendations = engine.generate_recommendations(factors)

    return ApiResponse.ok({
        "healthScore": health_score,
        "optimizedScore": optimized_score,
        "riskDimensions": risk_dimensions,
        "trendData": trend_data,
        "recommendations": recommendations,
    })
