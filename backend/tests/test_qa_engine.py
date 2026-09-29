"""
Tests for QA & Release Intelligence Engine (PRD-0010)
"""

import pytest
from app.services.qa_engine import (
    QAIntelligenceEngine,
    DefectRecord,
    DefectSeverity,
    DefectPriority,
    RiskClassification,
    TestLevel,
    QualityGateStatus,
)


def test_generate_test_strategy():
    engine = QAIntelligenceEngine()
    
    requirements = [
        {"id": "FR-001", "text": "Secure payment processing with external gateway"},
        {"id": "FR-002", "text": "Basic UI dashboard for transaction history"},
    ]
    
    strategy = engine.generate_test_strategy(
        prd_entity_id="prd-123",
        prd_title="Payments",
        requirements=requirements,
    )
    
    # High risk due to "payment" and "secure"
    assert strategy.risk_level in (RiskClassification.CRITICAL, RiskClassification.HIGH)
    assert strategy.automation_required is True
    # Should contain E2E and SECURITY because of keywords
    assert TestLevel.E2E in strategy.test_levels
    assert TestLevel.SECURITY in strategy.test_levels


def test_derive_test_cases():
    engine = QAIntelligenceEngine()
    
    cases = engine.derive_test_cases(
        requirement_ref="FR-001",
        requirement_text="Limit user list to 50 concurrent requests per minute",
        acceptance_criteria=[
            "Returns 429 when exceeding limit",
            "Returns 200 when under limit"
        ]
    )
    
    # Base cases: Positive, Negative, Permission, Boundary (due to 'limit'), Error, Concurrency (due to 'concurrent')
    # Plus 2 AC cases
    assert len(cases) >= 6
    scenario_types = [c.scenario_type for c in cases]
    assert any("BOUNDARY" in str(t) for t in scenario_types)
    assert any("CONCURRENCY" in str(t) for t in scenario_types)


def test_assess_quality_risk():
    engine = QAIntelligenceEngine()
    
    risk = engine.assess_quality_risk(
        requirement_ref="FR-001",
        requirement_text="Migrate legacy database to new distributed schema while maintaining real-time auth compliance",
    )
    
    # "migration", "database", "distributed", "auth", "compliance" -> High impact, High likelihood
    assert risk.impact == "HIGH"
    assert risk.likelihood == "HIGH"
    assert risk.risk_level in (RiskClassification.CRITICAL, RiskClassification.HIGH)


def test_classify_defect():
    engine = QAIntelligenceEngine()
    
    classification = engine.classify_defect(
        description="Users get a 500 error and system crashes when clicking login. It worked before yesterday's release."
    )
    
    assert classification.severity == DefectSeverity.CRITICAL
    assert classification.priority == DefectPriority.P0
    assert classification.is_regression is True
    assert classification.affected_component == "Authentication"


def test_generate_regression_set():
    engine = QAIntelligenceEngine()
    
    reg_set = engine.generate_regression_set(
        change_scope="Update billing database schema and API endpoints",
        total_test_count=100
    )
    
    # Should select API, Database, and Financial categories
    assert any("API" in cat for cat in reg_set.test_categories)
    assert any("Integrity" in cat for cat in reg_set.test_categories)
    assert any("Financial" in cat for cat in reg_set.test_categories)
    # Selection ratio should be higher due to risk
    assert reg_set.selected_test_count > 20


def test_assess_release_readiness():
    engine = QAIntelligenceEngine()
    
    readiness = engine.assess_release_readiness(
        release_name="v1.0.0",
        total_tests=100,
        passed_tests=98,
        failed_tests=2,
        blocked_tests=0,
        critical_defects=0,
        high_defects=1,
        total_requirements=50,
        covered_requirements=45,  # 90%
    )
    
    # 98% pass rate, 0 critical, 1 high, 90% coverage, 0 blocked -> Should pass all gates
    assert readiness.overall_status == "GO"
    assert readiness.failed_gates == 0
    assert readiness.passed_gates == 5


def test_assess_release_readiness_no_go():
    engine = QAIntelligenceEngine()
    
    readiness = engine.assess_release_readiness(
        release_name="v1.0.1",
        total_tests=100,
        passed_tests=80,  # 80% pass rate
        failed_tests=20,
        blocked_tests=1,
        critical_defects=2,
        high_defects=5,
        total_requirements=50,
        covered_requirements=30,  # 60% coverage
    )
    
    assert readiness.overall_status == "NO_GO"
    assert readiness.failed_gates > 0
    assert any(g.status == QualityGateStatus.FAILED for g in readiness.quality_gates if g.gate_name == "Test Pass Rate")
    assert any(g.status == QualityGateStatus.FAILED for g in readiness.quality_gates if g.gate_name == "Critical Defects")


def test_analyze_test_coverage():
    engine = QAIntelligenceEngine()
    
    requirements = [{"id": "FR-001"}, {"id": "FR-002"}, {"id": "FR-003"}, {"id": "FR-004"}]
    tested = ["FR-001", "FR-002"]
    
    coverage = engine.analyze_test_coverage(requirements, tested)
    
    assert coverage.total_requirements == 4
    assert coverage.covered_requirements == 2
    assert coverage.coverage_percent == 50.0
    assert len(coverage.uncovered_requirements) == 2


def test_trace_production_incident():
    engine = QAIntelligenceEngine()
    
    trace = engine.trace_production_incident(
        incident_description="Service timeout when 100 concurrent users try to export CSV data."
    )
    
    assert "Performance" in trace.probable_root_cause
    assert any("performance" in gap.lower() for gap in trace.test_gaps)
    assert len(trace.recommended_new_tests) > 0


# ─── Database-dependent methods ────────────────────────────────


@pytest.mark.asyncio
async def test_record_defect_requires_db():
    engine = QAIntelligenceEngine()
    
    record = DefectRecord(
        title="Test Defect",
        description="Test",
        requirement_ref="FR-001",
        severity=DefectSeverity.MEDIUM,
        priority=DefectPriority.P2,
        steps_to_reproduce=[],
        expected_behavior="x",
        actual_behavior="y",
    )
    
    with pytest.raises(ValueError, match="AsyncSession"):
        await engine.record_defect(record)


@pytest.mark.asyncio
async def test_detect_duplicate_defect_requires_db():
    engine = QAIntelligenceEngine()
    
    with pytest.raises(ValueError, match="AsyncSession"):
        await engine.detect_duplicate_defect("System crashes on login")


@pytest.mark.asyncio
async def test_trace_requirement_to_tests_requires_db():
    engine = QAIntelligenceEngine()
    
    with pytest.raises(ValueError, match="AsyncSession"):
        await engine.trace_requirement_to_tests("req-123")
