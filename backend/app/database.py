"""
TPG Database Engine & Session Management

Provides async SQLAlchemy engine and session factory.
All database access flows through this module.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


settings = get_settings()

engine_kwargs = {
    "echo": settings.database_echo,
}

if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

def _init_engine():
    try:
        return create_async_engine(
            settings.database_url,
            **engine_kwargs,
        )
    except Exception:
        # Fallback to async sqlite for local development/testing if postgres driver is unavailable
        return create_async_engine(
            "sqlite+aiosqlite:///./tpg_dev.db",
            echo=settings.database_echo,
        )

engine = _init_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
