"""
Tests for Engineering Intelligence Engine (PRD-0009)
"""

import pytest
from app.services.engineering_engine import (
    EngineeringIntelligenceEngine,
    EngineeringPhase,
    ADRStatus,
    TechDebtSeverity,
    EstimateConfidence,
    DependencyType,
    TechDebtItem,
    TechnicalRisk,
)


# ─── PRD Technical Analysis ───────────────────────────────────


def test_analyze_prd_technical_implications_detects_components():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Create a REST API endpoint for vendor reconciliation"},
        {"id": "FR-002", "text": "Store reconciliation results in the database with schema migration"},
        {"id": "FR-003", "text": "Send email notification when reconciliation completes"},
        {"id": "FR-004", "text": "Build a dashboard UI to display reconciliation status"},
    ]

    analysis = engine.analyze_prd_technical_implications(
        prd_title="Automated Vendor Reconciliation",
        prd_entity_id="prd-0042",
        requirements=requirements,
    )

    assert analysis.prd_entity_id == "prd-0042"
    assert analysis.phase == EngineeringPhase.TECHNICAL_DISCOVERY
    assert "API Gateway" in analysis.total_affected_components
    assert "Database" in analysis.total_affected_components
    assert "Notification Service" in analysis.total_affected_components
    assert "Frontend / UI" in analysis.total_affected_components
    assert analysis.architecture_impact in ("minor", "moderate", "significant")
    assert len(analysis.implications) == 4
    assert len(analysis.total_risks) >= 0


def test_analyze_prd_detects_risks_for_high_complexity():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Process real-time concurrent transactions with distributed locking"},
        {"id": "FR-002", "text": "Handle payment authorization with security token validation"},
    ]

    analysis = engine.analyze_prd_technical_implications(
        prd_title="Payment Processing",
        prd_entity_id="prd-pay",
        requirements=requirements,
    )

    # Should detect concurrent/distributed risk
    assert any("concurrent" in r.lower() or "distributed" in r.lower() for r in analysis.total_risks)
    # Should detect security risk
    assert any("security" in r.lower() for r in analysis.total_risks)


def test_analyze_empty_requirements():
    engine = EngineeringIntelligenceEngine()

    analysis = engine.analyze_prd_technical_implications(
        prd_title="Empty PRD",
        prd_entity_id="prd-empty",
        requirements=[],
    )

    assert analysis.architecture_impact == "none"
    assert len(analysis.implications) == 0


# ─── Technical Design ─────────────────────────────────────────


def test_generate_technical_design():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Create API endpoint for reconciliation"},
        {"id": "FR-002", "text": "Store results in database"},
        {"id": "FR-003", "text": "Publish event to Kafka queue when complete"},
    ]

    analysis = engine.analyze_prd_technical_implications(
        prd_title="Reconciliation",
        prd_entity_id="prd-042",
        requirements=requirements,
    )

    design = engine.generate_technical_design(
        prd_entity_id="prd-042",
        title="Reconciliation",
        analysis=analysis,
    )

    assert "Technical Design:" in design.title
    assert len(design.components) > 0
    assert len(design.data_flow) > 0
    assert design.migration_strategy != ""
    assert design.rollback_strategy != ""
    assert len(design.observability) > 0


# ─── Engineering Breakdown ─────────────────────────────────────


def test_decompose_into_epics():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Build reconciliation matching engine"},
        {"id": "FR-002", "text": "Create exception queue for ambiguous matches"},
        {"id": "FR-003", "text": "Add audit logging for all reconciliation decisions"},
        {"id": "FR-004", "text": "Build analytics dashboard for reconciliation metrics"},
        {"id": "FR-005", "text": "Create API endpoint for manual reconciliation override"},
    ]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-042",
        prd_title="Vendor Reconciliation",
        requirements=requirements,
    )

    assert breakdown.prd_entity_id == "prd-042"
    assert breakdown.total_stories == 5
    assert breakdown.total_estimated_hours > 0
    assert len(breakdown.epics) > 0

    # Each story should have acceptance criteria
    for epic in breakdown.epics:
        for story in epic.stories:
            assert len(story.acceptance_criteria) >= 3
            assert story.requirement_ref != ""
            assert story.estimated_hours is not None
            assert story.estimated_hours > 0


def test_decompose_single_requirement():
    engine = EngineeringIntelligenceEngine()

    requirements = [{"id": "FR-001", "text": "Add a new button to the dashboard"}]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-001",
        prd_title="Simple Feature",
        requirements=requirements,
    )

    assert breakdown.total_stories == 1
    assert len(breakdown.epics) == 1


# ─── Story Generation ─────────────────────────────────────────


def test_generate_story():
    engine = EngineeringIntelligenceEngine()

    story = engine.generate_story(
        requirement_ref="FR-007",
        requirement_text="Create API endpoint for listing reconciliation results with filtering",
        context="Part of the reconciliation module",
        prd_title="Vendor Reconciliation",
    )

    assert story.story_id == "STORY-FR-007"
    assert story.requirement_ref == "FR-007"
    assert len(story.acceptance_criteria) >= 3
    # Should have extra AC for list/search/filter
    assert any("empty result" in ac.lower() for ac in story.acceptance_criteria)
    assert story.estimated_hours is not None


