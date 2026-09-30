"""
Tests for Connector Intelligence Framework Engine (PRD-0004)
"""

import pytest
from app.models.connector import ConnectorType, ConnectorStatus
from app.services.connector_engine import (
    ConnectorIntelligenceEngine,
    IngestionBatchItem,
    InternalActionType,
)
from tests.conftest import TEST_WORKSPACE_ID


@pytest.mark.asyncio
async def test_register_and_list_connector(test_session):
    engine = ConnectorIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)

    # Register Slack connector
    res = await engine.register_connector(
        connector_type=ConnectorType.SLACK,
        display_name="Product Slack Workspace",
        config={"channels": ["#product", "#releases"]},
    )
    assert res["connector_id"] is not None
    assert res["status"] == ConnectorStatus.CONNECTED.value

    # List connectors
    connectors = await engine.list_connectors()
    assert len(connectors) >= 1
    assert any(c["display_name"] == "Product Slack Workspace" for c in connectors)


@pytest.mark.asyncio
async def test_ingest_batch_signals_and_commitments(test_session):
    engine = ConnectorIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)

    items = [
        IngestionBatchItem(
            channel="slack",
            sender="sarah.pm@example.com",
            content="We will deliver the updated API documentation by Monday.",
        ),
        IngestionBatchItem(
            channel="gmail",
            sender="enterprise-client@bigcorp.com",
            content="Our security audit team requires SOC2 compliance before final rollout.",
        ),
    ]

    res = await engine.ingest_batch(items)
    assert res["processed_count"] == 2
    assert res["signals_ingested"] == 2
    assert res["commitments_detected"] >= 1
    assert any("documentation" in c["deliverable"].lower() for c in res["detected_commitments"])


def test_detect_commitments_patterns():
    engine = ConnectorIntelligenceEngine()

    text = (
        "Sarah mentioned that we will ship the Vendor Wallet by 15 October. "
        "Also, I will submit the updated telemetry specs on Friday. "
        "Just a regular status update note with no commitments."
    )

    commitments = engine.detect_commitments_in_text(text, default_owner="Sarah")
    assert len(commitments) == 2
    assert any("Vendor Wallet" in c.deliverable for c in commitments)
    assert any("15 October" in c.due_date for c in commitments)


def test_draft_internal_action_constitutional_boundaries():
    engine = ConnectorIntelligenceEngine()

    # Draft email
    email_draft = engine.draft_internal_action(
        action_type=InternalActionType.EMAIL_DRAFT,
        recipient_or_target="customer@client.com",
        context="Client requested custom webhook integration.",
        user_intent="Explain webhook availability on current enterprise tier.",
    )
    assert email_draft["requires_human_approval"] is True
    assert email_draft["dispatched"] is False
    assert "customer@client.com" in email_draft["target"]
    assert "webhook" in email_draft["draft_body"].lower()

    # Draft Jira Story
    jira_draft = engine.draft_internal_action(
        action_type=InternalActionType.JIRA_ISSUE_DRAFT,
        recipient_or_target="PROJECT-PROD",
        context="Telemetry pipeline upgrade",
        user_intent="Support OpenTelemetry ingestion",
    )
    assert jira_draft["requires_human_approval"] is True
    assert jira_draft["dispatched"] is False
    assert jira_draft["issue_type"] == "Story"
