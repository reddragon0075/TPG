"""
API Dependencies

Shared dependencies injected into API route handlers.
"""

from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.workspace import Workspace


settings = get_settings()


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    """
    Verify the API key sent by ChatGPT Actions.

    In V1, this is a simple shared secret. Future versions
    may use JWT or OAuth for richer authentication.
    """
    if not settings.api_key:
        # No API key configured — development mode
        return "dev"

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
    return x_api_key


async def get_workspace_id(
    x_workspace_id: str = Header(
        default=None,
        alias="X-Workspace-ID",
    ),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Resolve the current workspace.

    V1: Single-user system. If no workspace exists, create one.
    Future: Resolve from authenticated user token.
    """
    if x_workspace_id:
        # Verify workspace exists
        stmt = select(Workspace).where(Workspace.id == x_workspace_id)
        result = await db.execute(stmt)
        workspace = result.scalar_one_or_none()
        if workspace:
            return workspace.id

    # V1: Auto-create default workspace if none exists
    stmt = select(Workspace).limit(1)
    result = await db.execute(stmt)
    workspace = result.scalar_one_or_none()

    if workspace:
        return workspace.id

    # First run — create the default Personal Workspace
    workspace = Workspace(
        owner_email="owner@tpg.local",
        owner_name="Product Owner",
        name="My Product Office",
        description="TPG V1 Personal Workspace",
    )
    db.add(workspace)
    await db.flush()

    return workspace.id
