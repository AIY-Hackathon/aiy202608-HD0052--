"""
数据库连接与会话管理
====================
使用 SQLAlchemy 2.0 async 风格。

默认使用 SQLite（零配置，本地开发即可运行）。
生产环境可切换为 PostgreSQL（设置 DATABASE_URL 环境变量）。
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 支持两种数据库 URL：
# - SQLite（默认，零配置）: sqlite+aiosqlite:///./gene_assistant.db
# - PostgreSQL: postgresql+asyncpg://user:pass@localhost:5432/gene_assistant
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./gene_assistant.db",
)

# 是否使用异步引擎（默认是）
ASYNC = DATABASE_URL.startswith(("sqlite+aiosqlite", "postgresql+asyncpg"))


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


if ASYNC:
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    """FastAPI 依赖注入：每个请求一个数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """创建所有表（开发阶段直接 create_all，后续可换 Alembic 迁移）。"""
    # 导入模型以注册到 Base.metadata
    import backend.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
