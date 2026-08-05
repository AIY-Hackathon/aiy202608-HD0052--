"""
API 端点单元测试 — A2
=======================
验证三个端点的数据结构对齐前端 mockData。

运行方式：
    pytest backend/tests/test_api.py -v
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient

from backend.api.profile import build_profile
from backend.main import app

client = TestClient(app)


# ============ 基础 ============

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ============ GET /api/profile ============

def test_profile_success():
    r = client.get("/api/profile")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]

    # 顶层结构
    assert "user" in data
    assert "summary" in data
    assert "geneCards" in data
    assert "riskDimensions" in data

    # user（对齐 mockData.userProfile）
    user = data["user"]
    assert set(user.keys()) == {"name", "healthScore", "geneticAge", "chronologicalAge"}
    assert 0 <= user["healthScore"] <= 100

    # summary（对齐 mockData.healthSummary）
    summary = data["summary"]
    assert set(summary.keys()) == {"score", "level", "levelLabel", "aiSummary"}
    assert summary["level"] in {"low", "moderate", "high"}

    # geneCards（对齐 mockData.geneCards[]）
    cards = data["geneCards"]
    assert 1 <= len(cards) <= 4
    for c in cards:
        assert "id" in c and "symbol" in c and "name" in c
        assert "category" in c and "riskLevel" in c
        assert "summary" in c and "interpretation" in c
        assert "recommendations" in c and "icon" in c

    # riskDimensions（对齐 mockData.riskDimensions[]）
    dims = data["riskDimensions"]
    assert len(dims) == 5
    keys = {d["key"] for d in dims}
    assert keys == {"metabolic", "cognitive", "cardiovascular", "athletic", "sleep"}
    for d in dims:
        assert 5 <= d["score"] <= 95
        assert d["baseline"] == 50


# ============ POST /api/simulate ============

def test_simulate_default():
    r = client.post("/api/simulate", json={"factors": {}})
    assert r.status_code == 200
    data = r.json()["data"]

    assert "healthScore" in data
    assert "optimizedScore" in data
    assert "riskDimensions" in data
    assert "trendData" in data
    assert "recommendations" in data

    # G×E 引擎返回 0-100 的 HTI（教育模拟指标，非疾病风险）
    assert 0 <= data["healthScore"] <= 100
    assert 0 <= data["optimizedScore"] <= 100
    # 优化生活方式应提高健康评分
    assert data["optimizedScore"] > data["healthScore"]


def test_simulate_poor_lifestyle():
    """不良生活方式应降低健康分。"""
    r = client.post("/api/simulate", json={"factors": {"sleep": 3, "exercise": 0, "diet": 1, "stress": 10}})
    data = r.json()["data"]
    assert data["healthScore"] < 60


def test_simulate_optimized_lifestyle():
    """优化生活方式应提高健康分。"""
    r = client.post("/api/simulate", json={"factors": {"sleep": 9, "exercise": 7, "diet": 9, "stress": 1}})
    data = r.json()["data"]
    assert data["healthScore"] > 80


def test_simulate_trend_structure():
    r = client.post("/api/simulate", json={"factors": {"sleep": 6, "exercise": 3}})
    data = r.json()["data"]
    trend = data["trendData"]
    # G×E 引擎默认时间点 [5, 10, 20]
    assert len(trend) == 3
    years = [t["year"] for t in trend]
    assert years == [5, 10, 20]
    for t in trend:
        assert "year" in t and "current" in t and "optimized" in t
        assert 0 <= t["current"] <= 100
        assert 0 <= t["optimized"] <= 100
    # 优化轨迹应优于当前轨迹（生活方式改变带来改善）
    assert all(t["optimized"] >= t["current"] for t in trend)


def test_simulate_recommendations_structure():
    r = client.post("/api/simulate", json={"factors": {"sleep": 5, "exercise": 2, "diet": 3, "stress": 8}})
    recs = r.json()["data"]["recommendations"]
    assert len(recs) >= 3
    for rec in recs:
        assert "id" in rec and "pillar" in rec and "icon" in rec
        assert "title" in rec and "description" in rec
        assert "difficulty" in rec and "impact" in rec and "time" in rec


# ============ GET /api/recommendations ============

def test_recommendations_query():
    r = client.get("/api/recommendations", params={"sleep": 5, "exercise": 2, "diet": 3, "stress": 8})
    assert r.status_code == 200
    data = r.json()["data"]
    assert "recommendations" in data
    assert "thirtyDayPlan" in data
    assert len(data["recommendations"]) >= 3


def test_recommendations_optimized():
    """优化生活 → 建议少。"""
    r = client.get("/api/recommendations", params={"sleep": 8, "exercise": 5, "diet": 8, "stress": 3})
    data = r.json()["data"]
    assert len(data["recommendations"]) <= 2


def test_recommendations_thirty_day_plan():
    r = client.get("/api/recommendations")
    plan = r.json()["data"]["thirtyDayPlan"]
    assert "goal" in plan
    assert len(plan["weeks"]) == 4
    for week in plan["weeks"]:
        assert "label" in week and "theme" in week and "tasks" in week
        assert len(week["tasks"]) == 3


# ============ build_profile（真实数据路径）============

def test_build_profile_with_variants():
    """真实变异应影响维度分与卡片等级。"""
    variants = [
        {"gene_name": "APOE", "clinvar_significance": "Pathogenic", "odds_ratio": 3.0},
        {"gene_name": "FTO", "clinvar_significance": "Benign", "odds_ratio": 1.0},
    ]
    profile = build_profile(variants)

    # APOE 卡片应 elevated
    apoe = next(c for c in profile["geneCards"] if c["symbol"] == "APOE")
    assert apoe["riskLevel"] == "elevated"

    # cognitive 维度应升高
    cognitive = next(d for d in profile["riskDimensions"] if d["key"] == "cognitive")
    assert cognitive["score"] > 50


def test_build_profile_no_variants():
    """无变异时应返回默认演示档案。"""
    profile = build_profile([])
    assert len(profile["geneCards"]) <= 4
    assert all(d["score"] == 50 for d in profile["riskDimensions"])
