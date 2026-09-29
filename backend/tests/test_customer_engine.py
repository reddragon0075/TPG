"""
Tests for Customer Intelligence Engine (PRD-0012)
"""

import pytest
from app.services.customer_engine import (
    CustomerIntelligenceEngine,
    CustomerSignal,
    CustomerProblem,
    SignalType,
    UrgencyLevel,
    Sentiment,
)


def test_ingest_signal():
    engine = CustomerIntelligenceEngine()
    signal = engine.ingest_signal(
        customer_id="CUS-123",
        source="EMAIL",
        source_reference="msg-1",
        raw_text="I am going to cancel my account, your competitor is much better.",
    )
    assert signal.signal_type == SignalType.CHURN_SIGNAL
    assert signal.urgency == UrgencyLevel.CRITICAL
    assert signal.sentiment == Sentiment.NEGATIVE


def test_extract_problem():
    engine = CustomerIntelligenceEngine()
    signal = CustomerSignal(
        workspace_id="ws-1",
        customer_id="CUS-123",
        source="SUPPORT",
        source_reference="tkt-1",
        signal_type=SignalType.PROBLEM_REPORT,
        summary="Customer complains about manual invoice processing.",
        raw_claim="We have to manually reconcile 100 invoices.",
        urgency=UrgencyLevel.MEDIUM,
        sentiment=Sentiment.NEUTRAL,
    )
    problem = engine.extract_problem(signal)
    assert problem.signal_id == "tkt-1"
    assert "manual" in problem.problem_statement


def test_estimate_impact():
    engine = CustomerIntelligenceEngine()
    problem = CustomerProblem(
        signal_id="tkt-1",
        problem_statement="Manual data entry takes hours",
        affected_workflow="Core",
        frequency="Unknown",
        workaround_exists=False,
    )
    impact = engine.estimate_impact(problem)
    assert impact.time_impact == "High"
    assert impact.severity == UrgencyLevel.HIGH


def test_extract_opportunity():
    engine = CustomerIntelligenceEngine()
    problem = CustomerProblem(
        signal_id="tkt-1",
        problem_statement="Manual data entry takes hours",
        affected_workflow="Core",
        frequency="Unknown",
        workaround_exists=False,
    )
    opp = engine.extract_opportunity(problem)
    assert "Automate" in opp.potential_opportunity


def test_analyze_churn_risk():
    engine = CustomerIntelligenceEngine()
    sig1 = CustomerSignal(
        workspace_id="ws-1",
        customer_id="CUS-123",
        source="SUPPORT",
        source_reference="tkt-1",
        signal_type=SignalType.CHURN_SIGNAL,
        summary="Threatening to leave",
        raw_claim="",
        urgency=UrgencyLevel.CRITICAL,
        sentiment=Sentiment.NEGATIVE,
    )
    risk = engine.analyze_churn_risk([sig1])
    assert risk.risk_level == UrgencyLevel.CRITICAL
    assert risk.primary_reason == "Threatening to leave"


def test_evaluate_feature_request():
    engine = CustomerIntelligenceEngine()
    eval_res = engine.evaluate_feature_request("We need an export to Excel button")
    assert eval_res.is_genuine_problem is True
    assert len(eval_res.alternative_solutions) > 0


def test_summarize_account():
    engine = CustomerIntelligenceEngine()
    sig1 = CustomerSignal(
        workspace_id="ws-1",
        customer_id="CUS-123",
        source="SUPPORT",
        source_reference="tkt-1",
        signal_type=SignalType.BUG_REPORT,
        summary="Bug 1",
        raw_claim="",
        urgency=UrgencyLevel.HIGH,
        sentiment=Sentiment.NEGATIVE,
    )
    sig2 = CustomerSignal(
        workspace_id="ws-1",
        customer_id="CUS-123",
        source="SUPPORT",
        source_reference="tkt-2",
        signal_type=SignalType.BUG_REPORT,
        summary="Bug 2",
        raw_claim="",
        urgency=UrgencyLevel.HIGH,
        sentiment=Sentiment.NEGATIVE,
    )
    summary = engine.summarize_account("CUS-123", [sig1, sig2])
    assert summary.total_signals == 2
    assert summary.overall_sentiment == Sentiment.NEGATIVE
    assert summary.churn_risk in (UrgencyLevel.HIGH, UrgencyLevel.MEDIUM)
