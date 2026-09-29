"""
Customer Intelligence API — PRD-0012

Exposes TPG's customer intelligence capabilities:
1. Ingest Customer Signal
2. Classify Signal
3. Extract Problem
4. Estimate Impact
5. Detect Patterns
6. Extract Opportunity
7. Analyze Churn Risk
8. Evaluate Feature Request
9. Journey Insight
10. Account Summary
11. Traceability
12. Extract Learning
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.schemas import (
    SignalIngestRequest, SignalIngestResponse,
    ProblemExtractRequest, ProblemExtractResponse,
    ImpactEstimateRequest, ImpactEstimateResponse,
    OpportunityExtractRequest, OpportunityExtractResponse,
    ChurnRiskRequest, ChurnRiskResponse,
    FeatureEvalRequest, FeatureEvalResponse,
    AccountSummaryRequest, AccountSummaryResponse,
    TraceRequest, TraceResponse,
)
from app.services.customer_engine import (
    CustomerIntelligenceEngine,
    CustomerSignal,
    CustomerProblem,
    SignalType,
    UrgencyLevel,
    Sentiment,
)

router = APIRouter(prefix="/customer", tags=["Customer Intelligence"])


@router.post("/signals", response_model=SignalIngestResponse)
async def ingest_signal(request: SignalIngestRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    signal = engine.ingest_signal(
        customer_id=request.customer_id,
        source=request.source,
        source_reference=request.source_reference,
        raw_text=request.raw_text,
    )
    return SignalIngestResponse(
        workspace_id=signal.workspace_id,
        customer_id=signal.customer_id,
        source=signal.source,
        source_reference=signal.source_reference,
        signal_type=signal.signal_type.value,
        summary=signal.summary,
        urgency=signal.urgency.value,
        sentiment=signal.sentiment.value,
    )


@router.post("/signals/classify")
async def classify_signal(text: str, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    signal_type = engine.classify_signal(text)
    return {"signal_type": signal_type.value}


@router.post("/problems/extract", response_model=ProblemExtractResponse)
async def extract_problem(request: ProblemExtractRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    sig_dict = request.signal.dict()
    sig = CustomerSignal(
        workspace_id=sig_dict["workspace_id"],
        customer_id=sig_dict["customer_id"],
        source=sig_dict["source"],
        source_reference=sig_dict["source_reference"],
        signal_type=SignalType(sig_dict["signal_type"]),
        summary=sig_dict["summary"],
        raw_claim="",
        urgency=UrgencyLevel(sig_dict["urgency"]),
        sentiment=Sentiment(sig_dict["sentiment"])
    )
    problem = engine.extract_problem(sig)
    return ProblemExtractResponse(**problem.__dict__)


@router.post("/impact/estimate", response_model=ImpactEstimateResponse)
async def estimate_impact(request: ImpactEstimateRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    prob_dict = request.problem.dict()
    prob = CustomerProblem(
        signal_id=prob_dict["signal_id"],
        problem_statement=prob_dict["problem_statement"],
        affected_workflow=prob_dict["affected_workflow"],
        frequency=prob_dict["frequency"],
        workaround_exists=prob_dict["workaround_exists"]
    )
    impact = engine.estimate_impact(prob)
    return ImpactEstimateResponse(
        problem_statement=impact.problem_statement,
        time_impact=impact.time_impact,
        cost_impact=impact.cost_impact,
        revenue_impact=impact.revenue_impact,
        user_frustration=impact.user_frustration,
        severity=impact.severity.value,
    )


@router.get("/patterns/{problem_id}")
async def detect_pattern(problem_id: str, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    # Stub using empty list for demonstration
    patterns = engine.detect_pattern([])
    return {"patterns": patterns}


@router.post("/opportunities/extract", response_model=OpportunityExtractResponse)
async def extract_opportunity(request: OpportunityExtractRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    prob_dict = request.problem.dict()
    prob = CustomerProblem(
        signal_id=prob_dict["signal_id"],
        problem_statement=prob_dict["problem_statement"],
        affected_workflow=prob_dict["affected_workflow"],
        frequency=prob_dict["frequency"],
        workaround_exists=prob_dict["workaround_exists"]
    )
    opp = engine.extract_opportunity(prob)
    return OpportunityExtractResponse(
        problem_statement=opp.problem_statement,
        potential_opportunity=opp.potential_opportunity,
        strategic_alignment=opp.strategic_alignment,
        confidence=opp.confidence.value,
    )


@router.post("/churn-risk/analyze", response_model=ChurnRiskResponse)
async def analyze_churn_risk(request: ChurnRiskRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    signals = []
    for sig in request.signals:
        s_dict = sig.dict()
        signals.append(CustomerSignal(
            workspace_id=s_dict["workspace_id"],
            customer_id=s_dict["customer_id"],
            source=s_dict["source"],
            source_reference=s_dict["source_reference"],
            signal_type=SignalType(s_dict["signal_type"]),
            summary=s_dict["summary"],
            raw_claim="",
            urgency=UrgencyLevel(s_dict["urgency"]),
            sentiment=Sentiment(s_dict["sentiment"])
        ))
    
    risk = engine.analyze_churn_risk(signals)
    return ChurnRiskResponse(
        customer_id=risk.customer_id,
        risk_level=risk.risk_level.value,
        primary_reason=risk.primary_reason,
        contributing_factors=risk.contributing_factors,
        recommended_action=risk.recommended_action,
    )


@router.post("/feature-requests/evaluate", response_model=FeatureEvalResponse)
async def evaluate_feature_request(request: FeatureEvalRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    eval_res = engine.evaluate_feature_request(request.raw_request)
    return FeatureEvalResponse(**eval_res.__dict__)


@router.get("/journey/insight")
async def get_journey_insight(customer_id: str, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    insight = engine.generate_customer_journey_insight(customer_id)
    return {"insight": insight}


@router.post("/accounts/summary", response_model=AccountSummaryResponse)
async def summarize_account(request: AccountSummaryRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    signals = []
    for sig in request.signals:
        s_dict = sig.dict()
        signals.append(CustomerSignal(
            workspace_id=s_dict["workspace_id"],
            customer_id=s_dict["customer_id"],
            source=s_dict["source"],
            source_reference=s_dict["source_reference"],
            signal_type=SignalType(s_dict["signal_type"]),
            summary=s_dict["summary"],
            raw_claim="",
            urgency=UrgencyLevel(s_dict["urgency"]),
            sentiment=Sentiment(s_dict["sentiment"])
        ))
    summary = engine.summarize_account(request.account_id, signals)
    return AccountSummaryResponse(
        account_id=summary.account_id,
        total_signals=summary.total_signals,
        primary_problems=summary.primary_problems,
        overall_sentiment=summary.overall_sentiment.value,
        churn_risk=summary.churn_risk.value,
    )


@router.get("/trace/{customer_id}", response_model=TraceResponse)
async def get_traceability(customer_id: str, workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    trace = engine.trace_customer_to_product(customer_id)
    return TraceResponse(**trace.__dict__)


@router.post("/learnings/extract")
async def extract_learning(workspace_id: str = Depends(get_workspace_id)):
    engine = CustomerIntelligenceEngine(workspace_id=workspace_id)
    learning = engine.extract_learning_from_feedback([])
    return {"learning": learning}
