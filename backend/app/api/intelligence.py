"""
Intelligence API — PRD-0002, PRD-0005, PRD-0006

Exposes TPG's core product reasoning capabilities:
1. Requirement Intelligence (Ambiguity analysis, question prioritization, JTBD)
2. Decision Intelligence (Trade-off matrix, ADR formulation, decision governance)
3. Graph Intelligence (Multi-stage retrieval, lineage tracing, pathfinding)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.models.entity import EntityType
from app.schemas import (
    RequirementAnalyzeRequest,
    RequirementAnalyzeResponse,
    DiscoveryQuestionSchema,
    JTBDSchema,
    RequirementIngestRequest,
    RequirementIngestResponse,
    DecisionEvaluateRequest,
    DecisionEvaluateResponse,
    RankedOptionResponse,
    DecisionRecordRequest,
    DecisionRecordResponse,
    MultiStageGraphQueryRequest,
    MultiStageGraphQueryResponse,
    EvidenceItemSchema,
    LineageTraceResponse,
    ShortestPathResponse,
    PRDAssessRequest,
    PRDAssessResponse,
    PRDGenerateRequest,
    PRDGenerateResponse,
    PRDSaveResponse,
)
from app.models.entity import Entity
from app.services.requirement_engine import (
    RequirementIntelligenceEngine,
)
from app.services.decision_engine import (
    ProductDecisionEngine,
    DecisionType,
    DecisionOutcome,
    SolutionOption,
)
from app.services.prd_engine import (
    PRDSpecificationEngine,
)
from app.graph.retrieval import GraphRetrievalEngine
from app.graph.traversal import GraphTraversalEngine


router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


# ─── Requirement Intelligence (PRD-0005) ──────────────────────

@router.post("/requirements/analyze", response_model=RequirementAnalyzeResponse)
async def analyze_requirement(
    request: RequirementAnalyzeRequest,
):
    """
    Analyzes a requirement or problem description for ambiguity.
    Identifies missing dimensions, scores completeness, and generates
    prioritized discovery questions according to PRD-0005 §9.
    """
    engine = RequirementIntelligenceEngine()
    analysis = engine.analyze_ambiguity(request.statement, context=request.context)

    return RequirementAnalyzeResponse(
        is_product_requirement=analysis.is_product_requirement,
        detected_type=analysis.detected_type.value,
        ambiguity_score=analysis.ambiguity_score,
        completeness_score=analysis.completeness_score,
        missing_dimensions=analysis.missing_dimensions,
        prioritized_questions=[
            DiscoveryQuestionSchema(
                priority=q.priority,
                dimension=q.dimension,
                question=q.question,
                rationale=q.rationale,
            )
            for q in analysis.prioritized_questions
        ],
        suggested_jtbd=[
            JTBDSchema(
                situation=j.situation,
                motivation=j.motivation,
                expected_outcome=j.expected_outcome,
            )
            for j in analysis.suggested_jtbd
        ],
    )


@router.post("/requirements/ingest", response_model=RequirementIngestResponse)
async def ingest_requirement(
    request: RequirementIngestRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingests a requirement into the Knowledge Graph with provenance tracking.
    """
    engine = RequirementIntelligenceEngine(db=db, workspace_id=workspace_id)
    res = await engine.ingest_requirement(
        raw_text=request.raw_text,
        title=request.title,
        initiative_id=request.initiative_id,
        source=request.source,
        source_reference=request.source_reference,
    )
    return RequirementIngestResponse(
        entity_id=res["entity_id"],
        entity_type=res["entity_type"],
        title=res["title"],
        ambiguity_score=res["ambiguity_score"],
        discovery_state=res["discovery_state"],
        next_questions=res["next_questions"],
    )


# ─── Decision Intelligence (PRD-0006) ─────────────────────────

