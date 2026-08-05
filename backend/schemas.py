"""
Pydantic 请求/响应模型 — 对齐 GenoLife AI 新前端
===================================================
数据契约来源：genolife-ai/src/data/mockData.js

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


# ============ 用户档案（mockData.userProfile）============

class UserProfile(BaseModel):
    """用户档案概览。"""

    name: str = "用户"
    healthScore: int = Field(0, ge=0, le=100)
    geneticAge: int = Field(0, ge=0)
    chronologicalAge: int = Field(0, ge=0)


# ============ 健康概览（mockData.healthSummary）============

class HealthSummary(BaseModel):
    """健康概览摘要。"""

    score: int = Field(0, ge=0, le=100)
    level: str = "moderate"  # low / moderate / high
    levelLabel: str = ""
    aiSummary: str = ""


# ============ 基因卡片（mockData.geneCards[]）============

class GeneCard(BaseModel):
    """单张基因卡片。"""

    id: str
    symbol: str  # 基因符号，如 APOE
    name: str  # 展示名，如 Cognitive Health
    category: str  # 类别，如 Brain & Longevity
    riskLevel: str  # low / moderate / elevated / advantage
    summary: str = ""
    interpretation: str = ""
    recommendations: list[str] = Field(default_factory=list)
    icon: str = "🧬"
    # 真实分析附加字段（前端可选）
    clinvar_significance: str | None = None
    odds_ratio: float | None = None
    genotype: str | None = None


# ============ 风险维度（mockData.riskDimensions[]）============

class RiskDimension(BaseModel):
    """单维度风险评分。"""

    key: str  # metabolic / cognitive / cardiovascular / athletic / sleep
    label: str  # Metabolic / Cognitive / ...
    score: int = Field(0, ge=0, le=100)
    baseline: int = Field(50, ge=0, le=100)


# ============ 基因档案（GET /api/profile 返回）============

class GeneticProfile(BaseModel):
    """完整基因分析档案。"""

    user: UserProfile
    summary: HealthSummary
    geneCards: list[GeneCard] = Field(default_factory=list)
    riskDimensions: list[RiskDimension] = Field(default_factory=list)


# ============ 模拟（mockData.simulation*）============

class SimulationFactor(BaseModel):
    """模拟因子定义。"""

    key: str  # sleep / exercise / diet / stress
    label: str
    icon: str
    min: float
    max: float
    step: float
    unit: str
    description: str = ""


class SimulateRequest(BaseModel):
    """POST /api/simulate 请求体。"""

    factors: dict[str, float] = Field(
        default_factory=dict,
        description="生活因素：nutrition_type/sleep_quality/development_stimulation/medical_adherence/environmental_safety",
    )
    report_id: str | None = Field(
        None,
        description="可选，指定报告 ID。未传时使用数据库中最近完成的报告。",
    )


class TrendPoint(BaseModel):
    """趋势数据点。"""

    year: int
    current: int
    optimized: int


class SimulationResult(BaseModel):
    """POST /api/simulate 返回（对齐 mockData 计算函数输出）。"""

    healthScore: int = Field(0, ge=0, le=100)
    riskDimensions: list[RiskDimension] = Field(default_factory=list)
    trendData: list[TrendPoint] = Field(default_factory=list)
    recommendations: list["RecommendationOut"] = Field(default_factory=list)
    optimizedScore: int = Field(0, ge=0, le=100)


# ============ 建议（mockData.generateRecommendations 输出）============

class RecommendationOut(BaseModel):
    """单条个性化建议。"""

    id: str
    pillar: str  # sleep / exercise / diet / stress / general
    icon: str = "🎯"
    title: str
    description: str
    difficulty: str = "moderate"  # easy / moderate / hard
    impact: int = Field(1, ge=1, le=5)
    time: str = ""


class RecommendationList(BaseModel):
    """GET /api/recommendations 返回。"""

    recommendations: list[RecommendationOut] = Field(default_factory=list)


# ============ 30 天计划（mockData.thirtyDayPlan）============

class TaskItem(BaseModel):
    """计划任务。"""

    day: str
    title: str
    desc: str


class WeekPlan(BaseModel):
    """每周计划。"""

    label: str
    theme: str
    tasks: list[TaskItem] = Field(default_factory=list)


class ThirtyDayPlan(BaseModel):
    """30 天健康计划。"""

    goal: str
    weeks: list[WeekPlan] = Field(default_factory=list)
