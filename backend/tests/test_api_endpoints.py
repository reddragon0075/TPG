"""
Integration Tests for TPG FastAPI Endpoints
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_memory_store_and_recall(async_client):
    # Store an entity
    store_payload = {
        "entity_type": "requirement",
        "name": "Single Sign-On (SAML/Okta)",
        "description": "Enterprise clients require SAML 2.0 integration for user authentication.",
        "properties": {"priority": "P0", "category": "security"},
        "source": "sales_deal_blocker",
        "confidence": "confirmed",
    }
    store_res = await async_client.post("/memory/store", json=store_payload)
    assert store_res.status_code == 200
    store_data = store_res.json()
    assert store_data["name"] == "Single Sign-On (SAML/Okta)"
    entity_id = store_data["entity_id"]

    # Recall
    recall_payload = {"query": "SAML Okta"}
    recall_res = await async_client.post("/memory/recall", json=recall_payload)
    assert recall_res.status_code == 200
    recall_data = recall_res.json()
    assert recall_data["total_results"] >= 1
    assert any(e["id"] == entity_id for e in recall_data["entities"])


@pytest.mark.asyncio
async def test_intelligence_requirement_analysis_endpoint(async_client):
    payload = {
        "statement": "We want an automatic Slack notification when trips are delayed by 15 minutes.",
        "context": {"source": "operations"},
    }
    res = await async_client.post("/intelligence/requirements/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_product_requirement"] is True
    assert "ambiguity_score" in data
    assert len(data["prioritized_questions"]) > 0


@pytest.mark.asyncio
async def test_intelligence_decision_evaluation_endpoint(async_client):
    payload = {
        "decision_question": "Should we build our own notification engine or use Novu/Courier?",
        "options": [
            {
                "name": "Novu / Courier Cloud",
                "description": "Multi-channel notifications SaaS",
                "effort": 2.0,
                "impact": 4.0,
                "risk": 1.5,
                "confidence": 0.85,
            },
            {
                "name": "Build Custom Notification Queue",
                "description": "Custom Redis and Celery worker infrastructure",
                "effort": 4.5,
                "impact": 3.5,
                "risk": 4.0,
                "confidence": 0.6,
            },
        ],
    }
    res = await async_client.post("/intelligence/decisions/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Novu" in data["top_recommendation"]
    assert len(data["ranked_options"]) == 2


@pytest.mark.asyncio
async def test_intelligence_graph_query_endpoint(async_client):
    # Store an initiative first
    store_payload = {
        "entity_type": "initiative",
        "name": "Vendor Wallet",
        "description": "Automated ledger and settlement wallet for vendors.",
        "source": "founder",
    }
    store_res = await async_client.post("/memory/store", json=store_payload)
    assert store_res.status_code == 200

    # Query the graph
    query_payload = {"query": "Why did we build Vendor Wallet?"}
    res = await async_client.post("/intelligence/graph/query", json=query_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ["why_decision", "lineage_trace", "general_search"]
    assert "Vendor Wallet" in data["narrative_summary"]


@pytest.mark.asyncio
async def test_strategy_api_endpoints(async_client):
    # Create theme
    theme_res = await async_client.post(
        "/strategy/themes",
        json={
            "name": "Platform Modernization",
            "description": "Migrate to modular event architecture.",
            "priority": "HIGH",
            "time_horizon": "6_12_MONTHS",
        },
    )
    assert theme_res.status_code == 200
    assert theme_res.json()["name"] == "Platform Modernization"

    # Score alignment
    align_res = await async_client.post(
        "/strategy/align",
        json={
            "initiative_name": "Kafka Event Bus",
            "problem_statement": "System needs scalable asynchronous messaging.",
            "linked_theme": "Platform Modernization",
            "linked_objective": "Sub-100ms latency",
            "has_validated_evidence": True,
        },
    )
    assert align_res.status_code == 200
    assert align_res.json()["alignment_score"] >= 80.0

    # Portfolio balance
    bal_res = await async_client.post(
        "/strategy/portfolio-balance",
        json={"allocations": {"growth": 50.0, "retention": 30.0, "tech_debt": 20.0}},
    )
    assert bal_res.status_code == 200
    assert bal_res.json()["status"] == "BALANCED"


@pytest.mark.asyncio
async def test_connector_api_endpoints(async_client):
    # Register connector
    conn_res = await async_client.post(
        "/connectors",
        json={
            "connector_type": "slack",
            "display_name": "Internal Ops Slack",
            "config": {"channel": "#ops"},
        },
    )
    assert conn_res.status_code == 200
    assert conn_res.json()["connector_type"] == "slack"

    # List connectors
    list_res = await async_client.get("/connectors")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Detect commitment
    commit_res = await async_client.post(
        "/connectors/commitments/detect",
        json={"text": "We will deliver the audit logs by next Wednesday."},
    )
    assert commit_res.status_code == 200
    assert commit_res.json()["commitments_found"] >= 1

    # Draft internal action
    draft_res = await async_client.post(
        "/connectors/actions/draft",
        json={
            "action_type": "EMAIL_DRAFT",
            "target": "client@enterprise.com",
            "context": "Customer requested update",
            "user_intent": "Confirm deliverable timeline",
        },
    )
    assert draft_res.status_code == 200
    assert draft_res.json()["requires_human_approval"] is True


@pytest.mark.asyncio
async def test_workspace_api_endpoints(async_client):
    # Workspace details
    me_res = await async_client.get("/workspace/me")
    assert me_res.status_code == 200
    assert "owner_email" in me_res.json()

    # Workspace stats
    stats_res = await async_client.get("/workspace/stats")
    assert stats_res.status_code == 200
    assert "total_entities" in stats_res.json()

    # RBAC check
    rbac_res = await async_client.post(
        "/workspace/rbac/check",
        json={"role": "CEO", "resource": "budget"},
    )
    assert rbac_res.status_code == 200
    assert rbac_res.json()["is_authorized"] is True