@router.post("/decisions/evaluate", response_model=DecisionEvaluateResponse)
async def evaluate_decision_options(
    request: DecisionEvaluateRequest,
):
    """
    Evaluates competing solution options across Effort, Impact, Risk, and Confidence.
    Generates quantitative efficiency scores and trade-off comparisons.
    """
    engine = ProductDecisionEngine()
    options = [
        SolutionOption(
            name=o.name,
            description=o.description,
            pros=o.pros,
            cons=o.cons,
            effort=o.effort,
            impact=o.impact,
            risk=o.risk,
            confidence=o.confidence,
        )
        for o in request.options
    ]
    ranked = engine.evaluate_tradeoffs(options)

    ranked_responses = [
        RankedOptionResponse(
            name=opt.name,
            score=score,
            analysis=analysis,
        )
        for opt, score, analysis in ranked
    ]

    top_name = ranked[0][0].name if ranked else "No options provided"
    tradeoffs = [
        f"Option '{opt.name}' scored {score} vs '{ranked[0][0].name}' ({ranked[0][1]})"
        for opt, score, _ in ranked[1:]
    ]

    return DecisionEvaluateResponse(
        decision_question=request.decision_question,
        top_recommendation=f"Recommended: {top_name}",
        ranked_options=ranked_responses,
        tradeoffs=tradeoffs,
    )


