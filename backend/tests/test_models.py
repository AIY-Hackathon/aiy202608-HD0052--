"""
数据库模型单元测试 — A1.2
==========================
验证 5 张表的创建、字段完整性与基本 CRUD 操作。

运行方式（在项目根目录）：
    pytest backend/tests/test_models.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

# 测试用独立 SQLite 数据库（避免污染开发库）
TEST_DB = "sqlite+aiosqlite:///./test_gene_assistant.db"
os.environ["DATABASE_URL"] = TEST_DB

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import inspect, select  # noqa: E402

from backend import models  # noqa: E402
from backend.database import SessionLocal, engine, init_db  # noqa: E402


@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试前重建表结构。"""
    import backend.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_all_tables_created():
    """5 张表都应存在。"""
    def _inspect(sync_conn):
        return inspect(sync_conn).get_table_names()

    async with engine.connect() as conn:
        tables = await conn.run_sync(_inspect)

    expected = {
        "users",
        "genetic_reports",
        "genetic_variants",
        "simulation_scenarios",
        "recommendations",
    }
    assert expected.issubset(set(tables)), f"缺少表: {expected - set(tables)}"


@pytest.mark.asyncio
async def test_user_report_variant_cascade():
    """用户 → 报告 → 变异 的关联创建与级联删除。"""
    async with SessionLocal() as session:
        user = models.User(anonymized_id="t_user_001")
        session.add(user)
        await session.flush()

        report = models.GeneticReport(
            user_id=user.id,
            original_filename="test.vcf",
            file_format="vcf",
            parsing_status="completed",
        )
        session.add(report)
        await session.flush()

        variant = models.GeneticVariant(
            report_id=report.id,
            chromosome="7",
            position=117149150,
            reference="CTT",
            alternative="C",
            rs_id="rs113993960",
            gene_name="CFTR",
            clinvar_significance="Pathogenic",
            odds_ratio=3.52,
            risk_score=0.87,
        )
        session.add(variant)
        await session.commit()

        # 关联查询
        result = await session.execute(
            select(models.GeneticVariant).where(
                models.GeneticVariant.report_id == report.id
            )
        )
        variants = result.scalars().all()
        assert len(variants) == 1
        assert variants[0].gene_name == "CFTR"
        assert variants[0].clinvar_significance == "Pathogenic"

        # 级联删除：删报告应删变异
        await session.delete(report)
        await session.commit()

        result = await session.execute(
            select(models.GeneticVariant).where(
                models.GeneticVariant.report_id == report.id
            )
        )
        assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_simulation_scenario_json_storage():
    """模拟场景的 JSON 字段应能存取复杂结构。"""
    async with SessionLocal() as session:
        scenario = models.SimulationScenario(
            name="基线场景",
            environmental_factors={"exercise_freq": 3, "bmi": 24.5, "smoking": 0},
            simulation_results={
                "health_trajectory": [{"year": 0, "risk": 0.08}],
                "confidence_intervals": {"upper": [0.08]},
            },
        )
        session.add(scenario)
        await session.commit()

        loaded = await session.get(models.SimulationScenario, scenario.id)
        assert loaded.name == "基线场景"
        assert loaded.environmental_factors["bmi"] == 24.5
        assert loaded.simulation_results["health_trajectory"][0]["year"] == 0


@pytest.mark.asyncio
async def test_recommendation_creation():
    """建议表基本写入与字段完整性。"""
    async with SessionLocal() as session:
        rec = models.Recommendation(
            recommendation_type="exercise",
            title="每周 150 分钟有氧运动",
            description="基于心血管风险评分 1.8 的建议",
            evidence_level="strong",
            evidence_links=["https://pubmed.ncbi.nlm.nih.gov/12345"],
            priority_score=85,
            difficulty_level="easy",
        )
        session.add(rec)
        await session.commit()

        loaded = await session.get(models.Recommendation, rec.id)
        assert loaded.title.startswith("每周")
        assert loaded.priority_score == 85
        assert loaded.status == "pending"  # 默认值
