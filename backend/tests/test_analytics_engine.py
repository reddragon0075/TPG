"""
Tests for Analytics & Outcome Intelligence Engine (PRD-0011)
"""

import pytest
from app.services.analytics_engine import (
    AnalyticsIntelligenceEngine,
    ExperimentDecision,
    OutcomeStatus,
    FeatureAdoptionState,
)


def test_define_kpi():
    engine = AnalyticsIntelligenceEngine()
    kpi = engine.define_kpi(
        name="Conversion Rate",
        description="Checkout conversion",
        formula="orders / sessions",
        unit="percentage",
        baseline=5.0,
        target=6.0,
    )
    assert kpi.name == "Conversion Rate"
    assert kpi.target == 6.0


def test_generate_instrumentation_requirements():
    engine = AnalyticsIntelligenceEngine()
    reqs = [{"id": "FR-001", "text": "Users can pay via credit card for their booking"}]
    instr = engine.generate_instrumentation_requirements("prd-123", reqs)
    
    assert len(instr.events) > 0
    assert any(e.name == "transaction_completed" for e in instr.events)


def test_define_experiment():
    engine = AnalyticsIntelligenceEngine()
    hyp = engine.generate_outcome_hypothesis(
        initiative_name="Checkout Redesign",
        action="simplify checkout",
        target_segment="all users",
        expected_behavior_change="dropoff",
        expected_outcome="increased revenue",
        primary_metric="conversion_rate",
        guardrails=["error_rate"]
    )
    exp = engine.define_experiment(hypothesis=hyp)
    assert exp.primary_metric == "conversion_rate"
    assert exp.target_population == "all users"


def test_evaluate_experiment():
    engine = AnalyticsIntelligenceEngine()
    eval = engine.evaluate_experiment(
        experiment_id="exp-001",
        control_value=5.0,
        treatment_value=6.0,  # 20% improvement
        is_statistically_significant=True,
        guardrails_passed=True,
    )
    assert eval.decision == ExperimentDecision.SHIP
    assert "20.0%" in eval.observed_effect
    
    eval_bad = engine.evaluate_experiment(
        experiment_id="exp-002",
        control_value=5.0,
        treatment_value=6.0,
        is_statistically_significant=True,
        guardrails_passed=False,
    )
    assert eval_bad.decision == ExperimentDecision.ROLLBACK


def test_analyze_funnel():
    engine = AnalyticsIntelligenceEngine()
    funnel = engine.analyze_funnel(
        steps=["Home", "Product", "Cart", "Checkout"],
        users_at_steps=[1000, 500, 100, 10]
    )
    # Home -> Product: 50%
    # Product -> Cart: 20%
    # Cart -> Checkout: 10% (Dropoff = 90%)
    assert funnel.overall_conversion == 1.0
    assert funnel.largest_dropoff_step == "Checkout"
    assert funnel.anomaly_detected is True


def test_evaluate_feature_adoption():
    engine = AnalyticsIntelligenceEngine()
    adoption = engine.evaluate_feature_adoption(
        feature_name="Dark Mode",
        eligible=1000,
        exposed=800,
        tried=400,
        retained=300
    )
    assert adoption.primary_state == FeatureAdoptionState.RETAINED
    assert adoption.adoption_rate == 30.0


def test_detect_anomaly():
    engine = AnalyticsIntelligenceEngine()
    anomaly = engine.detect_metric_anomaly("Active Users", 1000, 1200)
    assert anomaly.magnitude_pct == 20.0
    assert anomaly.is_anomaly is True


def test_evaluate_outcome_scorecard():
    engine = AnalyticsIntelligenceEngine()
    scorecard = engine.evaluate_outcome_scorecard(
        initiative_name="Faster API",
        baseline=1000,
        target=500,
        current=600,
    )
    # Needed change = -500. Current change = -400. Progress = 80%.
    assert scorecard.progress_pct == 80.0
    assert scorecard.status == OutcomeStatus.ON_TRACK
