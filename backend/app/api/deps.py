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
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> str:
    """
    Verify the API key sent by ChatGPT Actions.

    Supports X-API-Key header, Authorization: Bearer token,
    or development fallback if debug=True.
    """
    token = x_api_key
    if not token and authorization:
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()

    if not settings.api_key:
        return "dev"

    if token == settings.api_key:
        return token

    if settings.debug and not token:
        return "dev"

    raise HTTPException(
        status_code=401,
        detail="Invalid API key",
    )


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
