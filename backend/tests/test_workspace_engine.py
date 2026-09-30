"""
Tests for Workspace & RBAC Security Service (PRD-0003, PRD-0001 §385-§416)
"""

import pytest
from app.models.entity import Entity, EntityType, ConfidenceLevel, EntityStatus
from app.services.workspace_service import (
    WorkspaceService,
    UserRole,
    ResourceType,
)
from tests.conftest import TEST_WORKSPACE_ID


@pytest.mark.asyncio
async def test_workspace_info_and_stats(test_session):
    service = WorkspaceService(db=test_session, workspace_id=TEST_WORKSPACE_ID)

    # Add a couple entities to test stats
    e1 = Entity(
        workspace_id=TEST_WORKSPACE_ID,
        entity_type=EntityType.STRATEGY,
        name="Platform Strategy 2027",
        confidence=ConfidenceLevel.CONFIRMED,
        status=EntityStatus.ACTIVE,
    )
    e2 = Entity(
        workspace_id=TEST_WORKSPACE_ID,
        entity_type=EntityType.REQUIREMENT,
        name="Telemetry Ingestion",
        confidence=ConfidenceLevel.CONFIRMED,
        status=EntityStatus.ACTIVE,
    )
    test_session.add_all([e1, e2])
    await test_session.flush()

    info = await service.get_workspace_info()
    assert info is not None
    assert info["workspace_id"] == TEST_WORKSPACE_ID
    assert "name" in info

    stats = await service.get_aggregated_stats()
    assert stats["total_entities"] >= 2
    assert stats["entities_by_type"].get("strategy", 0) >= 1
    assert stats["entities_by_type"].get("requirement", 0) >= 1


@pytest.mark.asyncio
async def test_workspace_export_snapshot(test_session):
    service = WorkspaceService(db=test_session, workspace_id=TEST_WORKSPACE_ID)

    snapshot = await service.export_workspace_snapshot()
    assert snapshot["workspace_id"] == TEST_WORKSPACE_ID
    assert "exported_at" in snapshot
    assert isinstance(snapshot["entities"], list)
    assert isinstance(snapshot["relationships"], list)


@pytest.mark.asyncio
async def test_workspace_reset_purge(test_session):
    service = WorkspaceService(db=test_session, workspace_id=TEST_WORKSPACE_ID)

    # Purge workspace
    purge_res = await service.reset_workspace_knowledge()
    assert purge_res["status"] == "PURGED"

    # Verify zero entities remaining
    stats = await service.get_aggregated_stats()
    assert stats["total_entities"] == 0


def test_rbac_permission_matrix():
    # CEO has full access to everything
    ceo_check = WorkspaceService.check_permission(UserRole.CEO, ResourceType.BUDGET)
    assert ceo_check["is_authorized"] is True
    assert ceo_check["permission_level"] == "FULL"

    # Sr PM can access roadmap and PRD, but NOT budget
    sr_pm_budget = WorkspaceService.check_permission(UserRole.SR_PM, ResourceType.BUDGET)
    assert sr_pm_budget["is_authorized"] is False
    assert sr_pm_budget["permission_level"] == "NONE"

    sr_pm_roadmap = WorkspaceService.check_permission(UserRole.SR_PM, ResourceType.ROADMAP)
    assert sr_pm_roadmap["is_authorized"] is True

    # Jr PM cannot access client contracts or budget
    jr_pm_contracts = WorkspaceService.check_permission(UserRole.JR_PM, ResourceType.CLIENT_CONTRACTS)
    assert jr_pm_contracts["is_authorized"] is False

    jr_pm_roadmap = WorkspaceService.check_permission(UserRole.JR_PM, ResourceType.ROADMAP)
    assert jr_pm_roadmap["is_authorized"] is True
    assert jr_pm_roadmap["permission_level"] == "READ"

    # QA Lead has no access to roadmap or budget, but has sprint analytics
    qa_roadmap = WorkspaceService.check_permission(UserRole.QA_LEAD, ResourceType.ROADMAP)
    assert qa_roadmap["is_authorized"] is False

    qa_sprint = WorkspaceService.check_permission(UserRole.QA_LEAD, ResourceType.SPRINT_ANALYTICS)
    assert qa_sprint["is_authorized"] is True
