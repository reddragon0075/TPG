"""
Analytics & Outcome Intelligence API — PRD-0011

Exposes TPG's analytics and outcome intelligence capabilities:
1. Define KPI
2. Define Event
3. Generate Instrumentation Requirements
4. Generate Outcome Hypothesis
5. Define Experiment
6. Evaluate Experiment
7. Analyze Funnel
8. Analyze Retention
9. Evaluate Feature Adoption
10. Detect Metric Anomaly
11. Correlate Product Change
12. Evaluate Outcome Scorecard
13. Extract Strategic Learning
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.schemas import (
    KPIRequest, KPIResponse,
    EventRequest, EventResponse,
    InstrumentationRequest, InstrumentationResponse,
    OutcomeHypothesisRequest, OutcomeHypothesisResponse,
    ExperimentRequest, ExperimentResponse,
    ExperimentEvalRequest, ExperimentEvalResponse,
    FunnelRequest, FunnelResponse,
    RetentionRequest, RetentionResponse,
    FeatureAdoptionRequest, FeatureAdoptionResponse,
    AnomalyRequest, AnomalyResponse,
    CorrelationRequest, CorrelationResponse,
    ScorecardRequest, ScorecardResponse,
    StrategicLearningResponse,
)
from app.services.analytics_engine import (
    AnalyticsIntelligenceEngine,
    ExperimentEvaluation,
    ExperimentDecision,
)
from app.models.entity import ConfidenceLevel

router = APIRouter(prefix="/analytics", tags=["Analytics & Outcome Intelligence"])


@router.post("/kpi", response_model=KPIResponse)
async def define_kpi(request: KPIRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    kpi = engine.define_kpi(
        name=request.name,
        description=request.description,
        formula=request.formula,
        unit=request.unit,
        baseline=request.baseline,
        target=request.target,
        measurement_period=request.measurement_period,
    )
    return KPIResponse(
        name=kpi.name,
        description=kpi.description,
        formula=kpi.formula,
        unit=kpi.unit,
        baseline=kpi.baseline,
        target=kpi.target,
        measurement_period=kpi.measurement_period,
        status=kpi.status.value,
    )


@router.post("/event", response_model=EventResponse)
async def define_event(request: EventRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    event = engine.define_event(
        name=request.name,
        description=request.description,
        trigger=request.trigger,
        properties=request.properties,
        required_properties=request.required_properties,
        source=request.source,
    )
    return EventResponse(**event.__dict__)


@router.post("/instrumentation", response_model=InstrumentationResponse)
async def generate_instrumentation(request: InstrumentationRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    reqs = [{"id": r.id, "text": r.text} for r in request.requirements]
    instr = engine.generate_instrumentation_requirements(
        prd_entity_id=request.prd_entity_id,
        requirements=reqs,
    )
    return InstrumentationResponse(
        prd_entity_id=instr.prd_entity_id,
        events=[EventResponse(**e.__dict__) for e in instr.events],
        identity_rules=instr.identity_rules,
        deduplication_rules=instr.deduplication_rules,
        acceptance_criteria=instr.acceptance_criteria,
    )


@router.post("/hypothesis", response_model=OutcomeHypothesisResponse)
async def generate_hypothesis(request: OutcomeHypothesisRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    hyp = engine.generate_outcome_hypothesis(
        initiative_name=request.initiative_name,
        action=request.action,
        target_segment=request.target_segment,
        expected_behavior_change=request.expected_behavior_change,
        expected_outcome=request.expected_outcome,
        primary_metric=request.primary_metric,
        guardrails=request.guardrails,
    )
    return OutcomeHypothesisResponse(**hyp.__dict__)


@router.post("/experiment", response_model=ExperimentResponse)
async def define_experiment(request: ExperimentRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    # Convert response back to dataclass
    hyp_dict = request.hypothesis.dict()
    from app.services.analytics_engine import OutcomeHypothesis
    hyp = OutcomeHypothesis(**hyp_dict)
    
    exp = engine.define_experiment(
        hypothesis=hyp,
        min_sample_size=request.min_sample_size,
        duration_days=request.duration_days,
    )
    return ExperimentResponse(
        hypothesis=request.hypothesis,
        target_population=exp.target_population,
        control_variant=exp.control_variant,
        treatment_variant=exp.treatment_variant,
        primary_metric=exp.primary_metric,
        secondary_metrics=exp.secondary_metrics,
        guardrails=exp.guardrails,
        min_sample_size=exp.min_sample_size,
        duration_days=exp.duration_days,
        success_criteria=exp.success_criteria,
    )


@router.post("/experiment/evaluate", response_model=ExperimentEvalResponse)
async def evaluate_experiment(request: ExperimentEvalRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    eval = engine.evaluate_experiment(
        experiment_id=request.experiment_id,
        control_value=request.control_value,
        treatment_value=request.treatment_value,
        is_statistically_significant=request.is_statistically_significant,
        guardrails_passed=request.guardrails_passed,
    )
    return ExperimentEvalResponse(
        experiment_id=eval.experiment_id,
        observed_effect=eval.observed_effect,
        statistical_significance=eval.statistical_significance,
        confidence_level=eval.confidence_level.value,
        guardrails_ok=eval.guardrails_ok,
        decision=eval.decision.value,
        reasoning=eval.reasoning,
        learning=eval.learning,
    )


@router.post("/funnel", response_model=FunnelResponse)
async def analyze_funnel(request: FunnelRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    funnel = engine.analyze_funnel(steps=request.steps, users_at_steps=request.users_at_steps)
    return FunnelResponse(**funnel.__dict__)


@router.post("/retention", response_model=RetentionResponse)
async def analyze_retention(request: RetentionRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    retention = engine.analyze_retention(
        cohort_name=request.cohort_name,
        d1_rate=request.d1_rate,
        d7_rate=request.d7_rate,
        d30_rate=request.d30_rate,
    )
    return RetentionResponse(**retention.__dict__)


@router.post("/feature-adoption", response_model=FeatureAdoptionResponse)
async def evaluate_feature_adoption(request: FeatureAdoptionRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    adoption = engine.evaluate_feature_adoption(
        feature_name=request.feature_name,
        eligible=request.eligible_users,
        exposed=request.exposed_users,
        tried=request.tried_users,
        retained=request.retained_users,
    )
    return FeatureAdoptionResponse(
        feature_name=adoption.feature_name,
        eligible_users=adoption.eligible_users,
        exposed_users=adoption.exposed_users,
        tried_users=adoption.tried_users,
        retained_users=adoption.retained_users,
        adoption_rate=adoption.adoption_rate,
        primary_state=adoption.primary_state.value,
        recommendation=adoption.recommendation,
    )


@router.post("/anomaly", response_model=AnomalyResponse)
async def detect_anomaly(request: AnomalyRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    anomaly = engine.detect_metric_anomaly(
        metric_name=request.metric_name,
        baseline_value=request.baseline_value,
        observed_value=request.observed_value,
    )
    return AnomalyResponse(**anomaly.__dict__)


@router.post("/correlation", response_model=CorrelationResponse)
async def correlate_change(request: CorrelationRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    
    # Reconstruct anomaly dataclass
    from app.services.analytics_engine import AnomalyDetection
    anom_dict = request.anomaly.dict()
    anomaly = AnomalyDetection(**anom_dict)
    
    corr = engine.correlate_product_change(anomaly=anomaly, recent_releases=request.recent_releases)
    return CorrelationResponse(
        anomaly=request.anomaly,
        recent_releases=corr.recent_releases,
        correlation_strength=corr.correlation_strength,
        investigation_steps=corr.investigation_steps,
    )


@router.post("/scorecard", response_model=ScorecardResponse)
async def evaluate_scorecard(request: ScorecardRequest, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    scorecard = engine.evaluate_outcome_scorecard(
        initiative_name=request.initiative_name,
        baseline=request.baseline,
        target=request.target,
        current=request.current,
        guardrail_violations=request.guardrail_violations,
    )
    return ScorecardResponse(
        initiative_name=scorecard.initiative_name,
        baseline=scorecard.baseline,
        target=scorecard.target,
        current=scorecard.current,
        progress_pct=scorecard.progress_pct,
        status=scorecard.status.value,
        guardrail_status=scorecard.guardrail_status,
        recommendation=scorecard.recommendation,
    )


@router.post("/learning", response_model=StrategicLearningResponse)
async def extract_learning(request: ExperimentEvalResponse, workspace_id: str = Depends(get_workspace_id)):
    engine = AnalyticsIntelligenceEngine(workspace_id=workspace_id)
    
    # Reconstruct
    eval_dc = ExperimentEvaluation(
        experiment_id=request.experiment_id,
        observed_effect=request.observed_effect,
        statistical_significance=request.statistical_significance,
        confidence_level=ConfidenceLevel(request.confidence_level),
        guardrails_ok=request.guardrails_ok,
        decision=ExperimentDecision(request.decision),
        reasoning=request.reasoning,
        learning=request.learning,
    )
    
    learning = engine.extract_strategic_learning(eval_dc)
    return StrategicLearningResponse(
        source=learning.source,
        learning=learning.learning,
        confidence=learning.confidence.value,
        affected_decisions=learning.affected_decisions,
    )
