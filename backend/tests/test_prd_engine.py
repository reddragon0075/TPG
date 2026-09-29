"""
Tests for PRD & Product Specification Engine — PRD-0008
"""

import pytest
from app.services.prd_engine import (
    PRDSpecificationEngine,
    PRDReadinessLevel,
    PRDStatus,
)
from tests.conftest import TEST_WORKSPACE_ID


def test_prd_readiness_assessment():
    engine = PRDSpecificationEngine()

    # 1. Empty / Insufficient input
    res_empty = engine.assess_readiness(problem=None, requirements=[])
    assert res_empty.level == PRDReadinessLevel.NOT_READY
    assert len(res_empty.missing_critical_items) >= 2

    # 2. Problem only, no requirements
    res_partial = engine.assess_readiness(
        problem="Vendors lack visibility into daily payout ledger settlements.",
        requirements=[],
    )
    assert res_partial.level == PRDReadinessLevel.NOT_READY

    # 3. Complete input satisfying all constitutional gates
    res_ready = engine.assess_readiness(
        problem="Enterprise customers experience 48h delays reconciling vendor batch payments.",
        requirements=[
            "Automated webhook listener for Stripe payout confirmations",
            "Batch ledger settlement generator with idempotency protection",
            "Real-time reconciliation status dashboard with CSV export",
        ],
        decision_rationale="Approved by Product Leadership based on $50k monthly operational savings.",
        evidence=["14 enterprise support tickets", "Finance team interview notes"],
        success_metric="Reduce reconciliation cycle from 48h to < 10m",
    )
    assert res_ready.level == PRDReadinessLevel.EXECUTION_READY
    assert res_ready.overall_score == 1.0
    assert len(res_ready.missing_critical_items) == 0


def test_constitutional_prd_generation_and_markdown():
    engine = PRDSpecificationEngine()

    prd = engine.generate_prd(
        title="Vendor Wallet",
        problem="Vendors experience payment reconciliation delays causing vendor churn.",
        raw_requirements=[
            "Automated webhook settlement listener",
            "Idempotent batch transaction processing",
            "Exportable daily ledger statement",
        ],
        decision_rationale="Executive Decision: Approved based on high ROI.",
        evidence=["Ops tickets #412", "Survey of 50 top logistics vendors"],
        target_personas=["Logistics Fleet Operator", "Finance Manager"],
        non_goals=[
            "Cryptocurrency payments",
            "Direct P2P loans",
        ],
        success_metric="Settlement time reduced to < 5 minutes",
    )

    # Validate structure
    assert prd.title == "Vendor Wallet"
    assert prd.version == 1
    assert prd.status == PRDStatus.DRAFT
    assert len(prd.non_goals) == 2
    assert "Cryptocurrency payments" in prd.non_goals
    assert len(prd.functional_requirements) == 3
    assert len(prd.acceptance_criteria) == 3

    # Check Gherkin criteria
    first_ac = prd.acceptance_criteria[0]
    assert "Given" in first_ac.given or len(first_ac.given) > 0
    assert "When" in first_ac.when or len(first_ac.when) > 0
    assert "Then" in first_ac.then or len(first_ac.then) > 0

    # Validate Markdown rendering
    md = engine.render_markdown(prd)
    assert "# PRD: Vendor Wallet" in md
    assert "## 1. Executive Summary" in md
    assert "## 3. Scope Fencing (Goals vs. Non-Goals)" in md
    assert "**OUT OF SCOPE:** Cryptocurrency payments" in md
    assert "## 5. Acceptance Criteria (Gherkin)" in md


@pytest.mark.asyncio
async def test_prd_knowledge_graph_persistence_and_versioning(test_session):
    ws_id = TEST_WORKSPACE_ID
    engine = PRDSpecificationEngine(db=test_session, workspace_id=ws_id)

    prd_v1 = engine.generate_prd(
        title="Fleet Rostering Engine",
        problem="Manual fleet shifts cause route assignment overlap.",
        raw_requirements=["Automated shift scheduler", "Driver conflict detection"],
    )

    res_v1 = await engine.save_prd(prd_v1)
    assert res_v1["version"] == 1
    assert res_v1["title"] == "Fleet Rostering Engine"
    prd_id_v1 = res_v1["prd_id"]

    # Save revision with same title -> must increment to version 2
    prd_v2 = engine.generate_prd(
        title="Fleet Rostering Engine",
        problem="Manual fleet shifts cause route assignment overlap and overtime breaches.",
        raw_requirements=["Automated shift scheduler", "Driver conflict detection", "Overtime threshold alerts"],
    )
    res_v2 = await engine.save_prd(prd_v2)
    assert res_v2["version"] == 2
    assert res_v2["prd_id"] != prd_id_v1


@pytest.mark.asyncio
async def test_prd_api_integration(async_client):
    # 1. Assess Readiness
    assess_payload = {
        "problem": "Customers unable to export historical audits.",
        "requirements": ["CSV export button", "Background report generation worker"],
        "evidence": ["Customer survey"],
    }
    assess_res = await async_client.post("/intelligence/prd/assess", json=assess_payload)
    assert assess_res.status_code == 200
    assert assess_res.json()["overall_score"] > 0

    # 2. Generate PRD
    gen_payload = {
        "title": "Historical Audit Export",
        "problem": "Enterprise security auditors require CSV dumps of all user permissions.",
        "raw_requirements": [
            "Async export worker with pre-signed S3 download URL",
            "Audit event logging for export triggers",
        ],
        "non_goals": ["PDF rendering in v1"],
    }
    gen_res = await async_client.post("/intelligence/prd/generate", json=gen_payload)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert "Historical Audit Export" in gen_data["markdown"]
    assert "**OUT OF SCOPE:** PDF rendering in v1" in gen_data["markdown"]

    # 3. Save PRD
    save_res = await async_client.post("/intelligence/prd/save", json=gen_payload)
    assert save_res.status_code == 200
    save_data = save_res.json()
    prd_id = save_data["prd_id"]
    assert save_data["version"] == 1

    # 4. Fetch PRD
    get_res = await async_client.get(f"/intelligence/prd/{prd_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Historical Audit Export"
