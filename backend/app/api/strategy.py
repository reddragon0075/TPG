"""
Strategy & Roadmap Intelligence API — PRD-0007

Endpoints:
- POST /strategy/themes: Create and store strategic theme
- POST /strategy/objectives: Create and store strategic objective
- POST /strategy/bets: Formulate strategic bet
- POST /strategy/bets/evaluate: Evaluate strategic bet viability
- POST /strategy/assumptions: Register strategic assumption
- POST /strategy/align: Score initiative alignment to strategy
- POST /strategy/roadmap: Generate Now / Next / Later living roadmap
- POST /strategy/drift: Detect execution drift from strategy
- POST /strategy/portfolio-balance: Analyze portfolio allocation & risk
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.services.strategy_engine import (
    StrategyIntelligenceEngine,
    StrategicThemeData,
    StrategicObjectiveData,
    StrategicBetData,
    StrategicAssumptionData,
    TimeHorizon,
    ObjectiveType,
    BetLifecycleStatus,
    AssumptionStatus,
)
from app.schemas import (
    ThemeCreateRequest,
    ThemeResponse,
    ObjectiveCreateRequest,
    ObjectiveResponse,
    StrategicBetCreateRequest,
    StrategicBetResponse,
    BetEvaluateRequest,
    BetEvaluateResponse,
    AssumptionCreateRequest,
    AssumptionResponse,
    StrategicAlignRequest,
    StrategicAlignResponse,
    RoadmapGenerateRequest,
    RoadmapResponse,
    StrategicDriftRequest,
    StrategicDriftResponse,
    PortfolioBalanceRequest,
    PortfolioBalanceResponse,
)

router = APIRouter(prefix="/strategy", tags=["Strategy & Roadmap"])


@router.post("/themes", response_model=ThemeResponse)
async def create_strategic_theme(
    request: ThemeCreateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Creates a strategic theme in the Knowledge Graph."""
    engine = StrategyIntelligenceEngine(db=db, workspace_id=workspace_id)
    data = StrategicThemeData(
        name=request.name,
        description=request.description,
        priority=request.priority,
        time_horizon=TimeHorizon(request.time_horizon) if request.time_horizon in [e.value for e in TimeHorizon] else TimeHorizon.MEDIUM_6_12_MONTHS,
        success_metrics=request.success_metrics,
    )
    res = await engine.create_theme(data)
    return ThemeResponse(**res)


@router.post("/objectives", response_model=ObjectiveResponse)
async def create_strategic_objective(
    request: ObjectiveCreateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Creates a measurable strategic objective linked to a theme."""
    engine = StrategyIntelligenceEngine(db=db, workspace_id=workspace_id)
    obj_type = ObjectiveType(request.objective_type) if request.objective_type in [e.value for e in ObjectiveType] else ObjectiveType.GROWTH
    data = StrategicObjectiveData(
        name=request.name,
        theme_id=request.theme_id,
        objective_type=obj_type,
        description=request.description,
        baseline=request.baseline,
        target=request.target,
        unit=request.unit,
        deadline=request.deadline,
        owner=request.owner,
    )
    res = await engine.create_objective(data)
    return ObjectiveResponse(**res)


@router.post("/bets", response_model=StrategicBetResponse)
async def create_strategic_bet(
    request: StrategicBetCreateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Formulates and records a strategic bet hypothesis."""
    engine = StrategyIntelligenceEngine(db=db, workspace_id=workspace_id)
    bet_status = BetLifecycleStatus(request.status) if request.status in [e.value for e in BetLifecycleStatus] else BetLifecycleStatus.HYPOTHESIS
    data = StrategicBetData(
        name=request.name,
        hypothesis=request.hypothesis,
        strategic_theme_id=request.strategic_theme_id,
        expected_outcomes=request.expected_outcomes,
        investment_size=request.investment_size,
        assumptions=request.assumptions,
        risks=request.risks,
        confidence=request.confidence,
        status=bet_status,
    )
    res = await engine.create_bet(data)
    return StrategicBetResponse(**res)


@router.post("/bets/evaluate", response_model=BetEvaluateResponse)
async def evaluate_strategic_bet(
    request: BetEvaluateRequest,
):
    """Evaluates the viability of a strategic bet."""
    engine = StrategyIntelligenceEngine()
    res = engine.evaluate_bet(
        name=request.name,
        hypothesis=request.hypothesis,
        evidence_strength=request.evidence_strength,
        investment_size=request.investment_size,
        market_uncertainty=request.market_uncertainty,
    )
    return BetEvaluateResponse(**res)


@router.post("/assumptions", response_model=AssumptionResponse)
async def record_strategic_assumption(
    request: AssumptionCreateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Registers an assumption in the Strategic Assumption Register."""
    engine = StrategyIntelligenceEngine(db=db, workspace_id=workspace_id)
    data = StrategicAssumptionData(
        statement=request.statement,
        category=request.category,
        confidence=request.confidence,
        validation_criteria=request.validation_criteria,
    )
    res = await engine.record_assumption(data)
    return AssumptionResponse(**res)


@router.post("/align", response_model=StrategicAlignResponse)
async def score_initiative_alignment(
    request: StrategicAlignRequest,
):
    """Scores strategic alignment of an initiative (0-100)."""
    engine = StrategyIntelligenceEngine()
    res = engine.score_strategic_alignment(
        initiative_name=request.initiative_name,
        problem_statement=request.problem_statement,
        linked_theme=request.linked_theme,
        linked_objective=request.linked_objective,
        has_validated_evidence=request.has_validated_evidence,
    )
    return StrategicAlignResponse(**res)


@router.post("/roadmap", response_model=RoadmapResponse)
async def generate_living_roadmap(
    request: RoadmapGenerateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Sequences initiatives into living Now/Next/Later roadmap horizons."""
    engine = StrategyIntelligenceEngine(db=db, workspace_id=workspace_id)
    inits = [i.model_dump() for i in request.initiatives] if request.initiatives else None
    res = await engine.generate_roadmap(initiatives=inits)
    return RoadmapResponse(**res)


@router.post("/drift", response_model=StrategicDriftResponse)
async def detect_strategic_drift(
    request: StrategicDriftRequest,
):
    """Detects execution drift where active work diverges from declared themes."""
    engine = StrategyIntelligenceEngine()
    inits = [i.model_dump() for i in request.initiatives]
    res = engine.detect_strategic_drift(initiatives=inits, active_themes=request.active_themes)
    return StrategicDriftResponse(**res)


@router.post("/portfolio-balance", response_model=PortfolioBalanceResponse)
async def analyze_portfolio_balance(
    request: PortfolioBalanceRequest,
):
    """Analyzes portfolio investment balance across Growth, Retention, Efficiency, Tech Debt, Compliance."""
    engine = StrategyIntelligenceEngine()
    res = engine.analyze_portfolio_balance(allocations=request.allocations)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return PortfolioBalanceResponse(**res)
