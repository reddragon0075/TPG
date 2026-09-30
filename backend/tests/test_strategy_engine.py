"""
Tests for Product Strategy & Roadmap Intelligence Engine (PRD-0007)
"""

import pytest
from app.services.strategy_engine import (
    StrategyIntelligenceEngine,
    StrategicThemeData,
    StrategicObjectiveData,
    StrategicBetData,
    StrategicAssumptionData,
    TimeHorizon,
    ObjectiveType,
    BetLifecycleStatus,
    RoadmapHorizon,
)
from tests.conftest import TEST_WORKSPACE_ID


@pytest.mark.asyncio
async def test_create_theme(test_session):
    engine = StrategyIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)
    theme = await engine.create_theme(
        StrategicThemeData(
            name="Enterprise Expansion",
            description="Expand into Fortune 500 accounts with enterprise security.",
            priority="HIGH",
            time_horizon=TimeHorizon.LONG_12_24_MONTHS,
            success_metrics=["ARR +40%", "Enterprise retention 98%"],
        )
    )
    assert theme["theme_id"] is not None
    assert theme["name"] == "Enterprise Expansion"
    assert theme["priority"] == "HIGH"
    assert "ARR +40%" in theme["success_metrics"]


@pytest.mark.asyncio
async def test_create_objective_linked_to_theme(test_session):
    engine = StrategyIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)
    theme = await engine.create_theme(
        StrategicThemeData(
            name="Retention Theme",
            description="Boost customer retention across all tiers.",
        )
    )
    obj = await engine.create_objective(
        StrategicObjectiveData(
            name="Reduce Churn to 2%",
            theme_id=theme["theme_id"],
            objective_type=ObjectiveType.RETENTION,
            baseline=4.5,
            target=2.0,
            unit="%",
            deadline="2027-12-31",
            owner="VP Product",
        )
    )
    assert obj["objective_id"] is not None
    assert obj["theme_id"] == theme["theme_id"]
    assert obj["baseline"] == 4.5
    assert obj["target"] == 2.0


@pytest.mark.asyncio
async def test_create_and_evaluate_strategic_bet(test_session):
    engine = StrategyIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)
    bet = await engine.create_bet(
        StrategicBetData(
            name="Autonomous Agent Onboarding",
            hypothesis="Self-serve conversational onboarding will reduce time-to-first-value by 60%.",
            investment_size="MEDIUM",
            confidence=0.75,
        )
    )
    assert bet["bet_id"] is not None
    assert bet["name"] == "Autonomous Agent Onboarding"

    evaluation = engine.evaluate_bet(
        name=bet["name"],
        hypothesis=bet["hypothesis"],
        evidence_strength=0.85,
        investment_size="MEDIUM",
        market_uncertainty=0.3,
    )
    assert evaluation["viability_score"] > 60.0
    assert evaluation["recommendation"] in ("INVEST", "EXPLORE")
    assert len(evaluation["validation_milestones"]) == 3


@pytest.mark.asyncio
async def test_record_strategic_assumption(test_session):
    engine = StrategyIntelligenceEngine(db=test_session, workspace_id=TEST_WORKSPACE_ID)
    assump = await engine.record_assumption(
        StrategicAssumptionData(
            statement="Enterprise buyers will accept digital executive reasoning without human signoff.",
            category="BEHAVIORAL",
            confidence="MEDIUM",
        )
    )
    assert assump["assumption_id"] is not None
    assert assump["status"] == "UNVALIDATED"


def test_score_strategic_alignment():
    engine = StrategyIntelligenceEngine()

    # Strong alignment: theme, objective, and evidence
    res_strong = engine.score_strategic_alignment(
        initiative_name="SSO & RBAC Integration",
        problem_statement="Enterprise security requires Okta SSO and fine-grained permissions.",
        linked_theme="Enterprise Expansion",
        linked_objective="Close 20 Fortune 500 deals",
        has_validated_evidence=True,
    )
    assert res_strong["alignment_score"] == 100.0
    assert res_strong["alignment_level"] == "STRONG"
    assert res_strong["is_constitutionally_sound"] is True

    # Weak alignment: no theme, no objective, no evidence
    res_weak = engine.score_strategic_alignment(
        initiative_name="Random Pet Project",
        problem_statement="Short text",
        linked_theme=None,
        linked_objective=None,
        has_validated_evidence=False,
    )
    assert res_weak["alignment_score"] < 50.0
    assert res_weak["alignment_level"] == "WEAK"
    assert len(res_weak["gap_analysis"]) >= 2


@pytest.mark.asyncio
async def test_generate_roadmap_horizons():
    engine = StrategyIntelligenceEngine()
    initiatives = [
        {
            "id": "init-1",
            "name": "Core Knowledge Engine",
            "theme": "Enterprise Platform",
            "objective": "Scale to 100k nodes",
            "confidence": "confirmed",
            "status": "active",
        },
        {
            "id": "init-2",
            "name": "Self-Serve Discovery",
            "theme": "Growth",
            "objective": None,
            "confidence": "inferred",
            "status": "active",
        },
        {
            "id": "init-3",
            "name": "Quantum AI Speculative Module",
            "theme": None,
            "objective": None,
            "confidence": "assumed",
            "status": "draft",
        },
    ]

    roadmap = await engine.generate_roadmap(initiatives=initiatives)
    assert roadmap["total_initiatives"] == 3
    assert roadmap["now_count"] >= 1
    assert roadmap["horizons"]["NOW"][0]["name"] == "Core Knowledge Engine"
    assert roadmap["later_count"] >= 1


def test_detect_strategic_drift():
    engine = StrategyIntelligenceEngine()
    initiatives = [
        {"name": "Init A", "theme": "Enterprise Expansion"},
        {"name": "Init B", "theme": "Cost Reduction"},
        {"name": "Init C", "theme": "Unrelated Theme"},
        {"name": "Init D", "theme": "Unrelated Theme 2"},
    ]
    active_themes = ["Enterprise Expansion", "Cost Reduction"]

    drift = engine.detect_strategic_drift(initiatives=initiatives, active_themes=active_themes)
    assert drift["total_initiatives"] == 4
    assert drift["aligned_count"] == 2
    assert drift["unaligned_count"] == 2
    assert drift["drift_percentage"] == 50.0
    assert drift["drift_level"] == "HIGH"


def test_analyze_portfolio_balance():
    engine = StrategyIntelligenceEngine()

    # Imbalanced portfolio: 80% growth, 5% retention, 5% tech debt
    res = engine.analyze_portfolio_balance(
        allocations={"growth": 80.0, "retention": 5.0, "tech_debt": 5.0, "efficiency": 10.0}
    )
    assert res["status"] in ("WARNING", "CRITICAL_IMBALANCE")
    assert len(res["warnings"]) >= 2

    # Balanced portfolio
    balanced = engine.analyze_portfolio_balance(
        allocations={"growth": 40.0, "retention": 25.0, "tech_debt": 20.0, "efficiency": 15.0}
    )
    assert balanced["status"] == "BALANCED"
    assert len(balanced["warnings"]) == 0
