"""
GET /api/recommendations — 个性化建议
======================================
返回建议列表与 30 天计划（对齐前端 mockData 结构）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, Query

from backend.schemas import ApiResponse
from backend.services import prs_calculator as engine

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.get("/recommendations", response_model=ApiResponse)
def get_recommendations(
    sleep: float = Query(6, ge=3, le=10, description="睡眠时长（小时）"),
    exercise: float = Query(3, ge=0, le=7, description="每周运动天数"),
    diet: float = Query(5, ge=1, le=10, description="饮食质量评分"),
    stress: float = Query(6, ge=1, le=10, description="压力水平"),
    include_plan: bool = Query(True, description="是否包含 30 天计划"),
):
    """获取个性化生活方式建议。"""
    factors = {"sleep": sleep, "exercise": exercise, "diet": diet, "stress": stress}
    recommendations = engine.generate_recommendations(factors)

    result: dict = {"recommendations": recommendations}
    if include_plan:
        result["thirtyDayPlan"] = engine.generate_thirty_day_plan()

    return ApiResponse.ok(result)
