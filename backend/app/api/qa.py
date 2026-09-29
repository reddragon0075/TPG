"""
QA & Release Intelligence API — PRD-0010

Exposes TPG's quality and release intelligence capabilities:
1. Test Strategy Generation (Risk-based)
2. Test Case Derivation (Positive, negative, boundary, etc.)
3. Quality Risk Assessment
4. Defect Recording & Classification
5. Impact-based Regression Set Selection
6. Evidence-based Release Readiness Assessment
7. Requirement-to-Test Traceability
8. Requirement Coverage Analysis
9. Production Incident Tracing
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.schemas import (
    TestStrategyRequest,
    TestStrategyResponse,
    TestCaseRequest,
    TestCaseResponse,
    TestCaseSchema,
    QualityRiskRequest,
    QualityRiskResponse,
    DefectRequest,
    DefectResponse,
    DefectClassifyRequest,
    DefectClassifyResponse,
    RegressionSetRequest,
    RegressionSetResponse,
    ReleaseReadinessRequest,
    ReleaseReadinessResponse,
    QualityGateSchema,
    CoverageRequest,
    CoverageResponse,
    TraceabilityResponse,
    IncidentTraceRequest,
    IncidentTraceResponse,
)
from app.services.qa_engine import (
    QAIntelligenceEngine,
    DefectRecord,
    DefectSeverity,
    DefectPriority,
)

router = APIRouter(prefix="/qa", tags=["QA & Release Intelligence"])


@router.post(
    "/test-strategy",
    response_model=TestStrategyResponse,
    summary="Generate Test Strategy",
    description="Generates a risk-based test strategy for a PRD.",
)
async def generate_test_strategy(
    request: TestStrategyRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]
    
    strategy = engine.generate_test_strategy(
        prd_entity_id=request.prd_entity_id,
        prd_title=request.prd_title,
        requirements=reqs,
    )
    
    return TestStrategyResponse(
        prd_entity_id=strategy.prd_entity_id,
        prd_title=strategy.prd_title,
        risk_level=strategy.risk_level.value,
        test_levels=[t.value for t in strategy.test_levels],
        automation_required=strategy.automation_required,
        estimated_test_effort_hours=strategy.estimated_test_effort_hours,
        key_risk_areas=strategy.key_risk_areas,
        testing_approach=strategy.testing_approach,
        exit_criteria=strategy.exit_criteria,
        assumptions=strategy.assumptions,
    )


@router.post(
    "/test-cases",
    response_model=TestCaseResponse,
    summary="Derive Test Cases",
    description="Generates positive, negative, boundary, and error test cases from a requirement.",
)
async def derive_test_cases(
    request: TestCaseRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    cases = engine.derive_test_cases(
        requirement_ref=request.requirement_ref,
        requirement_text=request.requirement_text,
        acceptance_criteria=request.acceptance_criteria,
    )
    
    return TestCaseResponse(
        requirement_ref=request.requirement_ref,
        test_cases=[
            TestCaseSchema(
                test_case_id=c.test_case_id,
                requirement_ref=c.requirement_ref,
                title=c.title,
                test_level=c.test_level.value,
                preconditions=c.preconditions,
                steps=c.steps,
                expected_result=c.expected_result,
                scenario_type=c.scenario_type.value,
                priority=c.priority,
                is_automatable=c.is_automatable,
            )
            for c in cases
        ],
        total_cases=len(cases),
    )


@router.post(
    "/risk-assess",
    response_model=QualityRiskResponse,
    summary="Assess Quality Risk",
    description="Assesses requirement quality risk using Impact × Likelihood × Uncertainty.",
)
async def assess_quality_risk(
    request: QualityRiskRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    risk = engine.assess_quality_risk(
        requirement_ref=request.requirement_ref,
        requirement_text=request.requirement_text,
    )
    
    return QualityRiskResponse(
        requirement_ref=risk.requirement_ref,
        requirement_text=risk.requirement_text,
        impact=risk.impact,
        likelihood=risk.likelihood,
        uncertainty=risk.uncertainty,
        risk_level=risk.risk_level.value,
        reasoning=risk.reasoning,
        recommended_test_depth=risk.recommended_test_depth,
    )


@router.post(
    "/defect",
    response_model=DefectResponse,
    summary="Record a Defect",
    description="Records a defect in the Knowledge Graph, optionally linked to a requirement.",
)
async def record_defect(
    request: DefectRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(db=db, workspace_id=workspace_id)
    
    try:
        severity = DefectSeverity(request.severity.upper())
    except ValueError:
        severity = DefectSeverity.MEDIUM
        
    try:
        priority = DefectPriority(request.priority.upper())
    except ValueError:
        priority = DefectPriority.P2
        
    record = DefectRecord(
        title=request.title,
        description=request.description,
        requirement_ref=request.requirement_ref,
        severity=severity,
        priority=priority,
        steps_to_reproduce=request.steps_to_reproduce,
        expected_behavior=request.expected_behavior,
        actual_behavior=request.actual_behavior,
        environment=request.environment,
        is_regression=request.is_regression,
        root_cause_category=request.root_cause_category,
    )
    
    result = await engine.record_defect(record)
    await db.commit()
    
    return DefectResponse(**result)


@router.post(
    "/defect/classify",
    response_model=DefectClassifyResponse,
    summary="Classify Defect Description",
    description="Classifies a defect's severity, priority, regression flag, and root cause based on its description.",
)
async def classify_defect(
    request: DefectClassifyRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    classification = engine.classify_defect(description=request.description)
    
    return DefectClassifyResponse(
        severity=classification.severity.value,
        priority=classification.priority.value,
        is_regression=classification.is_regression,
        root_cause_category=classification.root_cause_category,
        affected_component=classification.affected_component,
        similar_defects=classification.similar_defects,
    )


@router.post(
    "/regression-set",
    response_model=RegressionSetResponse,
    summary="Generate Regression Set",
    description="Selects an impact-based regression test set from a change scope description.",
)
async def generate_regression_set(
    request: RegressionSetRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    reg_set = engine.generate_regression_set(
        change_scope=request.change_scope,
        total_test_count=request.total_test_count,
    )
    
    return RegressionSetResponse(
        change_scope=reg_set.change_scope,
        selected_test_count=reg_set.selected_test_count,
        test_categories=reg_set.test_categories,
        rationale=reg_set.rationale,
        estimated_execution_hours=reg_set.estimated_execution_hours,
        risk_areas=reg_set.risk_areas,
    )


@router.post(
    "/release-readiness",
    response_model=ReleaseReadinessResponse,
    summary="Assess Release Readiness",
    description="Evidence-based release readiness assessment evaluating multiple quality gates.",
)
async def assess_release_readiness(
    request: ReleaseReadinessRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    readiness = engine.assess_release_readiness(
        release_name=request.release_name,
        total_tests=request.total_tests,
        passed_tests=request.passed_tests,
        failed_tests=request.failed_tests,
        blocked_tests=request.blocked_tests,
        critical_defects=request.critical_defects,
        high_defects=request.high_defects,
        total_requirements=request.total_requirements,
        covered_requirements=request.covered_requirements,
    )
    
    return ReleaseReadinessResponse(
        release_name=readiness.release_name,
        overall_status=readiness.overall_status,
        test_pass_rate=readiness.test_pass_rate,
        open_critical_defects=readiness.open_critical_defects,
        open_high_defects=readiness.open_high_defects,
        coverage_percent=readiness.coverage_percent,
        quality_gates=[
            QualityGateSchema(
                gate_name=g.gate_name,
                criteria=g.criteria,
                status=g.status.value,
                evidence=g.evidence,
                override_reason=g.override_reason,
                override_approver=g.override_approver,
            )
            for g in readiness.quality_gates
        ],
        passed_gates=readiness.passed_gates,
        failed_gates=readiness.failed_gates,
        risks=readiness.risks,
        recommendation=readiness.recommendation,
    )


@router.post(
    "/coverage",
    response_model=CoverageResponse,
    summary="Analyze Test Coverage",
    description="Analyzes requirement-to-test coverage.",
)
async def analyze_coverage(
    request: CoverageRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]
    
    coverage = engine.analyze_test_coverage(
        requirements=reqs,
        tested_requirements=request.tested_requirements,
    )
    
    return CoverageResponse(
        total_requirements=coverage.total_requirements,
        covered_requirements=coverage.covered_requirements,
        uncovered_requirements=coverage.uncovered_requirements,
        coverage_percent=coverage.coverage_percent,
        coverage_by_level=coverage.coverage_by_level,
        recommendation=coverage.recommendation,
    )


@router.get(
    "/traceability/{requirement_id}",
    response_model=TraceabilityResponse,
    summary="Requirement Traceability",
    description="Traces a requirement to its test cases and execution results in the Knowledge Graph.",
)
async def get_traceability(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(db=db, workspace_id=workspace_id)
    
    trace = await engine.trace_requirement_to_tests(requirement_id)
    
    return TraceabilityResponse(
        requirement_ref=trace.requirement_ref,
        requirement_text=trace.requirement_text,
        linked_test_cases=trace.linked_test_cases,
        test_results=trace.test_results,
        is_fully_covered=trace.is_fully_covered,
    )


@router.post(
    "/incident-trace",
    response_model=IncidentTraceResponse,
    summary="Trace Production Incident",
    description="Traces a production incident back to potential test gaps and generates quality learning.",
)
async def trace_incident(
    request: IncidentTraceRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = QAIntelligenceEngine(workspace_id=workspace_id)
    
    trace = engine.trace_production_incident(
        incident_description=request.incident_description,
    )
    
    return IncidentTraceResponse(
        incident_description=trace.incident_description,
        probable_root_cause=trace.probable_root_cause,
        related_requirements=trace.related_requirements,
        test_gaps=trace.test_gaps,
        existing_tests=trace.existing_tests,
        recommended_new_tests=trace.recommended_new_tests,
        quality_learning=trace.quality_learning,
    )