@router.post("/decisions/record", response_model=DecisionRecordResponse)
async def record_decision(
    request: DecisionRecordRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Formulates a permanent ADR (Decision Record) and stores it in the Knowledge Graph.
    """
    engine = ProductDecisionEngine(db=db, workspace_id=workspace_id)
    options = [
        SolutionOption(
            name=o.name,
            description=o.description,
            pros=o.pros,
            cons=o.cons,
            effort=o.effort,
            impact=o.impact,
            risk=o.risk,
            confidence=o.confidence,
        )
        for o in request.options
    ]

    record = engine.formulate_decision(
        title=request.title,
        decision_type=DecisionType(request.decision_type),
        outcome=DecisionOutcome(request.outcome),
        decision_question=request.decision_question,
        context=request.context,
        rationale=request.rationale,
        options=options,
        evidence_citations=request.evidence_citations,
        risks=request.risks,
        expected_outcomes=request.expected_outcomes,
    )

    res = await engine.record_decision(
        record=record,
        initiative_id=request.initiative_id,
        problem_id=request.problem_id,
        requirement_id=request.requirement_id,
    )

    return DecisionRecordResponse(
        decision_id=res["decision_id"],
        title=res["title"],
        outcome=res["outcome"],
        confidence=res["confidence"],
        tradeoffs_count=res["tradeoffs_count"],
    )


# ─── Graph Intelligence (PRD-0002 §9) ─────────────────────────

@router.post("/graph/query", response_model=MultiStageGraphQueryResponse)
async def graph_query(
    request: MultiStageGraphQueryRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Multi-stage graph retrieval engine.
    Answers natural questions like:
    - 'Why did we build Vendor Wallet?'
    - 'What is blocking the Mobile MVP?'
    - 'Trace the provenance of initiative X'
    """
    retrieval_engine = GraphRetrievalEngine(db=db, workspace_id=workspace_id)
    ent_type = EntityType(request.entity_type) if request.entity_type else None

    res = await retrieval_engine.retrieve(
        query=request.query,
        entity_id=request.entity_id,
        entity_type=ent_type,
    )

    evidence_schemas = [
        EvidenceItemSchema(
            entity_id=e.entity_id,
            entity_type=e.entity_type,
            name=e.name,
            relationship=e.relationship,
            source=e.source,
            confidence=e.confidence,
        )
        for e in res.evidence
    ]

    return MultiStageGraphQueryResponse(
        query=res.query,
        intent=res.intent.value,
        narrative_summary=res.narrative_summary,
        evidence=evidence_schemas,
        total_nodes=len(res.subgraph_nodes),
        total_edges=len(res.subgraph_edges),
        confidence=res.confidence,
    )


@router.get("/graph/lineage/{entity_id}", response_model=LineageTraceResponse)
async def trace_lineage(
    entity_id: str,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Reconstructs the full upstream and downstream provenance tree of an entity.
    """
    traversal_engine = GraphTraversalEngine(db=db, workspace_id=workspace_id)
    lineage = await traversal_engine.trace_lineage(entity_id=entity_id)
    if not lineage:
        raise HTTPException(status_code=404, detail="Entity not found in workspace.")

    return LineageTraceResponse(
        entity_id=lineage.entity_id,
        root_name=lineage.root_entity.name,
        root_type=lineage.root_entity.entity_type,
        upstream_count=len(lineage.upstream_nodes),
        downstream_count=len(lineage.downstream_nodes),
        provenance_chain=lineage.provenance_chain,
    )


@router.get("/graph/path", response_model=ShortestPathResponse)
async def shortest_path(
    source_id: str = Query(...),
    target_id: str = Query(...),
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Finds the shortest relationship path between two entities in the workspace.
    """
    traversal_engine = GraphTraversalEngine(db=db, workspace_id=workspace_id)
    res = await traversal_engine.find_shortest_path(source_id=source_id, target_id=target_id)

    path_names = [n.name for n in res.nodes]

    return ShortestPathResponse(
        source_id=source_id,
        target_id=target_id,
        path_found=res.path_found,
        distance=res.distance,
        path_names=path_names,
    )


# ─── PRD & Product Specification (PRD-0008) ────────────────────

@router.post("/prd/assess", response_model=PRDAssessResponse)
async def assess_prd_readiness(
    request: PRDAssessRequest,
):
    """
    Evaluates PRD readiness before drafting (PRD-0008 §7, §8, §9).
    Prevents blind PRD generation without validated problem and decisions.
    """
    engine = PRDSpecificationEngine()
    assessment = engine.assess_readiness(
        problem=request.problem,
        requirements=request.requirements,
        decision_rationale=request.decision_rationale,
        evidence=request.evidence,
        success_metric=request.success_metric,
    )
    return PRDAssessResponse(
        level=assessment.level.value,
        overall_score=assessment.overall_score,
        dimension_scores=assessment.dimension_scores,
        missing_critical_items=assessment.missing_critical_items,
        readiness_notes=assessment.readiness_notes,
    )


@router.post("/prd/generate", response_model=PRDGenerateResponse)
async def generate_prd_specification(
    request: PRDGenerateRequest,
):
    """
    Synthesizes a complete, constitutional PRD conforming to PRD-0008 §10.
    Enforces scope fencing (non-goals), functional requirements, and Gherkin acceptance criteria.
    """
    engine = PRDSpecificationEngine()
    prd_doc = engine.generate_prd(
        title=request.title,
        problem=request.problem,
        raw_requirements=request.raw_requirements,
        decision_rationale=request.decision_rationale,
        evidence=request.evidence,
        target_personas=request.target_personas,
        non_goals=request.non_goals,
        success_metric=request.success_metric,
        initiative_id=request.initiative_id,
        decision_id=request.decision_id,
    )
    md = engine.render_markdown(prd_doc)

    return PRDGenerateResponse(
        title=prd_doc.title,
        version=prd_doc.version,
        status=prd_doc.status.value,
        executive_summary=prd_doc.executive_summary,
        goals=prd_doc.goals,
        non_goals=prd_doc.non_goals,
        functional_requirements_count=len(prd_doc.functional_requirements),
        acceptance_criteria_count=len(prd_doc.acceptance_criteria),
        markdown=md,
    )


@router.post("/prd/save", response_model=PRDSaveResponse)
async def save_prd_specification(
    request: PRDGenerateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Drafts and permanently saves an immutable PRD in the Knowledge Graph with version management.
    """
    engine = PRDSpecificationEngine(db=db, workspace_id=workspace_id)
    prd_doc = engine.generate_prd(
        title=request.title,
        problem=request.problem,
        raw_requirements=request.raw_requirements,
        decision_rationale=request.decision_rationale,
        evidence=request.evidence,
        target_personas=request.target_personas,
        non_goals=request.non_goals,
        success_metric=request.success_metric,
        initiative_id=request.initiative_id,
        decision_id=request.decision_id,
    )
    res = await engine.save_prd(prd_doc)

    return PRDSaveResponse(
        prd_id=res["prd_id"],
        title=res["title"],
        version=res["version"],
        status=res["status"],
        markdown_length=res["markdown_length"],
    )


@router.get("/prd/{prd_id}")
async def get_prd_specification(
    prd_id: str,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a saved PRD from the Knowledge Graph by its ID.
    """
    stmt = (
        select(Entity)
        .where(Entity.id == prd_id)
        .where(Entity.workspace_id == workspace_id)
        .where(Entity.entity_type == EntityType.PRD)
    )
    res = await db.execute(stmt)
    entity = res.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="PRD not found in workspace.")

    return {
        "prd_id": entity.id,
        "title": entity.name,
        "problem_statement": entity.description,
        "version": entity.version,
        "status": entity.properties.get("status", "DRAFT"),
        "non_goals": entity.properties.get("non_goals", []),
        "goals": entity.properties.get("goals", []),
        "markdown": entity.properties.get("markdown", ""),
    }

