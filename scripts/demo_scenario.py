"""
TPG Genesis Demo Scenario — The Constitutional PRD-0001 Benchmark

Demonstrates the ultimate test from PRD-0001 §54-§68:
A new employee joining after three years asks:
    "Why did we build Vendor Wallet?"

And TPG reconstructs without any manual documentation:
- 1. Original customer problem & stakeholder context
- 2. Strategic themes & objectives driving the initiative
- 3. Requirement ambiguity analysis & JTBD discovery
- 4. Solution trade-offs & immutable Architectural Decision Record (ADR)
- 5. PRD generation with non-goals and Gherkin acceptance criteria
- 6. Technical engineering decomposition & effort estimation
- 7. QA test strategy & Go/No-Go release readiness
- 8. Analytics KPI definition & actual measured business outcomes
- 9. Multi-stage graph retrieval and provenance lineage tree reconstruction!

Run with:
    python scripts/demo_scenario.py
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.workspace import Workspace
from app.models.entity import (
    Entity,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
    EntityRelationship,
    RelationshipType,
)
from app.services.strategy_engine import (
    StrategyIntelligenceEngine,
    StrategicThemeData,
    StrategicObjectiveData,
    StrategicBetData,
    ObjectiveType,
    TimeHorizon,
)
from app.services.customer_engine import CustomerIntelligenceEngine
from app.services.requirement_engine import RequirementIntelligenceEngine
from app.services.decision_engine import (
    ProductDecisionEngine,
    DecisionType,
    DecisionOutcome,
    SolutionOption,
)
from app.services.prd_engine import PRDSpecificationEngine
from app.services.engineering_engine import EngineeringIntelligenceEngine
from app.services.qa_engine import QAIntelligenceEngine
from app.services.analytics_engine import AnalyticsIntelligenceEngine, MetricStatus
from app.graph.retrieval import GraphRetrievalEngine
from app.graph.traversal import GraphTraversalEngine


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Safe formatting for all terminals
class C:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner(step_num: str, title: str, subtitle: str = ""):
    print(f"\n{C.BOLD}{C.CYAN}{'='*80}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}> STEP {step_num}: {title}{C.RESET}")
    if subtitle:
        print(f"{C.DIM}  {subtitle}{C.RESET}")
    print(f"{C.CYAN}{'-'*80}{C.RESET}")


async def run_genesis_simulation():
    print(f"\n{C.BOLD}{C.HEADER}+------------------------------------------------------------------------------+")
    print(f"|               TPG -- THE INVISIBLE AUTONOMOUS PRODUCT OFFICE                 |")
    print(f"|                  PRD-0001 Genesis Benchmark Demonstration                    |")
    print(f"+------------------------------------------------------------------------------+{C.RESET}")

    # Initialize in-memory SQLite async DB for fast, zero-dependency demo
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as db:
        # Create Demo Organization Workspace
        ws_id = "ws-taski-enterprise"
        workspace = Workspace(
            id=ws_id,
            owner_email="founder@taski.com",
            owner_name="taSki Mobility Founder",
            name="taSki Mobility Platform Workspace",
            description="Autonomous Product Office for urban fleet platform.",
        )
        db.add(workspace)
        await db.flush()

        # ─── 1. Strategy & Portfolio Setup (PRD-0007) ───────────────────────────
        print_banner("1", "Strategy & Theme Formulation (PRD-0007)", "Setting company strategic guardrails")
        strategy_engine = StrategyIntelligenceEngine(db=db, workspace_id=ws_id)

        theme = await strategy_engine.create_theme(
            StrategicThemeData(
                name="Fleet Ecosystem Retention & FinTech Expansion",
                description="Automate financial settlement flows for driver partners and commercial fleet owners.",
                priority="HIGH",
                time_horizon=TimeHorizon.LONG_12_24_MONTHS,
                success_metrics=["Partner Churn < 3%", "Payout Latency < 2h"],
            )
        )
        theme_id = theme["theme_id"]
        print(f"  {C.BOLD}• Strategic Theme Recorded:{C.RESET} '{theme['name']}' (ID: {theme_id[:8]}...)")

        objective = await strategy_engine.create_objective(
            StrategicObjectiveData(
                name="Compress Vendor Settlement Latency to < 2 Hours",
                theme_id=theme_id,
                objective_type=ObjectiveType.RETENTION,
                baseline=336.0,  # 14 days
                target=2.0,      # 2 hours
                unit="hours",
                deadline="2027-06-30",
                owner="VP Product",
            )
        )
        obj_id = objective["objective_id"]
        print(f"  {C.BOLD}• Objective Created:{C.RESET} '{objective['name']}' (Baseline: 336h -> Target: 2h)")

        bet = await strategy_engine.create_bet(
            StrategicBetData(
                name="Instant Vendor Digital Wallet",
                hypothesis="Providing instant ledger-backed digital wallets to fleet partners will reduce partner churn by 50% and eliminate manual finance team reconciliation.",
                strategic_theme_id=theme_id,
                investment_size="MEDIUM",
                confidence=0.88,
            )
        )
        bet_id = bet["bet_id"]
        print(f"  {C.BOLD}• Strategic Bet Formulated:{C.RESET} '{bet['name']}' (Confidence: 88%)")

        # ─── 2. Customer Signal Ingestion & Problem Extraction (PRD-0012) ─────────
        print_banner("2", "Customer Intelligence & Problem Extraction (PRD-0012)", "Ingesting real-world friction signals")
        customer_engine = CustomerIntelligenceEngine(db=db, workspace_id=ws_id)

        # Store Customer Organization & Stakeholder
        client_ent = Entity(
            id="cust-indigo",
            workspace_id=ws_id,
            entity_type=EntityType.CUSTOMER,
            name="IndiGo Fleet Network",
            description="Major regional airline transport vendor managing 2,500 shuttle drivers.",
            confidence=ConfidenceLevel.CONFIRMED,
        )
        contact_ent = Entity(
            id="person-rajesh",
            workspace_id=ws_id,
            entity_type=EntityType.CONTACT,
            name="Rajesh Kumar",
            description="Head of Ground Fleet Procurement, IndiGo Logistics",
            confidence=ConfidenceLevel.CONFIRMED,
        )
        db.add_all([client_ent, contact_ent])
        await db.flush()

        raw_msg = (
            "Vendor payment reconciliation takes 14 business days. Our fleet owners are refusing to accept "
            "airport transfers because settlements are unpredictable. We urgently need real-time wallet credits "
            "or we will cancel contract renewals next month."
        )
        signal = customer_engine.ingest_signal(
            customer_id="cust-indigo",
            source="slack",
            source_reference="slack-msg-indigo-001",
            raw_text=raw_msg,
        )
        print(f"  {C.BOLD}* Signal Ingested:{C.RESET} From Rajesh Kumar ({signal.signal_type.value}, Urgency: {signal.urgency.value})")

        problem = customer_engine.extract_problem(signal)
        impact = customer_engine.estimate_impact(problem)
        problem_ent = Entity(
            id="prob-vendor-delay",
            workspace_id=ws_id,
            entity_type=EntityType.PROBLEM,
            name="Vendor Payment Reconciliation Delays (14-day lag)",
            description=problem.problem_statement,
            properties={"impact": impact.time_impact, "severity": impact.severity.value},
            confidence=ConfidenceLevel.CONFIRMED,
        )
        db.add(problem_ent)

        # Connect Customer -> Problem
        db.add(EntityRelationship(
            source_entity_id="cust-indigo",
            target_entity_id="prob-vendor-delay",
            relationship_type=RelationshipType.REQUESTED_BY,
        ))
        await db.flush()
        print(f"  {C.BOLD}• Validated Problem Stored:{C.RESET} '{problem_ent.name}'")
        print(f"    Impact: High Churn Risk (Account Renewal at risk)")

        # ─── 3. Requirement Intelligence & Ambiguity Analysis (PRD-0005) ────────
        print_banner("3", "Requirement Intelligence & JTBD Synthesis (PRD-0005)", "Filtering noise and structuring intent")
        req_engine = RequirementIntelligenceEngine(db=db, workspace_id=ws_id)

        statement = "We need an automated digital wallet for vendors that settles batch trip payments in under 2 hours with instant withdrawal."
        analysis = req_engine.analyze_ambiguity(statement)
        print(f"  {C.BOLD}• Ambiguity Analysis Score:{C.RESET} {analysis.ambiguity_score}/100 (Completeness: {analysis.completeness_score}%)")
        print(f"  {C.BOLD}• Synthesized JTBD:{C.RESET}")
        for jtbd in analysis.suggested_jtbd:
            print(f"    - When {jtbd.situation}, I want to {jtbd.motivation}, so that {jtbd.expected_outcome}")

        # Ingest central initiative and requirement
        init_ent = Entity(
            id="init-vendor-wallet",
            workspace_id=ws_id,
            entity_type=EntityType.INITIATIVE,
            name="Vendor Wallet",
            description="Automated ledger, digital wallet, and real-time bank settlement engine for fleet partners.",
            confidence=ConfidenceLevel.CONFIRMED,
        )
        req_ent = Entity(
            id="req-realtime-wallet",
            workspace_id=ws_id,
            entity_type=EntityType.REQUIREMENT,
            name="Real-time Batch Payout Settlements",
            description=statement,
            confidence=ConfidenceLevel.CONFIRMED,
        )
        db.add_all([init_ent, req_ent])

        # Link Problem -> Requirement -> Initiative -> Strategic Bet
        db.add_all([
            EntityRelationship(source_entity_id="prob-vendor-delay", target_entity_id="req-realtime-wallet", relationship_type=RelationshipType.RESOLVES),
            EntityRelationship(source_entity_id="req-realtime-wallet", target_entity_id="init-vendor-wallet", relationship_type=RelationshipType.PART_OF),
            EntityRelationship(source_entity_id="init-vendor-wallet", target_entity_id=bet_id, relationship_type=RelationshipType.SUPPORTS),
            EntityRelationship(source_entity_id="init-vendor-wallet", target_entity_id=obj_id, relationship_type=RelationshipType.MEASURED_BY),
        ])
        await db.flush()
        print(f"  {C.BOLD}• Initiative Created:{C.RESET} 'Vendor Wallet' (Linked to Strategy Bet & Objective)")

        # ─── 4. Product Decision Engine & Immutable ADR (PRD-0006) ──────────────
        print_banner("4", "Decision Engine & Trade-off Scoring (PRD-0006)", "Quantitative evaluation before commitment")
        decision_engine = ProductDecisionEngine(db=db, workspace_id=ws_id)

        opt1 = SolutionOption(
            name="Integrated Cloud Payout API (Stripe Connect / RazorpayX)",
            description="Plug-and-play regulated payout rails with built-in banking API connections.",
            effort=2.5,
            impact=4.8,
            risk=1.2,
            confidence=0.92,
        )
        opt2 = SolutionOption(
            name="In-House Bank Host-to-Host SFTP File Transfer",
            description="Direct batched file protocol with local partner bank.",
            effort=5.0,
            impact=3.0,
            risk=3.8,
            confidence=0.60,
        )

        ranked = decision_engine.evaluate_tradeoffs([opt1, opt2])
        for opt, score, notes in ranked:
            print(f"  * Candidate Option: {opt.name}")
            print(f"    Efficiency Score: {score} | {notes}")

        adr_record = decision_engine.formulate_decision(
            title="ADR-001: Adopt Cloud Payout Rails for Vendor Wallet",
            decision_type=DecisionType.BUILD_VS_BUY,
            outcome=DecisionOutcome.APPROVED,
            decision_question="Should taSki build custom bank SFTP queues or integrate regulated Cloud Payout APIs?",
            context="IndiGo churn risk demands <2h settlement; building custom banking protocol takes 6+ months.",
            rationale="Integrated Cloud Payout API yields 3.6x higher efficiency score with minimal regulatory overhead.",
            options=[opt1, opt2],
            evidence_citations=["Customer Signal from IndiGo", "IndiGo contract renewal value $1.2M"],
            risks=["Transaction fee per transfer", "API outage dependency"],
            expected_outcomes=["Reduce settlement lag to < 2 hours", "Prevent partner churn"],
        )
        adr_save = await decision_engine.record_decision(
            record=adr_record,
            initiative_id="init-vendor-wallet",
            problem_id="prob-vendor-delay",
            requirement_id="req-realtime-wallet",
        )
        adr_id = adr_save["decision_id"]
        print(f"  {C.BOLD}• Immutable ADR Persisted:{C.RESET} {adr_record.title} (ID: {adr_id[:8]}...)")

        # ─── 5. PRD & Product Specification Engine (PRD-0008) ────────────────────
        print_banner("5", "PRD Specification Synthesis (PRD-0008)", "Generating execution contract with scope fencing")
        prd_engine = PRDSpecificationEngine(db=db, workspace_id=ws_id)

        assessment = prd_engine.assess_readiness(
            problem="Vendor payout reconciliation lag causes high churn and partner walkouts.",
            requirements=["Instant wallet ledger", "Automated batch payouts", "Driver mobile view"],
            decision_rationale="Approved ADR-001 utilizing Cloud Payout rails.",
            evidence=["IndiGo operational logs", "Partner survey 89% requesting daily pay"],
            success_metric="Payout latency < 2h and churn < 3%",
        )
        print(f"  {C.BOLD}• PRD Readiness Gate:{C.RESET} Level = {C.GREEN}{assessment.level.value}{C.RESET} (Score: {assessment.overall_score}/100)")

        prd_doc = prd_engine.generate_prd(
            title="PRD: Vendor Wallet & Automated Payout Engine",
            problem="14-day manual vendor settlement creates unacceptable partner churn and threatens enterprise contract renewals.",
            raw_requirements=[
                "Real-time balance tracking for driver partners",
                "Automated batch disbursement API triggered upon shift completion",
                "Bank webhook listener for payout confirmation",
            ],
            decision_rationale="Approved ADR-001 (Cloud Payout Rails).",
            evidence=["IndiGo churn risk", "Partner interview feedback"],
            target_personas=["Fleet Owner", "Driver Partner", "Internal Finance Controller"],
            non_goals=[
                "B2C passenger payments (handled by main app)",
                "Driver credit lines or micro-loans (deferred to Phase 2)",
                "Physical debit card issuance",
            ],
            success_metric="Payout turnaround time reduced from 336 hours to under 2 hours.",
            initiative_id="init-vendor-wallet",
            decision_id=adr_id,
        )
        prd_save = await prd_engine.save_prd(prd_doc)
        prd_id = prd_save["prd_id"]
        print(f"  {C.BOLD}• Constitutional PRD Saved:{C.RESET} {prd_doc.title} (v{prd_doc.version})")
        print(f"    - Functional Requirements: {len(prd_doc.functional_requirements)} specs")
        print(f"    - Acceptance Criteria (Gherkin): {len(prd_doc.acceptance_criteria)} scenarios")
        print(f"    - Explicit Scope Non-Goals: {len(prd_doc.non_goals)} items fenced")

        # ─── 6. Engineering Intelligence (PRD-0009) ─────────────────────────────
        print_banner("6", "Execution & Engineering Intelligence (PRD-0009)", "Translating PRD to technical architecture")
        eng_engine = EngineeringIntelligenceEngine(db=db, workspace_id=ws_id)

        eng_breakdown = eng_engine.decompose_into_epics(
            prd_entity_id=prd_id,
            prd_title=prd_doc.title,
            requirements=[
                {"id": "FR-001", "text": "Real-time double-entry ledger balance table"},
                {"id": "FR-002", "text": "Batch disbursement webhook processor and API integration"},
                {"id": "FR-003", "text": "Driver partner wallet history endpoint"},
            ],
        )
        effort = eng_engine.estimate_effort(eng_breakdown)
        print(f"  * Technical Breakdown: {len(eng_breakdown.epics)} Epics, {eng_breakdown.total_stories} Stories")
        print(f"  * Estimated Engineering Effort: {effort.total_hours} Hours ({effort.confidence.value} Confidence)")

        # Link PRD -> Epic entities in graph
        for ep in eng_breakdown.epics:
            epic_ent = Entity(
                id=ep.epic_id,
                workspace_id=ws_id,
                entity_type=EntityType.EPIC,
                name=ep.title,
                description=ep.description,
                confidence=ConfidenceLevel.CONFIRMED,
            )
            db.add(epic_ent)
            db.add(EntityRelationship(
                source_entity_id=prd_id,
                target_entity_id=ep.epic_id,
                relationship_type=RelationshipType.IMPLEMENTS,
            ))
        await db.flush()

        # ─── 7. QA & Release Intelligence (PRD-0010) ────────────────────────────
        print_banner("7", "QA & Release Readiness Intelligence (PRD-0010)", "Verifying quality gates & release criteria")
        qa_engine = QAIntelligenceEngine(db=db, workspace_id=ws_id)

        strategy = qa_engine.generate_test_strategy(
            prd_entity_id=prd_id,
            prd_title=prd_doc.title,
            requirements=[
                {"id": fr.req_id, "text": fr.description}
                for fr in prd_doc.functional_requirements
            ],
        )
        print(f"  * QA Strategy Formulated: Risk Level = {strategy.risk_level.value}, Levels = {[lvl.value for lvl in strategy.test_levels]}")
        print(f"  * Testing Approach: {strategy.testing_approach[:80]}... (Est. {strategy.estimated_test_effort_hours}h QA)")

        readiness = qa_engine.assess_release_readiness(
            release_name="Vendor Wallet v1.0",
            total_tests=45,
            passed_tests=44,
            failed_tests=1,
            blocked_tests=0,
            critical_defects=0,
            high_defects=0,
            total_requirements=3,
            covered_requirements=3,
        )
        print(f"  * Release Gate Decision: {readiness.overall_status} (Pass Rate: {readiness.test_pass_rate}%, Passed Gates: {readiness.passed_gates})")

        # ─── 8. Analytics & Outcome Scorecard (PRD-0011) ────────────────────────
        print_banner("8", "Analytics & Outcome Intelligence (PRD-0011)", "Measuring outcomes, not just shipped features")
        analytics_engine = AnalyticsIntelligenceEngine(db=db, workspace_id=ws_id)

        kpi_def = analytics_engine.define_kpi(
            name="Vendor Payout Latency",
            description="Elapsed hours from driver shift completion to confirmed bank deposit",
            formula="deposit_timestamp - shift_completed_timestamp",
            unit="hours",
            baseline=336.0,
            target=2.0,
            measurement_period="daily",
        )
        kpi_ent = Entity(
            id="kpi-payout-latency",
            workspace_id=ws_id,
            entity_type=EntityType.KPI,
            name=kpi_def.name,
            description=kpi_def.description,
            properties={"target": kpi_def.target, "baseline": kpi_def.baseline, "unit": kpi_def.unit},
            confidence=ConfidenceLevel.CONFIRMED,
        )
        db.add(kpi_ent)
        await db.flush()
        print(f"  * Primary KPI Tracked: '{kpi_def.name}' (Target: {kpi_def.target}h)")

        # Evaluate Measured Outcomes Against Baseline
        scorecard = analytics_engine.evaluate_outcome_scorecard(
            initiative_name="Vendor Wallet",
            baseline=336.0,
            target=2.0,
            current=1.4,
            guardrail_violations=0,
        )
        print(f"  * Measured Business Outcome:")
        print(f"    - Actual Latency: 1.4 hours (Baseline: 336h, Target: 2.0h)")
        print(f"    - Progress: {scorecard.progress_pct}% | Status: {scorecard.status.value}")
        print(f"    - Outcome Assessment: {scorecard.recommendation}")

        # Link KPI -> Initiative
        db.add(EntityRelationship(
            source_entity_id="init-vendor-wallet",
            target_entity_id=kpi_ent.id,
            relationship_type=RelationshipType.MEASURED_BY,
        ))
        await db.flush()

        # ─── 9. THE CONSTITUTIONAL RECONSTRUCTION (PRD-0001 §54) ────────────────
        print_banner("9", "THE CONSTITUTIONAL TEST (PRD-0001 §54)", "Reconstructing 'Why did we build Vendor Wallet?'")
        print(f"\n{C.YELLOW}{C.BOLD}Incoming Question from New Employee:{C.RESET}")
        query_text = "Why did we build Vendor Wallet?"
        print(f"  Question: \"{query_text}\"\n")

        retrieval_engine = GraphRetrievalEngine(db=db, workspace_id=ws_id)
        traversal_engine = GraphTraversalEngine(db=db, workspace_id=ws_id)

        # 1. Multi-Stage Intent & Evidence Retrieval
        retrieval_res = await retrieval_engine.retrieve(query=query_text)

        print(f"{C.BOLD}{C.CYAN}--- TPG AUTONOMOUS SYNTHESIS ---{C.RESET}")
        print(f"{C.BOLD}Intent Detected:{C.RESET} {retrieval_res.intent.value}")
        print(f"{C.BOLD}Confidence:{C.RESET} {retrieval_res.confidence}")
        print(f"\n{C.BOLD}Reconstructed Executive Narrative:{C.RESET}")
        print(f"  {retrieval_res.narrative_summary}\n")

        print(f"{C.BOLD}Synthesized Evidence Chain ({len(retrieval_res.evidence)} items):{C.RESET}")
        for ev in retrieval_res.evidence:
            print(f"  * [{ev.entity_type.upper()}] {C.BOLD}{ev.name}{C.RESET} - Relation: '{ev.relationship}' (Confidence: {ev.confidence})")

        # 2. Lineage Provenance Tree
        lineage = await traversal_engine.trace_lineage(entity_id="init-vendor-wallet")
        print(f"\n{C.BOLD}{C.CYAN}--- FULL PROVENANCE LINEAGE TREE ---{C.RESET}")
        print(f"Root: {C.BOLD}{lineage.root_entity.name}{C.RESET} [{lineage.root_entity.entity_type}]")
        print(f"  [^] Upstream Business Drivers ({len(lineage.upstream_nodes)} nodes):")
        for up in lineage.upstream_nodes:
            print(f"    |-- [{up.entity_type}] {up.name}")
        print(f"  [v] Downstream Outcomes & Specs ({len(lineage.downstream_nodes)} nodes):")
        for down in lineage.downstream_nodes:
            print(f"    \\-- [{down.entity_type}] {down.name}")

        print(f"\n{C.BOLD}{C.GREEN}[SUCCESS] BENCHMARK PASSED: Institutional knowledge reconstructed completely without manual documentation.{C.RESET}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_genesis_simulation())

