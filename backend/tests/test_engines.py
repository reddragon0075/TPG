"""
Tests for Domain Intelligence Engines (PRD-0005 & PRD-0006)
"""

import pytest
from app.services.requirement_engine import (
    RequirementIntelligenceEngine,
    RequirementType,
)
from app.services.decision_engine import (
    ProductDecisionEngine,
    DecisionType,
    DecisionOutcome,
    SolutionOption,
)


def test_noise_filtering_vs_product_requirements():
    engine = RequirementIntelligenceEngine()

    # Noise / Operational statements
    t_noise, is_prod_noise = engine.classify_statement("Please book a room for tomorrow's standup meeting")
    assert is_prod_noise is False
    assert t_noise == RequirementType.NON_PRODUCT_NOISE

    t_ops, is_prod_ops = engine.classify_statement("The office wifi is not working and reset my password")
    assert is_prod_ops is False
    assert t_ops == RequirementType.OPERATIONAL_REQUEST

    # Real Product Requirements
    t_feat, is_prod_feat = engine.classify_statement("We need bulk CSV import for employee rosters")
    assert is_prod_feat is True
    assert t_feat == RequirementType.FEATURE_REQUEST

    t_prob, is_prod_prob = engine.classify_statement("Operations team takes 4 hours wasting time on manual entry friction")
    assert is_prod_prob is True
    assert t_prob == RequirementType.PROBLEM_REPORT

    t_bug, is_prod_bug = engine.classify_statement("Drivers getting 500 error when clicking submit payout")
    assert is_prod_bug is True
    assert t_bug == RequirementType.BUG


def test_ambiguity_scoring_and_question_prioritization():
    engine = RequirementIntelligenceEngine()

    # Ambiguous one-liner: "Build an AI chatbot"
    analysis = engine.analyze_ambiguity("Build an AI chatbot")
    assert analysis.is_product_requirement is True
    assert analysis.ambiguity_score >= 0.6  # High ambiguity
    assert "problem_clarity" in analysis.missing_dimensions
    assert "user_persona" in analysis.missing_dimensions

    # Prioritized discovery questions should be ordered by priority (1=highest info value)
    assert len(analysis.prioritized_questions) > 0
    assert analysis.prioritized_questions[0].priority == 1
    assert "problem" in analysis.prioritized_questions[0].question.lower()

    # Complete statement: with persona, problem, and impact
    complete_text = (
        "Vendors are struggling with reconciliation delays costing $50k monthly "
        "because manual spreadsheets fail under high volume. We need batch payouts."
    )
    analysis_complete = engine.analyze_ambiguity(complete_text)
    assert analysis_complete.ambiguity_score < 0.5
    assert analysis_complete.completeness_score > 0.5


def test_decision_tradeoff_scoring():
    engine = ProductDecisionEngine()

    # Option A: High impact, low effort, high confidence, low risk
    opt_a = SolutionOption(
        name="Automated Stripe Webhooks",
        description="Integrate webhook listener for real-time ledger updates",
        impact=4.5,
        effort=2.0,
        risk=1.5,
        confidence=0.9,
    )

    # Option B: High effort, high risk, moderate impact
    opt_b = SolutionOption(
        name="Custom In-House Banking Rail",
        description="Build direct ACH settlement engine",
        impact=4.0,
        effort=5.0,
        risk=4.5,
        confidence=0.6,
    )

    ranked = engine.evaluate_tradeoffs([opt_b, opt_a])
    # Option A should win decisively
    assert ranked[0][0].name == "Automated Stripe Webhooks"
    assert ranked[0][1] > ranked[1][1]

    # Test Decision Record formulation
    record = engine.formulate_decision(
        title="Payment Reconciliation Architecture",
        decision_type=DecisionType.ARCHITECTURE,
        outcome=DecisionOutcome.APPROVED,
        decision_question="How should vendor settlement reconciliations be automated?",
        context="Current volume is causing 48-hour delays during month-end closes.",
        rationale="Stripe webhooks provide 90% SLA improvement with minimal infrastructure overhead.",
        options=[opt_a, opt_b],
        evidence_citations=["Ops interview notes #14", "Q3 Stripe API benchmark"],
        risks=[{"risk": "Webhook replay attacks", "mitigation": "HMAC signature verification"}],
        expected_outcomes=["Reduce settlement latency from 48h to < 10m"],
    )

    assert record.outcome == DecisionOutcome.APPROVED
    assert len(record.tradeoffs) == 1
    assert record.confidence == 0.9
