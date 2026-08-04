"""
Pydantic 请求/响应模型 — API 数据契约
======================================
对齐前端 frontend/mock_data.py 与 api_client.py 的数据结构。

统一响应格式：
    {"success": bool, "data": {...} | None, "error": {...} | None}
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应包装。"""

    success: bool = True
    data: T | None = None
    error: dict | None = None

    @classmethod
    def ok(cls, data: Any = None) -> "ApiResponse":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str) -> "ApiResponse":
        return cls(success=False, data=None, error={"code": code, "message": message})


# ============ 变异 ============

class VariantOut(BaseModel):
    """分析结果中的单条变异。"""

    id: str
    chromosome: str
    position: int
    reference: str
    alternative: str
    rs_id: str | None = None
    gene_name: str | None = None
    clinvar_significance: str | None = None
    clinvar_review_status: str | None = None
    odds_ratio: float | None = None
    population_frequency: float | None = None
    quality_score: float | None = None
    risk_score: float | None = None


class AnalysisResult(BaseModel):
    """GET /api/analysis/{report_id} 返回。"""

    report_id: str
    variants: list[VariantOut]
    risk_scores: dict[str, float] = Field(default_factory=dict)
    overall_risk_level: str = "low"  # low / moderate / high
    confidence_intervals: dict[str, list[float]] = Field(default_factory=dict)
    quality_score: float = 0.0


# ============ 上传 ============

class UploadResult(BaseModel):
    """POST /api/upload 返回。"""

    report_id: str
    variant_count: int = 0
    status: str = "completed"
    original_filename: str
    created_at: str


# ============ 模拟 ============

class SimulationRequest(BaseModel):
    """POST /api/simulate 请求体。"""

    report_id: str
    environmental_factors: dict[str, float] = Field(
        default_factory=dict,
        description="环境因素：exercise_freq/bmi/smoking/alcohol/diet_quality",
    )


class SimulationResult(BaseModel):
    """POST /api/simulate 返回。"""

    scenario_id: str
    health_trajectory: list[dict] = Field(default_factory=list)
    confidence_intervals: dict[str, list[float]] = Field(default_factory=dict)


# ============ 建议 ============

class RecommendationRequest(BaseModel):
    """POST /api/recommendations 请求体。"""

    report_id: str
    preferences: dict | None = None


class RecommendationOut(BaseModel):
    """单条建议。"""

    id: str
    recommendation_type: str
    title: str
    description: str
    evidence_level: str | None = None
    evidence_links: list[str] = Field(default_factory=list)
    priority_score: int | None = None
    difficulty_level: str | None = None
    status: str = "pending"


class RecommendationList(BaseModel):
    """POST /api/recommendations 返回。"""

    recommendations: list[RecommendationOut] = Field(default_factory=list)


# ============ 报告导出 ============

class ExportQuery(BaseModel):
    """GET /api/report/{report_id}/export 查询参数。"""

    format: str = "html"  # pdf / html
