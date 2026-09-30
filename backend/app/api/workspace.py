"""
Workspace & RBAC Security API — PRD-0003, PRD-0001 §385-§416

Endpoints:
- GET /workspace/me: Current workspace profile and settings
- GET /workspace/stats: Aggregated memory, relationship, and connector counts
- GET /workspace/export: Full knowledge snapshot export for portability
- POST /workspace/reset: Purge all knowledge in workspace (reset)
- POST /workspace/rbac/check: Check role permission against resource matrix
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.services.workspace_service import (
    WorkspaceService,
    UserRole,
    ResourceType,
)
from app.schemas import (
    WorkspaceInfoResponse,
    WorkspaceStatsResponse,
    WorkspaceExportResponse,
    WorkspaceResetResponse,
    RBACCheckRequest,
    RBACCheckResponse,
)

router = APIRouter(prefix="/workspace", tags=["Workspace & Security"])


@router.get("/me", response_model=WorkspaceInfoResponse)
async def get_current_workspace(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves profile details for the current active workspace."""
    service = WorkspaceService(db=db, workspace_id=workspace_id)
    info = await service.get_workspace_info()
    if not info:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return WorkspaceInfoResponse(**info)


@router.get("/stats", response_model=WorkspaceStatsResponse)
async def get_workspace_statistics(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Returns aggregated entity counts and relationship totals."""
    service = WorkspaceService(db=db, workspace_id=workspace_id)
    stats = await service.get_aggregated_stats()
    return WorkspaceStatsResponse(**stats)


@router.get("/export", response_model=WorkspaceExportResponse)
async def export_workspace_snapshot(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Exports all entities and relationships as an offline JSON package."""
    service = WorkspaceService(db=db, workspace_id=workspace_id)
    snapshot = await service.export_workspace_snapshot()
    return WorkspaceExportResponse(**snapshot)


@router.post("/reset", response_model=WorkspaceResetResponse)
async def reset_workspace(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Wipes all knowledge entities and relationships in the workspace."""
    service = WorkspaceService(db=db, workspace_id=workspace_id)
    res = await service.reset_workspace_knowledge()
    return WorkspaceResetResponse(**res)


@router.post("/rbac/check", response_model=RBACCheckResponse)
async def check_rbac_permission(
    request: RBACCheckRequest,
):
    """
    Evaluates role permissions according to constitutional RBAC matrix (PRD-0001 §406).
    """
    try:
        role = UserRole(request.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Supported roles: {[e.value for e in UserRole]}",
        )

    try:
        resource = ResourceType(request.resource.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource '{request.resource}'. Supported resources: {[e.value for e in ResourceType]}",
        )

    res = WorkspaceService.check_permission(role=role, resource=resource)
    return RBACCheckResponse(**res)
