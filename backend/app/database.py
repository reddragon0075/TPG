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

from pathlib import Path

def _resolve_db_url(url: str) -> str:
    if url.startswith("sqlite+aiosqlite:///./"):
        backend_dir = Path(__file__).resolve().parent.parent
        db_filename = url[len("sqlite+aiosqlite:///./"):]
        abs_db_path = (backend_dir / db_filename).resolve().as_posix()
        return f"sqlite+aiosqlite:///{abs_db_path}"
    return url

def _init_engine():
    resolved_url = _resolve_db_url(settings.database_url)
    try:
        return create_async_engine(
            resolved_url,
            **engine_kwargs,
        )
    except Exception:
        fallback_path = (Path(__file__).resolve().parent.parent / "tpg_dev.db").resolve().as_posix()
        return create_async_engine(
            f"sqlite+aiosqlite:///{fallback_path}",
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


async def ensure_db_schema():
    """Creates tables if missing and adds missing commercial columns for dev/SQLite."""
    from sqlalchemy import inspect, text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def _migrate(sync_conn):
            inspector = inspect(sync_conn)
            if "workspaces" in inspector.get_table_names():
                existing = {c["name"] for c in inspector.get_columns("workspaces")}
                columns_to_add = [
                    ("subscription_tier", "VARCHAR(50) DEFAULT 'pro'"),
                    ("subscription_status", "VARCHAR(50) DEFAULT 'active'"),
                    ("license_key", "VARCHAR(100)"),
                    ("valid_until", "TIMESTAMP"),
                    ("trial_ends_at", "TIMESTAMP"),
                    ("stripe_customer_id", "VARCHAR(100)"),
                    ("stripe_subscription_id", "VARCHAR(100)"),
                    ("entities_limit", "INTEGER DEFAULT 5000"),
                    ("connectors_limit", "INTEGER DEFAULT 10"),
                ]
                for col_name, col_type in columns_to_add:
                    if col_name not in existing:
                        try:
                            sync_conn.execute(text(f"ALTER TABLE workspaces ADD COLUMN {col_name} {col_type}"))
                        except Exception:
                            pass

        await conn.run_sync(_migrate)