# ─── Dependency Mapping ───────────────────────────────────────


def test_map_dependencies():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Create database schema and migration for reconciliation"},
        {"id": "FR-002", "text": "Build API endpoint for reconciliation service"},
        {"id": "FR-003", "text": "Build UI dashboard for reconciliation status"},
    ]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-042",
        prd_title="Reconciliation",
        requirements=requirements,
    )

    deps = engine.map_dependencies(breakdown)

    # Should detect: DB blocks API, API blocks UI
    assert len(deps) > 0
    assert any(d.is_blocking for d in deps)


# ─── Effort Estimation ────────────────────────────────────────


def test_estimate_effort():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Build API endpoint"},
        {"id": "FR-002", "text": "Build database migration"},
    ]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-001",
        prd_title="Test",
        requirements=requirements,
    )

    estimate = engine.estimate_effort(breakdown)

    assert estimate.total_hours > 0
    assert estimate.development_hours > 0
    assert estimate.testing_hours > 0
    assert estimate.contingency_hours > 0
    assert estimate.total_hours > estimate.development_hours
    assert estimate.confidence == EstimateConfidence.MEDIUM
    assert any("estimate" in a.lower() for a in estimate.assumptions)


# ─── Capacity Analysis ────────────────────────────────────────


def test_analyze_capacity_detects_conflict():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Build complex real-time concurrent distributed system"},
        {"id": "FR-002", "text": "Build API endpoint with database migration"},
        {"id": "FR-003", "text": "Build UI dashboard with frontend components"},
    ]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-001",
        prd_title="Big Feature",
        requirements=requirements,
    )
    estimate = engine.estimate_effort(breakdown)

    # Give very little capacity → should detect conflict
    capacity = engine.analyze_capacity(
        available_hours=10.0,
        estimate=estimate,
    )

    assert capacity.has_conflict is True
    assert capacity.conflict_hours > 0
    assert capacity.utilization_percent > 100
    assert len(capacity.recommendations) > 0


def test_analyze_capacity_sufficient():
    engine = EngineeringIntelligenceEngine()

    requirements = [{"id": "FR-001", "text": "Add a button"}]

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-001",
        prd_title="Tiny Feature",
        requirements=requirements,
    )
    estimate = engine.estimate_effort(breakdown)

    capacity = engine.analyze_capacity(
        available_hours=500.0,
        estimate=estimate,
    )

    assert capacity.has_conflict is False
    assert capacity.conflict_hours == 0


# ─── Duplicate Detection ──────────────────────────────────────


@pytest.mark.asyncio
async def test_detect_duplicate_work_requires_db():
    engine = EngineeringIntelligenceEngine()

    with pytest.raises(ValueError, match="AsyncSession"):
        await engine.detect_duplicate_work("Build reconciliation engine")


# ─── Technical Debt ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_tech_debt_requires_db():
    engine = EngineeringIntelligenceEngine()

    item = TechDebtItem(
        component="Payment Service",
        description="Hardcoded currency conversion rates",
        severity=TechDebtSeverity.HIGH,
        product_impact="Cannot support multi-currency payments",
        business_cost="Blocking EMEA market expansion",
        remediation="Integrate with live FX rate provider",
    )

    with pytest.raises(ValueError, match="AsyncSession"):
        await engine.record_tech_debt(item)


# ─── Engineering Handoff ──────────────────────────────────────


def test_generate_engineering_handoff():
    engine = EngineeringIntelligenceEngine()

    requirements = [
        {"id": "FR-001", "text": "Create API endpoint for reconciliation"},
        {"id": "FR-002", "text": "Store results in database"},
        {"id": "FR-003", "text": "Build dashboard UI for reconciliation"},
    ]

    analysis = engine.analyze_prd_technical_implications(
        prd_title="Vendor Reconciliation",
        prd_entity_id="prd-042",
        requirements=requirements,
    )

    breakdown = engine.decompose_into_epics(
        prd_entity_id="prd-042",
        prd_title="Vendor Reconciliation",
        requirements=requirements,
    )

    estimate = engine.estimate_effort(breakdown)

    handoff = engine.generate_engineering_handoff(
        prd_title="Vendor Reconciliation",
        prd_entity_id="prd-042",
        analysis=analysis,
        breakdown=breakdown,
        estimate=estimate,
        objective="Reduce reconciliation effort by 50%",
    )

    assert handoff.initiative_name == "Vendor Reconciliation"
    assert handoff.prd_reference == "prd-042"
    assert handoff.objective == "Reduce reconciliation effort by 50%"
    assert len(handoff.affected_components) > 0
    assert len(handoff.epics) > 0
    assert handoff.total_stories == 3
    assert handoff.total_estimated_hours > 0
    assert handoff.estimate_confidence == EstimateConfidence.MEDIUM.value
