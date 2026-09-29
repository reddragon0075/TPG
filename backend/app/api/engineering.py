"""
Engineering Intelligence API — PRD-0009

Exposes TPG's engineering intelligence capabilities:
1. PRD Technical Analysis — identify affected components, new components, dependencies, risks
2. Technical Design Generation — structured design specifications
3. Architecture Decision Records — create and persist ADRs
4. Engineering Breakdown — decompose PRDs into epics → stories → subtasks
5. Effort Estimation — development + testing + integration + contingency
6. Capacity Analysis — detect team overload
7. Technical Debt — first-class knowledge entities
8. Technical Risk — risk tracking with mitigation
9. Implementation Drift Detection — PRD vs execution comparison
10. Blocker Analysis — blocked stories with aging
11. Engineering Handoff — complete handoff document
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.schemas import (
    EngineeringAnalyzeRequest,
    EngineeringAnalyzeResponse,
    TechnicalImplicationSchema,
    TechnicalDesignRequest,
    TechnicalDesignResponse,
    ComponentSchema,
    ADRCreateRequest,
    ADRCreateResponse,
    BreakdownRequest,
    BreakdownResponse,
    EpicSchema,
    StorySchema,
    DependencySchema,
    EffortEstimateRequest,
    EffortEstimateResponse,
    CapacityRequest,
    CapacityResponse,
    TechDebtRequest,
    TechDebtResponse,
    TechRiskRequest,
    TechRiskResponse,
    DriftAnalysisResponse,
    DriftItemSchema,
    BlockerAnalysisResponse,
    BlockerSchema,
    HandoffRequest,
    HandoffResponse,
)
from app.services.engineering_engine import (
    EngineeringIntelligenceEngine,
    TechDebtItem,
    TechDebtSeverity,
    TechnicalRisk,
)


router = APIRouter(prefix="/engineering", tags=["Engineering Intelligence"])


# ─── PRD Technical Analysis (PRD-0009 §8, §16) ────────────────


@router.post(
    "/analyze",
    response_model=EngineeringAnalyzeResponse,
    summary="Analyze PRD for technical implications",
    description=(
        "Inspects a PRD's requirements to identify affected components, "
        "new components needed, dependencies, and technical risks. "
        "Does NOT invent architecture — only surfaces evidence-based implications."
    ),
)
async def analyze_prd(
    request: EngineeringAnalyzeRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    analysis = engine.analyze_prd_technical_implications(
        prd_title=request.prd_title,
        prd_entity_id=request.prd_entity_id,
        requirements=reqs,
    )

    return EngineeringAnalyzeResponse(
        prd_entity_id=analysis.prd_entity_id,
        prd_title=analysis.prd_title,
        phase=analysis.phase.value,
        architecture_impact=analysis.architecture_impact,
        total_affected_components=analysis.total_affected_components,
        total_new_components=analysis.total_new_components,
        total_dependencies=analysis.total_dependencies,
        total_risks=analysis.total_risks,
        implications=[
            TechnicalImplicationSchema(
                requirement_ref=impl.requirement_ref,
                requirement_text=impl.requirement_text,
                affected_components=impl.affected_components,
                new_components=impl.new_components,
                data_model_changes=impl.data_model_changes,
                api_changes=impl.api_changes,
                dependencies=impl.dependencies,
                risks=impl.risks,
                confidence=impl.confidence,
            )
            for impl in analysis.implications
        ],
        recommendation=analysis.recommendation,
    )


# ─── Technical Design (PRD-0009 §17) ──────────────────────────


@router.post(
    "/design",
    response_model=TechnicalDesignResponse,
    summary="Generate technical design specification",
    description=(
        "Generates a structured technical design document from PRD requirements. "
        "Includes components, data flow, API changes, failure modes, and observability."
    ),
)
async def generate_design(
    request: TechnicalDesignRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    # First analyze, then generate design
    analysis = engine.analyze_prd_technical_implications(
        prd_title=request.title,
        prd_entity_id=request.prd_entity_id,
        requirements=reqs,
    )

    design = engine.generate_technical_design(
        prd_entity_id=request.prd_entity_id,
        title=request.title,
        analysis=analysis,
        architecture_context=request.architecture_context or "",
    )

    return TechnicalDesignResponse(
        title=design.title,
        architecture_context=design.architecture_context,
        existing_system=design.existing_system,
        proposed_changes=design.proposed_changes,
        components=[ComponentSchema(name=c["name"], change_type=c["change_type"], confidence=c.get("confidence", "inferred")) for c in design.components],
        data_flow=design.data_flow,
        api_changes=design.api_changes,
        data_model=design.data_model,
        events=design.events,
        dependencies=design.dependencies,
        security_considerations=design.security_considerations,
        scalability_notes=design.scalability_notes,
        failure_modes=design.failure_modes,
        observability=design.observability,
        migration_strategy=design.migration_strategy,
        rollback_strategy=design.rollback_strategy,
        open_questions=design.open_questions,
    )


# ─── Architecture Decision Records (PRD-0009 §12, §13) ────────


@router.post(
    "/adr",
    response_model=ADRCreateResponse,
    summary="Create Architecture Decision Record",
    description=(
        "Creates and persists an ADR in the Knowledge Graph. "
        "ADRs document major technical decisions with context, "
        "alternatives, and consequences for organizational memory."
    ),
)
async def create_adr(
    request: ADRCreateRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine(db=db, workspace_id=workspace_id)

    alternatives = [
        {"name": alt.name, "description": alt.description, "pros": alt.pros, "cons": alt.cons}
        for alt in request.alternatives
    ]

    result = await engine.create_architecture_decision(
        title=request.title,
        context=request.context,
        alternatives=alternatives,
        decision=request.decision,
        consequences=request.consequences,
        rationale=request.rationale,
        related_prd_id=request.related_prd_id,
        related_initiative_id=request.related_initiative_id,
    )

    await db.commit()
    return ADRCreateResponse(**result)


# ─── Engineering Breakdown (PRD-0009 §28) ──────────────────────


@router.post(
    "/breakdown",
    response_model=BreakdownResponse,
    summary="Decompose PRD into engineering work",
    description=(
        "Breaks a PRD into Epics → Stories → Subtasks with "
        "acceptance criteria and effort estimates. "
        "Each story traces back to a specific requirement."
    ),
)
async def decompose_prd(
    request: BreakdownRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    breakdown = engine.decompose_into_epics(
        prd_entity_id=request.prd_entity_id,
        prd_title=request.prd_title,
        requirements=reqs,
    )

    return BreakdownResponse(
        prd_entity_id=breakdown.prd_entity_id,
        prd_title=breakdown.prd_title,
        epics=[
            EpicSchema(
                epic_id=e.epic_id,
                title=e.title,
                description=e.description,
                stories=[
                    StorySchema(
                        story_id=s.story_id,
                        title=s.title,
                        context=s.context,
                        requirement_ref=s.requirement_ref,
                        acceptance_criteria=s.acceptance_criteria,
                        dependencies=s.dependencies,
                        estimated_hours=s.estimated_hours,
                        estimate_confidence=s.estimate_confidence.value,
                    )
                    for s in e.stories
                ],
            )
            for e in breakdown.epics
        ],
        total_stories=breakdown.total_stories,
        total_estimated_hours=breakdown.total_estimated_hours,
        estimate_confidence=breakdown.estimate_confidence.value,
    )


# ─── Effort Estimation (PRD-0009 §22-§25) ─────────────────────


@router.post(
    "/estimate",
    response_model=EffortEstimateResponse,
    summary="Estimate effort for engineering work",
    description=(
        "Calculates effort estimates with confidence levels. "
        "Estimate = Development + Testing + Integration + Migration + Deployment + Contingency. "
        "⚠️ Estimates are labeled as estimates, never commitments."
    ),
)
async def estimate_effort(
    request: EffortEstimateRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    breakdown = engine.decompose_into_epics(
        prd_entity_id=request.prd_entity_id,
        prd_title=request.prd_title,
        requirements=reqs,
    )

    estimate = engine.estimate_effort(
        breakdown=breakdown,
        testing_multiplier=request.testing_multiplier,
        integration_multiplier=request.integration_multiplier,
        contingency_multiplier=request.contingency_multiplier,
    )

    return EffortEstimateResponse(
        development_hours=estimate.development_hours,
        testing_hours=estimate.testing_hours,
        integration_hours=estimate.integration_hours,
        migration_hours=estimate.migration_hours,
        deployment_hours=estimate.deployment_hours,
        contingency_hours=estimate.contingency_hours,
        total_hours=estimate.total_hours,
        confidence=estimate.confidence.value,
        assumptions=estimate.assumptions,
    )


# ─── Capacity Analysis (PRD-0009 §26, §27) ────────────────────


@router.post(
    "/capacity",
    response_model=CapacityResponse,
    summary="Analyze team capacity vs requirements",
    description=(
        "Compares required effort against available team capacity. "
        "Detects overload and suggests mitigation strategies."
    ),
)
async def analyze_capacity(
    request: CapacityRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    breakdown = engine.decompose_into_epics(
        prd_entity_id=request.prd_entity_id,
        prd_title=request.prd_title,
        requirements=reqs,
    )

    estimate = engine.estimate_effort(breakdown)

    capacity = engine.analyze_capacity(
        available_hours=request.available_hours,
        estimate=estimate,
    )

    return CapacityResponse(
        available_hours=capacity.available_hours,
        required_hours=capacity.required_hours,
        conflict_hours=capacity.conflict_hours,
        has_conflict=capacity.has_conflict,
        utilization_percent=capacity.utilization_percent,
        recommendations=capacity.recommendations,
    )


# ─── Technical Debt (PRD-0009 §72-§76) ────────────────────────


@router.post(
    "/tech-debt",
    response_model=TechDebtResponse,
    summary="Record technical debt",
    description=(
        "Records technical debt as a first-class entity in the Knowledge Graph. "
        "Tech debt must be connected to product/business impact — "
        "not merely labeled as debt."
    ),
)
async def record_tech_debt(
    request: TechDebtRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine(db=db, workspace_id=workspace_id)

    try:
        severity = TechDebtSeverity(request.severity.upper())
    except ValueError:
        severity = TechDebtSeverity.MEDIUM

    item = TechDebtItem(
        component=request.component,
        description=request.description,
        severity=severity,
        product_impact=request.product_impact,
        business_cost=request.business_cost,
        remediation=request.remediation,
        estimated_effort_hours=request.estimated_effort_hours,
        accumulated_since=request.accumulated_since,
    )

    result = await engine.record_tech_debt(item)
    await db.commit()
    return TechDebtResponse(**result)


# ─── Technical Risk (PRD-0009 §77-§81) ────────────────────────


@router.post(
    "/tech-risk",
    response_model=TechRiskResponse,
    summary="Record technical risk",
    description=(
        "Records a technical risk in the Knowledge Graph. "
        "Links to related initiatives where applicable."
    ),
)
async def record_tech_risk(
    request: TechRiskRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine(db=db, workspace_id=workspace_id)

    risk = TechnicalRisk(
        risk=request.risk,
        likelihood=request.likelihood,
        impact=request.impact,
        mitigation=request.mitigation,
        owner=request.owner,
        related_component=request.related_component,
    )

    result = await engine.record_technical_risk(
        risk=risk,
        related_initiative_id=request.related_initiative_id,
    )

    await db.commit()
    return TechRiskResponse(**result)


# ─── Implementation Drift Detection (PRD-0009 §52-§55) ────────


@router.get(
    "/drift/{prd_id}",
    response_model=DriftAnalysisResponse,
    summary="Detect implementation drift",
    description=(
        "Compares PRD requirements against engineering execution status. "
        "Identifies missing, incomplete, diverged, and untracked work."
    ),
)
async def detect_drift(
    prd_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine(db=db, workspace_id=workspace_id)

    drift_items = await engine.detect_implementation_drift(prd_entity_id=prd_id)

    return DriftAnalysisResponse(
        prd_entity_id=prd_id,
        total_drift_items=len(drift_items),
        drift_items=[
            DriftItemSchema(
                requirement_ref=d.requirement_ref,
                requirement_text=d.requirement_text,
                expected_status=d.expected_status,
                actual_status=d.actual_status,
                drift_type=d.drift_type,
                details=d.details,
            )
            for d in drift_items
        ],
    )


# ─── Blocker Analysis (PRD-0009 §37-§40) ──────────────────────


@router.get(
    "/blockers/{epic_id}",
    response_model=BlockerAnalysisResponse,
    summary="Analyze blockers and aging",
    description=(
        "Identifies blocked stories within an epic and calculates "
        "how long each item has been blocked (blocker aging)."
    ),
)
async def analyze_blockers(
    epic_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine(db=db, workspace_id=workspace_id)

    blockers = await engine.analyze_blockers(epic_entity_id=epic_id)

    return BlockerAnalysisResponse(
        epic_entity_id=epic_id,
        total_blockers=len(blockers),
        blockers=[
            BlockerSchema(
                blocked_entity_id=b.blocked_entity_id,
                blocked_name=b.blocked_name,
                blocking_entity_id=b.blocking_entity_id,
                blocking_name=b.blocking_name,
                blocked_since=b.blocked_since,
                age_days=b.age_days,
                severity=b.severity,
            )
            for b in blockers
        ],
    )


# ─── Engineering Handoff (PRD-0009 §89, §90) ──────────────────


@router.post(
    "/handoff",
    response_model=HandoffResponse,
    summary="Generate full engineering handoff",
    description=(
        "Generates a complete engineering handoff document combining "
        "technical analysis, engineering breakdown, effort estimates, "
        "risks, and observability requirements."
    ),
)
async def generate_handoff(
    request: HandoffRequest,
    workspace_id: str = Depends(get_workspace_id),
):
    engine = EngineeringIntelligenceEngine()
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]

    # Run full pipeline: Analyze → Breakdown → Estimate → Handoff
    analysis = engine.analyze_prd_technical_implications(
        prd_title=request.prd_title,
        prd_entity_id=request.prd_entity_id,
        requirements=reqs,
    )

    breakdown = engine.decompose_into_epics(
        prd_entity_id=request.prd_entity_id,
        prd_title=request.prd_title,
        requirements=reqs,
    )

    estimate = engine.estimate_effort(breakdown)

    handoff = engine.generate_engineering_handoff(
        prd_title=request.prd_title,
        prd_entity_id=request.prd_entity_id,
        analysis=analysis,
        breakdown=breakdown,
        estimate=estimate,
        objective=request.objective or "",
    )

    return HandoffResponse(
        initiative_name=handoff.initiative_name,
        prd_reference=handoff.prd_reference,
        objective=handoff.objective,
        architecture_impact=handoff.architecture_impact,
        affected_components=handoff.affected_components,
        new_components=handoff.new_components,
        dependencies=handoff.dependencies,
        data_model_changes=handoff.data_model_changes,
        events=handoff.events,
        observability=handoff.observability,
        rollback_strategy=handoff.rollback_strategy,
        epics=handoff.epics,
        total_stories=handoff.total_stories,
        total_estimated_hours=handoff.total_estimated_hours,
        estimate_confidence=handoff.estimate_confidence,
        risks=handoff.risks,
        open_questions=handoff.open_questions,
    )
