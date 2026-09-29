"""
Pytest Fixtures for TPG Backend Test Suite
"""

import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.api.deps import get_workspace_id
from app.main import app
from app.models.workspace import Workspace
from app.models.entity import Entity, EntityRelationship, EntityType, RelationshipType, ConfidenceLevel, EntityStatus


TEST_WORKSPACE_ID = "ws-test-12345"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """In-memory SQLite async engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yields an active database session for a test."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        # Pre-seed a test workspace
        ws = Workspace(
            id=TEST_WORKSPACE_ID,
            owner_email="founder@skynetorg.com",
            owner_name="Founder",
            name="Test Product Office",
        )
        session.add(ws)
        await session.commit()

        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI AsyncClient configured with test DB and mocked workspace header."""
    async def override_get_db():
        yield test_session

    async def override_get_workspace_id():
        return TEST_WORKSPACE_ID

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_workspace_id] = override_get_workspace_id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
