"""
数据库 ORM 模型 — 基因分析助手
================================
5 张核心表：
  1. users                  — 用户（匿名化）
  2. genetic_reports        — 基因报告（上传记录）
  3. genetic_variants       — 基因变异（报告解析结果）
  4. simulation_scenarios   — 健康模拟场景
  5. recommendations        — 个性化建议

字段对齐前端 mock_data.py 的数据结构，
见 docs/requirements.md R1 / R3 / R4 与 docs/design.md §5。
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    """生成短 UUID 作为主键（可读性更好）。"""
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """用户表 — 匿名化存储，符合数据隐私要求（R5）。"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_uuid)
    # 匿名化标识符，与真实身份分离
    anonymized_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    consent_status: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # 关联
    reports: Mapped[list["GeneticReport"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class GeneticReport(Base):
    """基因报告表 — 一次文件上传对应一条记录。"""

    __tablename__ = "genetic_reports"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    original_filename: Mapped[str] = mapped_column(String(255))
    file_format: Mapped[str] = mapped_column(String(20))  # vcf / tsv
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    # pending → processing → completed / failed
    parsing_status: Mapped[str] = mapped_column(String(20), default="pending")
    variant_count: Mapped[int] = mapped_column(Integer, default=0)
    validation_errors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 关联
    user: Mapped["User"] = relationship(back_populates="reports")
    variants: Mapped[list["GeneticVariant"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class GeneticVariant(Base):
    """基因变异表 — 从 VCF 解析出的每一条变异。

    字段对齐前端 MOCK_ANALYSIS_RESULT["variants"][0] 的结构。
    """

    __tablename__ = "genetic_variants"
    __table_args__ = (
        Index("idx_variant_location", "chromosome", "position"),
        Index("idx_variant_rsid", "rs_id"),
    )

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_uuid)
    report_id: Mapped[str] = mapped_column(
        ForeignKey("genetic_reports.id", ondelete="CASCADE")
    )

    # === VCF 核心字段 ===
    chromosome: Mapped[str] = mapped_column(String(5))  # "1".."22","X","Y","MT"
    position: Mapped[int] = mapped_column(Integer)
    reference: Mapped[str] = mapped_column(Text)
    alternative: Mapped[str] = mapped_column(Text)
    rs_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # === ClinVar 注释 ===
    gene_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    clinvar_significance: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Pathogenic / Benign / VUS ...
    clinvar_review_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # reviewed_by_expert_panel ...

    # === 风险计算 ===
    odds_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    population_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # PRS 权重贡献

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # 关联
    report: Mapped["GeneticReport"] = relationship(back_populates="variants")


class SimulationScenario(Base):
    """健康模拟场景表 — 一次模拟运行的结果。"""

    __tablename__ = "simulation_scenarios"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    report_id: Mapped[str | None] = mapped_column(
        ForeignKey("genetic_reports.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), default="未命名场景")

    # 环境因素输入（前端 slider 传参）
    # {"exercise_freq": 3, "bmi": 24.5, "smoking": 0, "alcohol": 2, "diet_quality": 4}
    environmental_factors: Mapped[dict] = mapped_column(JSON, default=dict)

    # 模拟结果（JSON 存储，避免过度规范化）
    # {"health_trajectory": [...], "confidence_intervals": {...}}
    simulation_results: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Recommendation(Base):
    """个性化建议表 — 建议引擎输出。"""

    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    report_id: Mapped[str | None] = mapped_column(
        ForeignKey("genetic_reports.id", ondelete="CASCADE"), nullable=True
    )

    recommendation_type: Mapped[str] = mapped_column(String(50))  # diet/exercise/screening...
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    evidence_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    evidence_links: Mapped[list | None] = mapped_column(JSON, nullable=True)
    priority_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    difficulty_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/accepted/completed/rejected

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
