"""
GenoLife AI — FastAPI 后端入口
================================
真实基因分析 API，对齐 genolife-ai React 前端。

端点：
  GET   /api/health              → 健康检查
  GET   /api/profile             → 基因分析档案（概览 + 基因卡片 + 风险维度）
  POST  /api/upload              → 上传 VCF 基因报告
  GET   /api/analysis/{id}       → 分析结果（变异 + 风险 + 档案）
  POST  /api/simulate            → 生活方式模拟
  GET   /api/recommendations     → 个性化建议 + 30 天计划

启动：
  uvicorn backend.main:app --reload
文档：
  http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import analysis, profile, recommendations, simulate, upload
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化数据库表。"""
    await init_db()
    yield


app = FastAPI(
    title="GenoLife AI API",
    description="真实基因分析后端 — 对齐 React 前端",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(profile.router)
app.include_router(simulate.router)
app.include_router(recommendations.router)
app.include_router(upload.router)
app.include_router(analysis.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "genolife-backend", "version": "0.2.0"}
