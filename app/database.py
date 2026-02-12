"""
Async SQLAlchemy setup and dependency injection for DB session.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

_settings = get_settings()


def _ensure_asyncpg_url(url: str) -> str:
    """Convert PostgreSQL URL to async driver (asyncpg) for create_async_engine."""
    if "+asyncpg" in url:
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if "postgresql+psycopg" in url or "postgresql+psycopg2" in url:
        return (
            url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1).replace(
                "postgresql+psycopg://", "postgresql+asyncpg://", 1
            )
        )
    return url


engine = create_async_engine(
    _ensure_asyncpg_url(_settings.database_url),
    pool_pre_ping=True,
    echo=_settings.environment == "development",
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
