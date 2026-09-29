"""
Analytics & Outcome Intelligence Engine (AOIE) — PRD-0011

Implements:
1. KPI & Metric Definition (PRD-0011 §6-§11)
2. Event Definition (PRD-0011 §17-§20)
3. Instrumentation Requirements Generation (PRD-0011 §21)
4. Outcome Hypothesis Generation (PRD-0011 §29-§30)
5. Experiment Definition (PRD-0011 §31-§35)
6. Experiment Evaluation & Learning (PRD-0011 §42-§45)
7. Funnel Analysis (PRD-0011 §46-§48)
8. Retention Analysis (PRD-0011 §50-§55)
9. Feature Adoption Evaluation (PRD-0011 §51-§52)
10. Metric Anomaly Detection (PRD-0011 §63-§65)
11. Product Change Correlation (PRD-0011 §66-§67)
12. Outcome Scorecard Evaluation (PRD-0011 §68-§70)
13. Strategic Learning Extraction (PRD-0011 §71-§76)

Constitutional Principle:
- TPG optimizes for outcomes, not shipped features.
- Evidence before opinion.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import (
    Entity,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
)


# ─── Enums ─────────────────────────────────────────────────────────

class MetricStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUPERSEDED = "SUPERSEDED"
    INVALID = "INVALID"


class ExperimentStatus(str, Enum):
    IDEA = "IDEA"
    HYPOTHESIS = "HYPOTHESIS"
    DESIGN = "DESIGN"
    INSTRUMENTATION = "INSTRUMENTATION"
    READY = "READY"
    RUNNING = "RUNNING"
    ANALYSIS = "ANALYSIS"
    DECISION = "DECISION"
    LEARNING = "LEARNING"
    CANCELLED = "CANCELLED"
    INCONCLUSIVE = "INCONCLUSIVE"
    INVALID = "INVALID"


class ExperimentDecision(str, Enum):
    SHIP = "SHIP"
    ITERATE = "ITERATE"
    EXTEND = "EXTEND"
    ROLLBACK = "ROLLBACK"
    ABANDON = "ABANDON"
    INCONCLUSIVE = "INCONCLUSIVE"


class FeatureAdoptionState(str, Enum):
    NOT_EXPOSED = "NOT_EXPOSED"
    EXPOSED = "EXPOSED"
    TRIED = "TRIED"
    ADOPTED = "ADOPTED"
    REPEATED = "REPEATED"
    RETAINED = "RETAINED"
    ABANDONED = "ABANDONED"


class OutcomeStatus(str, Enum):
    NOT_MEASURED = "NOT_MEASURED"
    MEASURING = "MEASURING"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    ACHIEVED = "ACHIEVED"
    PARTIALLY_ACHIEVED = "PARTIALLY_ACHIEVED"
    MISSED = "MISSED"
    INCONCLUSIVE = "INCONCLUSIVE"


# ─── Dataclasses ───────────────────────────────────────────────────

@dataclass
class KPIDefinition:
    name: str
    description: str
    formula: str
    unit: str
    baseline: float | None
    target: float | None
    measurement_period: str
    status: MetricStatus = MetricStatus.ACTIVE


@dataclass
class EventDefinition:
    name: str
    description: str
    trigger: str
    properties: list[str]
    required_properties: list[str]
    source: str


@dataclass
class InstrumentationRequirement:
    prd_entity_id: str
    events: list[EventDefinition]
    identity_rules: list[str]
    deduplication_rules: list[str]
    acceptance_criteria: list[str]


@dataclass
class OutcomeHypothesis:
    initiative_name: str
    hypothesis_if: str
    hypothesis_for_segment: str
    hypothesis_then_behavior: str
    hypothesis_which_improves: str
    measured_by_metric: str
    guardrails: list[str]


@dataclass
class ExperimentDefinition:
    hypothesis: OutcomeHypothesis
    target_population: str
    control_variant: str
    treatment_variant: str
    primary_metric: str
    secondary_metrics: list[str]
    guardrails: list[str]
    min_sample_size: int
    duration_days: int
    success_criteria: list[str]


@dataclass
class ExperimentEvaluation:
    experiment_id: str
    observed_effect: str
    statistical_significance: bool
    confidence_level: ConfidenceLevel
    guardrails_ok: bool
    decision: ExperimentDecision
    reasoning: str
    learning: str


@dataclass
class FunnelAnalysis:
    steps: list[str]
    conversion_rates: list[float]
    overall_conversion: float
    largest_dropoff_step: str
    anomaly_detected: bool
    insights: list[str]


@dataclass
class RetentionAnalysis:
    cohort_name: str
    retention_d1: float
    retention_d7: float
    retention_d30: float
    trend: str
    insights: list[str]


@dataclass
class FeatureAdoption:
    feature_name: str
    eligible_users: int
    exposed_users: int
    tried_users: int
    retained_users: int
    adoption_rate: float
    primary_state: FeatureAdoptionState
    recommendation: str


@dataclass
class AnomalyDetection:
    metric_name: str
    baseline_value: float
    observed_value: float
    magnitude_pct: float
    is_anomaly: bool
    potential_causes: list[str]


@dataclass
class ProductChangeCorrelation:
    anomaly: AnomalyDetection
    recent_releases: list[str]
    correlation_strength: str
    investigation_steps: list[str]


@dataclass
class OutcomeScorecard:
    initiative_name: str
    baseline: float
    target: float
    current: float
    progress_pct: float
    status: OutcomeStatus
    guardrail_status: str
    recommendation: str


@dataclass
class StrategicLearning:
    source: str
    learning: str
    confidence: ConfidenceLevel
    affected_decisions: list[str]


# ─── Engine ────────────────────────────────────────────────────────

class AnalyticsIntelligenceEngine:
    """
    Analytics & Outcome Intelligence Engine (PRD-0011).
    Optimizes for outcomes instead of shipped features.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    def define_kpi(
        self,
        name: str,
        description: str,
        formula: str,
        unit: str,
        baseline: float | None = None,
        target: float | None = None,
        measurement_period: str = "weekly",
    ) -> KPIDefinition:
        """Defines a normalized KPI (PRD-0011 §6-§11)."""
        return KPIDefinition(
            name=name,
            description=description,
            formula=formula,
            unit=unit,
            baseline=baseline,
            target=target,
            measurement_period=measurement_period,
            status=MetricStatus.ACTIVE,
        )

    def define_event(
        self,
        name: str,
        description: str,
        trigger: str,
        properties: list[str],
        required_properties: list[str],
        source: str = "frontend",
    ) -> EventDefinition:
        """Defines an analytics event (PRD-0011 §17-§20)."""
        return EventDefinition(
            name=name.lower().replace(" ", "_"),
            description=description,
            trigger=trigger,
            properties=properties,
            required_properties=required_properties,
            source=source,
        )

    def generate_instrumentation_requirements(
        self,
        prd_entity_id: str,
        requirements: list[dict[str, str]],
    ) -> InstrumentationRequirement:
        """Generates required events and tracking rules (PRD-0011 §21)."""
        events = []
        for req in requirements:
            text = req.get("text", "").lower()
            if "booking" in text or "payment" in text:
                events.append(self.define_event(
                    name="transaction_completed",
                    description="User completes a financial transaction",
                    trigger="Successful payment response",
                    properties=["amount", "currency", "item_id"],
                    required_properties=["amount", "currency"]
                ))
            if "signup" in text or "register" in text:
                events.append(self.define_event(
                    name="user_signup",
                    description="User creates an account",
                    trigger="Registration form submitted successfully",
                    properties=["method", "source"],
                    required_properties=["method"]
                ))
        
        return InstrumentationRequirement(
            prd_entity_id=prd_entity_id,
            events=events,
            identity_rules=["Identify user immediately upon login/signup"],
            deduplication_rules=["Deduplicate by event_id within 5 seconds"],
            acceptance_criteria=[
                "Event fires exactly once per action",
                "All required properties are present"
            ],
        )

    def generate_outcome_hypothesis(
        self,
        initiative_name: str,
        action: str,
        target_segment: str,
        expected_behavior_change: str,
        expected_outcome: str,
        primary_metric: str,
        guardrails: list[str],
    ) -> OutcomeHypothesis:
        """Generates a structured outcome hypothesis (PRD-0011 §29-§30)."""
        return OutcomeHypothesis(
            initiative_name=initiative_name,
            hypothesis_if=f"we {action}",
            hypothesis_for_segment=target_segment,
            hypothesis_then_behavior=f"{expected_behavior_change} should change",
            hypothesis_which_improves=expected_outcome,
            measured_by_metric=primary_metric,
            guardrails=guardrails,
        )

    def define_experiment(
        self,
        hypothesis: OutcomeHypothesis,
        min_sample_size: int = 1000,
        duration_days: int = 14,
    ) -> ExperimentDefinition:
        """Defines an experiment from a hypothesis (PRD-0011 §31-§35)."""
        return ExperimentDefinition(
            hypothesis=hypothesis,
            target_population=hypothesis.hypothesis_for_segment,
            control_variant="Current experience",
            treatment_variant="New proposed experience",
            primary_metric=hypothesis.measured_by_metric,
            secondary_metrics=[],
            guardrails=hypothesis.guardrails,
            min_sample_size=min_sample_size,
            duration_days=duration_days,
            success_criteria=[
                f"Statistically significant improvement in {hypothesis.measured_by_metric}",
                "No degradation in guardrail metrics"
            ],
        )

    def evaluate_experiment(
        self,
        experiment_id: str,
        control_value: float,
        treatment_value: float,
        is_statistically_significant: bool,
        guardrails_passed: bool,
    ) -> ExperimentEvaluation:
        """Evaluates experiment results and recommends decision (PRD-0011 §42-§45)."""
        improvement = ((treatment_value - control_value) / max(control_value, 0.0001)) * 100
        
        if is_statistically_significant and guardrails_passed and improvement > 0:
            decision = ExperimentDecision.SHIP
            reasoning = f"Treatment outperformed control by {improvement:.1f}% with significance and passed guardrails."
            learning = "Hypothesis validated. The change drove positive behavior."
            conf = ConfidenceLevel.CONFIRMED
        elif not guardrails_passed:
            decision = ExperimentDecision.ROLLBACK
            reasoning = "Guardrails failed. Cannot ship regardless of primary metric."
            learning = "The change introduced unacceptable negative side-effects."
            conf = ConfidenceLevel.CONFIRMED
        elif is_statistically_significant and improvement <= 0:
            decision = ExperimentDecision.ABANDON
            reasoning = f"Treatment performed worse or equal ({improvement:.1f}%)."
            learning = "Hypothesis invalidated. The change did not drive intended behavior."
            conf = ConfidenceLevel.CONFIRMED
        else:
            decision = ExperimentDecision.INCONCLUSIVE
            reasoning = "Results not statistically significant."
            learning = "Insufficient evidence to draw a conclusion."
            conf = ConfidenceLevel.INFERRED

        return ExperimentEvaluation(
            experiment_id=experiment_id,
            observed_effect=f"{improvement:.1f}% change",
            statistical_significance=is_statistically_significant,
            confidence_level=conf,
            guardrails_ok=guardrails_passed,
            decision=decision,
            reasoning=reasoning,
            learning=learning,
        )

    def analyze_funnel(
        self,
        steps: list[str],
        users_at_steps: list[int],
    ) -> FunnelAnalysis:
        """Analyzes a user funnel and detects anomalies (PRD-0011 §46-§48)."""
        if len(steps) != len(users_at_steps) or not steps:
            raise ValueError("Steps and users_at_steps must be equal length and non-empty.")
            
        conversion_rates = []
        for i in range(1, len(users_at_steps)):
            rate = users_at_steps[i] / max(users_at_steps[i-1], 1)
            conversion_rates.append(round(rate * 100, 1))
            
        overall = (users_at_steps[-1] / max(users_at_steps[0], 1)) * 100
        
        dropoffs = [100.0 - r for r in conversion_rates]
        if dropoffs:
            max_dropoff_idx = dropoffs.index(max(dropoffs))
            largest_dropoff_step = steps[max_dropoff_idx + 1]
            anomaly = max(dropoffs) > 50.0  # heuristic: >50% drop is an anomaly
        else:
            largest_dropoff_step = "None"
            anomaly = False
            
        return FunnelAnalysis(
            steps=steps,
            conversion_rates=conversion_rates,
            overall_conversion=round(overall, 1),
            largest_dropoff_step=largest_dropoff_step,
            anomaly_detected=anomaly,
            insights=[
                f"Overall conversion is {overall:.1f}%",
                f"Largest dropoff is at {largest_dropoff_step} ({max(dropoffs) if dropoffs else 0:.1f}% drop)"
            ],
        )

    def analyze_retention(
        self,
        cohort_name: str,
        d1_rate: float,
        d7_rate: float,
        d30_rate: float,
    ) -> RetentionAnalysis:
        """Analyzes retention cohort data (PRD-0011 §50)."""
        trend = "Stable"
        if d30_rate < 10.0:
            trend = "High Churn"
        elif d30_rate > 40.0:
            trend = "Strong Retention"
            
        return RetentionAnalysis(
            cohort_name=cohort_name,
            retention_d1=d1_rate,
            retention_d7=d7_rate,
            retention_d30=d30_rate,
            trend=trend,
            insights=[
                f"D30 retention is {d30_rate}%",
                f"Trend indicates {trend.lower()}"
            ],
        )

    def evaluate_feature_adoption(
        self,
        feature_name: str,
        eligible: int,
        exposed: int,
        tried: int,
        retained: int,
    ) -> FeatureAdoption:
        """Evaluates feature adoption funnel (PRD-0011 §51-§52)."""
        if retained > 0:
            state = FeatureAdoptionState.RETAINED
        elif tried > 0:
            state = FeatureAdoptionState.TRIED
        elif exposed > 0:
            state = FeatureAdoptionState.EXPOSED
        else:
            state = FeatureAdoptionState.NOT_EXPOSED
            
        adoption_rate = (retained / max(eligible, 1)) * 100
        
        if adoption_rate > 20:
            rec = "Feature has strong adoption. Focus on optimization."
        elif tried > 0 and (retained / tried) < 0.1:
            rec = "Users try but don't retain. Investigate friction or unmet value."
        elif exposed > 0 and (tried / exposed) < 0.1:
            rec = "Users are exposed but don't try. Investigate discoverability or messaging."
        else:
            rec = "Increase exposure to eligible users."

        return FeatureAdoption(
            feature_name=feature_name,
            eligible_users=eligible,
            exposed_users=exposed,
            tried_users=tried,
            retained_users=retained,
            adoption_rate=round(adoption_rate, 1),
            primary_state=state,
            recommendation=rec,
        )

    def detect_metric_anomaly(
        self,
        metric_name: str,
        baseline_value: float,
        observed_value: float,
    ) -> AnomalyDetection:
        """Detects anomalies in metrics (PRD-0011 §63-§65)."""
        magnitude = ((observed_value - baseline_value) / max(baseline_value, 0.0001)) * 100
        is_anomaly = abs(magnitude) > 15.0  # heuristic
        
        causes = []
        if is_anomaly:
            if magnitude < 0:
                causes = ["Recent release bug", "Tracking issue", "Seasonality drop"]
            else:
                causes = ["Successful new feature", "Bot traffic spike", "Seasonality peak"]
                
        return AnomalyDetection(
            metric_name=metric_name,
            baseline_value=baseline_value,
            observed_value=observed_value,
            magnitude_pct=round(magnitude, 1),
            is_anomaly=is_anomaly,
            potential_causes=causes,
        )

    def correlate_product_change(
        self,
        anomaly: AnomalyDetection,
        recent_releases: list[str],
    ) -> ProductChangeCorrelation:
        """Correlates metric anomalies with recent product changes (PRD-0011 §66-§67)."""
        strength = "HIGH" if anomaly.is_anomaly and recent_releases else "LOW"
        
        return ProductChangeCorrelation(
            anomaly=anomaly,
            recent_releases=recent_releases,
            correlation_strength=strength,
            investigation_steps=[
                "Check error rates during release window",
                "Segment anomaly by platform/device",
                "Verify event instrumentation was not changed"
            ] if anomaly.is_anomaly else ["No investigation needed"]
        )

    def evaluate_outcome_scorecard(
        self,
        initiative_name: str,
        baseline: float,
        target: float,
        current: float,
        guardrail_violations: int = 0,
    ) -> OutcomeScorecard:
        """Evaluates progress against expected outcomes (PRD-0011 §68-§70)."""
        total_change_needed = target - baseline
        current_change = current - baseline
        
        if total_change_needed == 0:
            progress = 100.0 if current >= target else 0.0
        else:
            progress = (current_change / total_change_needed) * 100

        if progress >= 100 and guardrail_violations == 0:
            status = OutcomeStatus.ACHIEVED
            rec = "Outcome achieved successfully."
        elif progress >= 50 and guardrail_violations == 0:
            status = OutcomeStatus.ON_TRACK
            rec = "Tracking well, continue monitoring."
        elif guardrail_violations > 0:
            status = OutcomeStatus.AT_RISK
            rec = "Guardrails violated. Immediate attention required."
        else:
            status = OutcomeStatus.MISSED
            rec = "Outcome missed. Initiate hypothesis review."

        return OutcomeScorecard(
            initiative_name=initiative_name,
            baseline=baseline,
            target=target,
            current=current,
            progress_pct=round(max(0, min(100, progress)), 1),
            status=status,
            guardrail_status="VIOLATED" if guardrail_violations > 0 else "OK",
            recommendation=rec,
        )

    def extract_strategic_learning(
        self,
        experiment_evaluation: ExperimentEvaluation,
    ) -> StrategicLearning:
        """Extracts strategic learning from outcomes (PRD-0011 §71-§76)."""
        return StrategicLearning(
            source=f"Experiment: {experiment_evaluation.experiment_id}",
            learning=experiment_evaluation.learning,
            confidence=experiment_evaluation.confidence_level,
            affected_decisions=["Update product roadmap", "Revise related PRDs"]
        )
