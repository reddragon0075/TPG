"""
QA & Release Intelligence Engine (QRIE) — PRD-0010

Implements:
1. Risk-Based Test Strategy Generation (PRD-0010 §7-§10)
2. Test Case Derivation from Acceptance Criteria (PRD-0010 §11-§16)
3. Quality Risk Assessment — Impact × Likelihood × Uncertainty (PRD-0010 §17-§20)
4. Defect Recording, Classification & Duplicate Detection (PRD-0010 §21-§30)
5. Impact-Based Regression Set Selection (PRD-0010 §31-§35)
6. Evidence-Based Release Readiness Assessment (PRD-0010 §36-§45)
7. Quality Gate Evaluation (PRD-0010 §46-§52)
8. Requirement-to-Test Traceability (PRD-0010 §53-§60)
9. Requirement Coverage Analysis (PRD-0010 §61-§65)
10. Production Incident → Test Gap Tracing (PRD-0010 §66-§72)

Constitutional Principles:
- Quality intelligence must remain traceable to product requirements.
- TPG must never autonomously communicate with external clients.
- Test strategies are evidence-based, never checkbox exercises.
- Defects are connected to requirements, not isolated records.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import (
    Entity,
    EntityRelationship,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
    RelationshipType,
)


# ─── Enums ─────────────────────────────────────────────────────────


class QualityPhase(str, Enum):
    """Quality Assurance Lifecycle (PRD-0010 §7)."""
    NOT_ANALYZED = "NOT_ANALYZED"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    TEST_STRATEGY = "TEST_STRATEGY"
    TEST_DESIGN = "TEST_DESIGN"
    READY_FOR_TEST = "READY_FOR_TEST"
    TESTING = "TESTING"
    DEFECT_TRIAGE = "DEFECT_TRIAGE"
    REGRESSION = "REGRESSION"
    RELEASE_CANDIDATE = "RELEASE_CANDIDATE"
    RELEASE_ASSESSMENT = "RELEASE_ASSESSMENT"
    RELEASED = "RELEASED"
    PRODUCTION_VALIDATION = "PRODUCTION_VALIDATION"
    QUALITY_LEARNING = "QUALITY_LEARNING"


class TestLevel(str, Enum):
    """Test levels / pyramid tiers (PRD-0010 §11)."""
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    API = "API"
    CONTRACT = "CONTRACT"
    E2E = "E2E"
    UI = "UI"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    ACCESSIBILITY = "ACCESSIBILITY"
    COMPATIBILITY = "COMPATIBILITY"
    MIGRATION = "MIGRATION"
    RESILIENCE = "RESILIENCE"
    SMOKE = "SMOKE"
    REGRESSION = "REGRESSION"


class TestResult(str, Enum):
    """Individual test execution result."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    NOT_RUN = "NOT_RUN"
    INCONCLUSIVE = "INCONCLUSIVE"


class DefectSeverity(str, Enum):
    """Defect severity classification (PRD-0010 §23)."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DefectPriority(str, Enum):
    """Defect business priority (may differ from severity)."""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class RiskClassification(str, Enum):
    """Quality risk level (PRD-0010 §17)."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class QualityGateStatus(str, Enum):
    """Release quality gate evaluation result (PRD-0010 §46)."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    OVERRIDDEN = "OVERRIDDEN"
    NOT_EVALUATED = "NOT_EVALUATED"


class ScenarioType(str, Enum):
    """Test scenario category (PRD-0010 §14)."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    BOUNDARY = "BOUNDARY"
    PERMISSION = "PERMISSION"
    CONCURRENCY = "CONCURRENCY"
    ERROR_HANDLING = "ERROR_HANDLING"
    EDGE_CASE = "EDGE_CASE"


# ─── Dataclasses ───────────────────────────────────────────────────


@dataclass
class TestStrategy:
    """Risk-based test strategy for a PRD (PRD-0010 §8)."""
    prd_entity_id: str
    prd_title: str
    risk_level: RiskClassification
    test_levels: list[TestLevel]
    automation_required: bool
    estimated_test_effort_hours: float
    key_risk_areas: list[str]
    testing_approach: str
    exit_criteria: list[str]
    assumptions: list[str]


@dataclass
class TestScenario:
    """A specific test scenario derived from a requirement."""
    scenario_type: ScenarioType
    title: str
    description: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str


@dataclass
class TestCase:
    """A complete test case linked to a requirement (PRD-0010 §12)."""
    test_case_id: str
    requirement_ref: str
    title: str
    test_level: TestLevel
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    scenario_type: ScenarioType
    priority: str = "P1"
    is_automatable: bool = True


@dataclass
class DefectRecord:
    """A defect linked to a requirement (PRD-0010 §22)."""
    title: str
    description: str
    requirement_ref: str | None
    severity: DefectSeverity
    priority: DefectPriority
    steps_to_reproduce: list[str]
    expected_behavior: str
    actual_behavior: str
    environment: str = "staging"
    is_regression: bool = False
    root_cause_category: str | None = None


@dataclass
class DefectClassification:
    """Result of defect classification analysis (PRD-0010 §25)."""
    severity: DefectSeverity
    priority: DefectPriority
    is_regression: bool
    root_cause_category: str
    affected_component: str
    similar_defects: list[str]


@dataclass
class QualityRisk:
    """Quality risk assessment (PRD-0010 §17)."""
    requirement_ref: str
    requirement_text: str
    impact: str       # HIGH, MEDIUM, LOW
    likelihood: str   # HIGH, MEDIUM, LOW
    uncertainty: str  # HIGH, MEDIUM, LOW
    risk_level: RiskClassification
    reasoning: str
    recommended_test_depth: str


@dataclass
class QualityGate:
    """A release quality gate with evaluation criteria (PRD-0010 §46)."""
    gate_name: str
    criteria: str
    status: QualityGateStatus
    evidence: str
    override_reason: str | None = None
    override_approver: str | None = None


@dataclass
class RegressionSet:
    """Impact-based regression test selection (PRD-0010 §31)."""
    change_scope: str
    selected_test_count: int
    test_categories: list[str]
    rationale: str
    estimated_execution_hours: float
    risk_areas: list[str]


@dataclass
class CoverageReport:
    """Requirement-to-test coverage analysis (PRD-0010 §61)."""
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: list[str]
    coverage_percent: float
    coverage_by_level: dict[str, int]
    recommendation: str


@dataclass
class TraceabilityRecord:
    """Requirement → test → result traceability (PRD-0010 §53)."""
    requirement_ref: str
    requirement_text: str
    linked_test_cases: list[str]
    test_results: list[dict[str, str]]
    is_fully_covered: bool


@dataclass
class ReleaseReadiness:
    """Evidence-based release readiness assessment (PRD-0010 §40)."""
    release_name: str
    overall_status: str  # GO, NO_GO, CONDITIONAL_GO
    test_pass_rate: float
    open_critical_defects: int
    open_high_defects: int
    coverage_percent: float
    quality_gates: list[QualityGate]
    passed_gates: int
    failed_gates: int
    risks: list[str]
    recommendation: str


@dataclass
class IncidentTrace:
    """Production incident traced to test gaps (PRD-0010 §66)."""
    incident_description: str
    probable_root_cause: str
    related_requirements: list[str]
    test_gaps: list[str]
    existing_tests: list[str]
    recommended_new_tests: list[str]
    quality_learning: str


# ─── Engine ────────────────────────────────────────────────────────


class QAIntelligenceEngine:
    """
    QA and Release Intelligence Engine.

    Connects Engineering execution to Quality Assurance and Release.
    Generates test strategies from PRDs, derives test cases from
    acceptance criteria, manages defects, and assesses release
    readiness with evidence-based quality gates.

    Constitutional principle (PRD-0010):
    > Quality decisions must be evidence-based, never checkbox exercises.
    > TPG must never autonomously communicate with external clients.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    # ─── Test Strategy ─────────────────────────────────────────

    def generate_test_strategy(
        self,
        prd_entity_id: str,
        prd_title: str,
        requirements: list[dict[str, str]],
    ) -> TestStrategy:
        """
        Generates a risk-based test strategy from PRD requirements
        (PRD-0010 §7-§10).

        Strategy is driven by requirement complexity and risk profile,
        not by a fixed template.
        """
        risk_indicators = 0
        key_risk_areas: list[str] = []
        test_levels: set[TestLevel] = {TestLevel.UNIT, TestLevel.INTEGRATION}

        for req in requirements:
            text = req.get("text", "").lower()

            if any(w in text for w in ["payment", "billing", "financial", "transaction"]):
                risk_indicators += 3
                key_risk_areas.append(f"{req.get('id', '?')}: Financial/payment logic")
                test_levels.add(TestLevel.E2E)
                test_levels.add(TestLevel.SECURITY)

            if any(w in text for w in ["security", "auth", "permission", "rbac", "token"]):
                risk_indicators += 2
                key_risk_areas.append(f"{req.get('id', '?')}: Security/authorization")
                test_levels.add(TestLevel.SECURITY)

            if any(w in text for w in ["api", "endpoint", "rest", "graphql"]):
                risk_indicators += 1
                test_levels.add(TestLevel.API)
                test_levels.add(TestLevel.CONTRACT)

            if any(w in text for w in ["database", "migration", "schema"]):
                risk_indicators += 2
                key_risk_areas.append(f"{req.get('id', '?')}: Data model/migration")
                test_levels.add(TestLevel.MIGRATION)

            if any(w in text for w in ["ui", "frontend", "dashboard"]):
                risk_indicators += 1
                test_levels.add(TestLevel.UI)
                test_levels.add(TestLevel.ACCESSIBILITY)

            if any(w in text for w in ["real-time", "concurrent", "distributed", "performance"]):
                risk_indicators += 2
                key_risk_areas.append(f"{req.get('id', '?')}: Performance/concurrency")
                test_levels.add(TestLevel.PERFORMANCE)
                test_levels.add(TestLevel.RESILIENCE)

        # Determine overall risk level
        if risk_indicators >= 8:
            risk_level = RiskClassification.CRITICAL
        elif risk_indicators >= 5:
            risk_level = RiskClassification.HIGH
        elif risk_indicators >= 2:
            risk_level = RiskClassification.MEDIUM
        else:
            risk_level = RiskClassification.LOW

        # Estimate test effort (rough: 30% of dev time per requirement)
        base_effort = len(requirements) * 8.0  # 8h per requirement
        multiplier = {"CRITICAL": 2.0, "HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.7}
        est_hours = round(base_effort * multiplier.get(risk_level.value, 1.0), 1)

        approach = (
            f"Risk-based testing for '{prd_title}'. "
            f"Risk level: {risk_level.value}. "
            f"Focus on {', '.join(key_risk_areas[:3]) if key_risk_areas else 'general functional coverage'}. "
            f"Test pyramid: {', '.join(sorted(t.value for t in test_levels))}."
        )

        exit_criteria = [
            "All critical and high priority test cases pass",
            "Zero open critical defects",
            f"Requirement coverage ≥ {'95%' if risk_level in (RiskClassification.CRITICAL, RiskClassification.HIGH) else '80%'}",
            "All quality gates evaluated",
            "Regression suite passes",
        ]

        return TestStrategy(
            prd_entity_id=prd_entity_id,
            prd_title=prd_title,
            risk_level=risk_level,
            test_levels=sorted(test_levels, key=lambda t: t.value),
            automation_required=risk_level in (RiskClassification.CRITICAL, RiskClassification.HIGH),
            estimated_test_effort_hours=est_hours,
            key_risk_areas=key_risk_areas,
            testing_approach=approach,
            exit_criteria=exit_criteria,
            assumptions=[
                "Test environment mirrors production configuration",
                "Test data is representative of production volumes",
                "External dependencies are stub-able for isolated testing",
            ],
        )

    # ─── Test Case Derivation ──────────────────────────────────

    def derive_test_cases(
        self,
        requirement_ref: str,
        requirement_text: str,
        acceptance_criteria: list[str] | None = None,
    ) -> list[TestCase]:
        """
        Generates comprehensive test cases from a requirement and its
        acceptance criteria (PRD-0010 §11-§16).

        Produces positive, negative, boundary, permission, concurrency,
        and error scenarios.
        """
        text_lower = requirement_text.lower()
        acceptance_criteria = acceptance_criteria or []
        cases: list[TestCase] = []
        case_idx = 0

        # 1. Positive test case (always)
        case_idx += 1
        cases.append(TestCase(
            test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
            requirement_ref=requirement_ref,
            title=f"Positive: {requirement_text[:60]}",
            test_level=TestLevel.INTEGRATION,
            preconditions=["System is operational", "User is authenticated and authorized"],
            steps=["Execute the primary action as described in the requirement"],
            expected_result="Action completes successfully with expected output",
            scenario_type=ScenarioType.POSITIVE,
        ))

        # 2. Negative / invalid input
        case_idx += 1
        cases.append(TestCase(
            test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
            requirement_ref=requirement_ref,
            title=f"Negative: Invalid input for {requirement_text[:40]}",
            test_level=TestLevel.INTEGRATION,
            preconditions=["System is operational"],
            steps=["Submit request with invalid/missing required fields"],
            expected_result="System returns clear validation error (400) without processing",
            scenario_type=ScenarioType.NEGATIVE,
        ))

        # 3. Permission / authorization
        case_idx += 1
        cases.append(TestCase(
            test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
            requirement_ref=requirement_ref,
            title=f"Permission: Unauthorized access to {requirement_text[:40]}",
            test_level=TestLevel.INTEGRATION,
            preconditions=["User is NOT authenticated or lacks required role"],
            steps=["Attempt action without proper authorization"],
            expected_result="System returns 401/403 and denies access",
            scenario_type=ScenarioType.PERMISSION,
        ))

        # 4. Boundary conditions (if data/numbers involved)
        if any(w in text_lower for w in ["list", "count", "limit", "max", "min", "range", "size", "batch"]):
            case_idx += 1
            cases.append(TestCase(
                test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
                requirement_ref=requirement_ref,
                title=f"Boundary: Edge values for {requirement_text[:40]}",
                test_level=TestLevel.INTEGRATION,
                preconditions=["System is operational"],
                steps=["Test with zero items", "Test with maximum allowed items", "Test with exactly one item"],
                expected_result="System handles all boundary conditions correctly",
                scenario_type=ScenarioType.BOUNDARY,
            ))

        # 5. Error handling
        case_idx += 1
        cases.append(TestCase(
            test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
            requirement_ref=requirement_ref,
            title=f"Error: System failure during {requirement_text[:40]}",
            test_level=TestLevel.INTEGRATION,
            preconditions=["System is operational"],
            steps=["Simulate downstream service failure", "Verify error handling and recovery"],
            expected_result="System returns appropriate error response without data corruption",
            scenario_type=ScenarioType.ERROR_HANDLING,
        ))

        # 6. Concurrency (if applicable)
        if any(w in text_lower for w in ["concurrent", "parallel", "simultaneous", "real-time", "batch"]):
            case_idx += 1
            cases.append(TestCase(
                test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
                requirement_ref=requirement_ref,
                title=f"Concurrency: Parallel execution of {requirement_text[:40]}",
                test_level=TestLevel.PERFORMANCE,
                preconditions=["System is under normal load"],
                steps=["Execute multiple concurrent requests", "Verify data integrity and no race conditions"],
                expected_result="All concurrent requests complete correctly without data corruption",
                scenario_type=ScenarioType.CONCURRENCY,
            ))

        # 7. From acceptance criteria
        for ac_idx, ac_text in enumerate(acceptance_criteria):
            case_idx += 1
            cases.append(TestCase(
                test_case_id=f"TC-{requirement_ref}-{case_idx:03d}",
                requirement_ref=requirement_ref,
                title=f"AC {ac_idx + 1}: {ac_text[:60]}",
                test_level=TestLevel.E2E,
                preconditions=["System is operational", "Test data is prepared"],
                steps=[f"Verify: {ac_text}"],
                expected_result=f"Acceptance criterion met: {ac_text[:60]}",
                scenario_type=ScenarioType.POSITIVE,
                priority="P1",
            ))

        return cases

    # ─── Quality Risk Assessment ───────────────────────────────

    def assess_quality_risk(
        self,
        requirement_ref: str,
        requirement_text: str,
    ) -> QualityRisk:
        """
        Assesses quality risk using Impact × Likelihood × Uncertainty
        (PRD-0010 §17-§20).
        """
        text_lower = requirement_text.lower()

        # Impact assessment
        high_impact_keywords = ["payment", "financial", "security", "auth", "data loss", "compliance", "billing"]
        med_impact_keywords = ["api", "database", "migration", "integration", "notification"]
        impact = "HIGH" if any(w in text_lower for w in high_impact_keywords) else \
                 "MEDIUM" if any(w in text_lower for w in med_impact_keywords) else "LOW"

        # Likelihood assessment (complexity-driven)
        high_likelihood_keywords = ["distributed", "concurrent", "real-time", "migration", "legacy"]
        med_likelihood_keywords = ["complex", "multiple", "batch", "async", "queue"]
        likelihood = "HIGH" if any(w in text_lower for w in high_likelihood_keywords) else \
                     "MEDIUM" if any(w in text_lower for w in med_likelihood_keywords) else "LOW"

        # Uncertainty assessment
        uncertain_keywords = ["maybe", "possibly", "unclear", "tbd", "to be determined", "unknown"]
        brief = len(requirement_text.strip()) < 30
        uncertainty = "HIGH" if any(w in text_lower for w in uncertain_keywords) or brief else \
                      "MEDIUM" if len(requirement_text.strip()) < 80 else "LOW"

        # Risk matrix
        risk_score = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        total = risk_score[impact] + risk_score[likelihood] + risk_score[uncertainty]

        if total >= 8:
            risk_level = RiskClassification.CRITICAL
        elif total >= 6:
            risk_level = RiskClassification.HIGH
        elif total >= 4:
            risk_level = RiskClassification.MEDIUM
        else:
            risk_level = RiskClassification.LOW

        depth_map = {
            RiskClassification.CRITICAL: "Exhaustive testing required — all levels, full regression, performance, security",
            RiskClassification.HIGH: "Deep testing — integration, E2E, security, and regression",
            RiskClassification.MEDIUM: "Standard testing — unit, integration, key E2E scenarios",
            RiskClassification.LOW: "Light testing — unit tests and smoke test",
        }

        reasoning = (
            f"Impact: {impact} (based on requirement scope). "
            f"Likelihood: {likelihood} (based on technical complexity). "
            f"Uncertainty: {uncertainty} (based on requirement clarity). "
            f"Overall risk: {risk_level.value} (score: {total}/9)."
        )

        return QualityRisk(
            requirement_ref=requirement_ref,
            requirement_text=requirement_text,
            impact=impact,
            likelihood=likelihood,
            uncertainty=uncertainty,
            risk_level=risk_level,
            reasoning=reasoning,
            recommended_test_depth=depth_map.get(risk_level, "Standard testing"),
        )

    # ─── Defect Management ─────────────────────────────────────

    async def record_defect(
        self,
        defect: DefectRecord,
    ) -> dict[str, Any]:
        """
        Records a defect in the Knowledge Graph linked to its
        originating requirement (PRD-0010 §21-§24).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized on QAIntelligenceEngine.")

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.DEFECT,
            name=defect.title,
            description=defect.description,
            properties={
                "severity": defect.severity.value,
                "priority": defect.priority.value,
                "steps_to_reproduce": defect.steps_to_reproduce,
                "expected_behavior": defect.expected_behavior,
                "actual_behavior": defect.actual_behavior,
                "environment": defect.environment,
                "is_regression": defect.is_regression,
                "root_cause_category": defect.root_cause_category,
                "requirement_ref": defect.requirement_ref,
                "reported_at": datetime.now(timezone.utc).isoformat(),
            },
            source="qa_engine",
            confidence=ConfidenceLevel.CONFIRMED,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        return {
            "defect_id": entity.id,
            "title": entity.name,
            "severity": defect.severity.value,
            "priority": defect.priority.value,
            "is_regression": defect.is_regression,
        }

    def classify_defect(
        self,
        description: str,
    ) -> DefectClassification:
        """
        Classifies a defect description for severity, priority,
        regression flag, and root cause category (PRD-0010 §25-§28).
        """
        text_lower = description.lower()

        # Severity
        if any(w in text_lower for w in ["crash", "data loss", "security breach", "system down", "unable to login"]):
            severity = DefectSeverity.CRITICAL
        elif any(w in text_lower for w in ["error", "500", "broken", "not working", "fails"]):
            severity = DefectSeverity.HIGH
        elif any(w in text_lower for w in ["incorrect", "wrong", "unexpected", "missing"]):
            severity = DefectSeverity.MEDIUM
        else:
            severity = DefectSeverity.LOW

        # Priority (roughly tracks severity but can differ)
        priority_map = {
            DefectSeverity.CRITICAL: DefectPriority.P0,
            DefectSeverity.HIGH: DefectPriority.P1,
            DefectSeverity.MEDIUM: DefectPriority.P2,
            DefectSeverity.LOW: DefectPriority.P3,
        }
        priority = priority_map[severity]

        # Regression detection
        is_regression = any(w in text_lower for w in ["regression", "used to work", "worked before", "previously", "broke after"])

        # Root cause category
        if any(w in text_lower for w in ["null", "exception", "undefined", "type error"]):
            root_cause = "Code Defect"
        elif any(w in text_lower for w in ["timeout", "slow", "latency", "performance"]):
            root_cause = "Performance"
        elif any(w in text_lower for w in ["config", "setting", "environment", "variable"]):
            root_cause = "Configuration"
        elif any(w in text_lower for w in ["data", "database", "migration", "corrupt"]):
            root_cause = "Data Issue"
        elif any(w in text_lower for w in ["ui", "css", "display", "layout", "alignment"]):
            root_cause = "UI/UX"
        else:
            root_cause = "Functional Defect"

        # Affected component
        if any(w in text_lower for w in ["api", "endpoint", "rest"]):
            component = "API Layer"
        elif any(w in text_lower for w in ["database", "query", "sql"]):
            component = "Database"
        elif any(w in text_lower for w in ["ui", "frontend", "page", "screen"]):
            component = "Frontend"
        elif any(w in text_lower for w in ["auth", "login", "permission"]):
            component = "Authentication"
        else:
            component = "Service Layer"

        return DefectClassification(
            severity=severity,
            priority=priority,
            is_regression=is_regression,
            root_cause_category=root_cause,
            affected_component=component,
            similar_defects=[],  # Would search graph in production
        )

    async def detect_duplicate_defect(
        self,
        description: str,
    ) -> list[dict[str, Any]]:
        """
        Searches the Knowledge Graph for similar existing defects
        (PRD-0010 §29, §30).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        keywords = [w for w in description.lower().split() if len(w) > 3][:5]

        results = []
        for kw in keywords:
            stmt = (
                select(Entity)
                .where(Entity.workspace_id == self.workspace_id)
                .where(Entity.entity_type == EntityType.DEFECT)
                .where(Entity.status == EntityStatus.ACTIVE)
                .where(Entity.name.ilike(f"%{kw}%"))
                .limit(5)
            )
            res = await self.db.execute(stmt)
            for entity in res.scalars().all():
                if entity.id not in [r["entity_id"] for r in results]:
                    results.append({
                        "entity_id": entity.id,
                        "title": entity.name,
                        "severity": entity.properties.get("severity", "UNKNOWN"),
                        "similarity": "keyword_match",
                    })

        return results[:10]

    # ─── Regression Set ────────────────────────────────────────

    def generate_regression_set(
        self,
        change_scope: str,
        total_test_count: int = 100,
    ) -> RegressionSet:
        """
        Selects impact-based regression test set from change analysis
        (PRD-0010 §31-§35).
        """
        text_lower = change_scope.lower()
        categories: list[str] = ["Smoke Tests"]
        risk_areas: list[str] = []
        selection_ratio = 0.2  # Default: 20% of total tests

        if any(w in text_lower for w in ["api", "endpoint"]):
            categories.append("API Contract Tests")
            risk_areas.append("API backward compatibility")
            selection_ratio += 0.1

        if any(w in text_lower for w in ["database", "migration", "schema"]):
            categories.append("Data Integrity Tests")
            categories.append("Migration Verification Tests")
            risk_areas.append("Data model integrity")
            selection_ratio += 0.15

        if any(w in text_lower for w in ["auth", "security", "permission"]):
            categories.append("Security / Authorization Tests")
            risk_areas.append("Authorization boundary")
            selection_ratio += 0.1

        if any(w in text_lower for w in ["ui", "frontend"]):
            categories.append("UI Smoke Tests")
            categories.append("Accessibility Tests")
            risk_areas.append("Visual regression")
            selection_ratio += 0.1

        if any(w in text_lower for w in ["payment", "financial", "billing"]):
            categories.append("Financial Integration Tests")
            risk_areas.append("Financial transaction integrity")
            selection_ratio += 0.2

        selected_count = min(total_test_count, max(5, int(total_test_count * min(selection_ratio, 1.0))))
        est_hours = round(selected_count * 0.1, 1)  # ~6 min per test

        rationale = (
            f"Selected {selected_count}/{total_test_count} tests based on change scope: '{change_scope[:60]}'. "
            f"Risk areas: {', '.join(risk_areas) if risk_areas else 'general'}. "
            f"Test categories: {', '.join(categories)}."
        )

        return RegressionSet(
            change_scope=change_scope,
            selected_test_count=selected_count,
            test_categories=categories,
            rationale=rationale,
            estimated_execution_hours=est_hours,
            risk_areas=risk_areas,
        )

    # ─── Release Readiness ─────────────────────────────────────

    def assess_release_readiness(
        self,
        release_name: str,
        total_tests: int,
        passed_tests: int,
        failed_tests: int,
        blocked_tests: int,
        critical_defects: int,
        high_defects: int,
        total_requirements: int,
        covered_requirements: int,
    ) -> ReleaseReadiness:
        """
        Evidence-based release readiness assessment with quality gates
        (PRD-0010 §36-§45).
        """
        pass_rate = round((passed_tests / max(total_tests, 1)) * 100, 1)
        coverage = round((covered_requirements / max(total_requirements, 1)) * 100, 1)

        # Evaluate quality gates
        gates: list[QualityGate] = []

        # Gate 1: Test pass rate ≥ 95%
        gates.append(QualityGate(
            gate_name="Test Pass Rate",
            criteria="≥ 95% of test cases pass",
            status=QualityGateStatus.PASSED if pass_rate >= 95 else QualityGateStatus.FAILED,
            evidence=f"Pass rate: {pass_rate}% ({passed_tests}/{total_tests})",
        ))

        # Gate 2: Zero critical defects
        gates.append(QualityGate(
            gate_name="Critical Defects",
            criteria="Zero open critical defects",
            status=QualityGateStatus.PASSED if critical_defects == 0 else QualityGateStatus.FAILED,
            evidence=f"Open critical defects: {critical_defects}",
        ))

        # Gate 3: High defects ≤ 2
        gates.append(QualityGate(
            gate_name="High Defects",
            criteria="≤ 2 open high-severity defects",
            status=QualityGateStatus.PASSED if high_defects <= 2 else QualityGateStatus.FAILED,
            evidence=f"Open high defects: {high_defects}",
        ))

        # Gate 4: Requirement coverage ≥ 80%
        gates.append(QualityGate(
            gate_name="Requirement Coverage",
            criteria="≥ 80% requirement coverage",
            status=QualityGateStatus.PASSED if coverage >= 80 else QualityGateStatus.FAILED,
            evidence=f"Coverage: {coverage}% ({covered_requirements}/{total_requirements})",
        ))

        # Gate 5: No blocked tests
        gates.append(QualityGate(
            gate_name="Blocked Tests",
            criteria="Zero blocked test cases",
            status=QualityGateStatus.PASSED if blocked_tests == 0 else QualityGateStatus.FAILED,
            evidence=f"Blocked tests: {blocked_tests}",
        ))

        passed_gates = sum(1 for g in gates if g.status == QualityGateStatus.PASSED)
        failed_gates = sum(1 for g in gates if g.status == QualityGateStatus.FAILED)

        # Determine overall status
        if failed_gates == 0:
            overall = "GO"
            recommendation = f"Release '{release_name}' is recommended for deployment. All quality gates passed."
        elif critical_defects > 0 or pass_rate < 85:
            overall = "NO_GO"
            recommendation = (
                f"Release '{release_name}' is NOT recommended for deployment. "
                f"{failed_gates} quality gate(s) failed. "
                f"Critical blockers: {critical_defects} critical defects, {pass_rate}% pass rate."
            )
        else:
            overall = "CONDITIONAL_GO"
            recommendation = (
                f"Release '{release_name}' may proceed with conditions. "
                f"{failed_gates} quality gate(s) failed but no critical blockers. "
                f"Recommend stakeholder sign-off before deployment."
            )

        risks = []
        if critical_defects > 0:
            risks.append(f"{critical_defects} critical defect(s) unresolved")
        if pass_rate < 95:
            risks.append(f"Test pass rate ({pass_rate}%) below threshold")
        if coverage < 80:
            risks.append(f"Requirement coverage ({coverage}%) below threshold")
        if blocked_tests > 0:
            risks.append(f"{blocked_tests} test case(s) blocked — potential hidden risk")

        return ReleaseReadiness(
            release_name=release_name,
            overall_status=overall,
            test_pass_rate=pass_rate,
            open_critical_defects=critical_defects,
            open_high_defects=high_defects,
            coverage_percent=coverage,
            quality_gates=gates,
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            risks=risks,
            recommendation=recommendation,
        )

    # ─── Quality Gate Evaluation ───────────────────────────────

    def evaluate_quality_gates(
        self,
        gates: list[QualityGate],
    ) -> dict[str, Any]:
        """
        Evaluates a set of quality gates and returns summary
        (PRD-0010 §46-§52).
        """
        passed = [g for g in gates if g.status == QualityGateStatus.PASSED]
        failed = [g for g in gates if g.status == QualityGateStatus.FAILED]
        overridden = [g for g in gates if g.status == QualityGateStatus.OVERRIDDEN]

        return {
            "total_gates": len(gates),
            "passed": len(passed),
            "failed": len(failed),
            "overridden": len(overridden),
            "all_passed": len(failed) == 0,
            "failed_gate_names": [g.gate_name for g in failed],
            "overridden_gate_names": [g.gate_name for g in overridden],
        }

    # ─── Traceability ──────────────────────────────────────────

    async def trace_requirement_to_tests(
        self,
        requirement_entity_id: str,
    ) -> TraceabilityRecord:
        """
        Returns full traceability: requirement → test cases → results
        (PRD-0010 §53-§60).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        # Load requirement
        req_stmt = select(Entity).where(Entity.id == requirement_entity_id)
        req_result = await self.db.execute(req_stmt)
        req_entity = req_result.scalar_one_or_none()
        if not req_entity:
            return TraceabilityRecord(
                requirement_ref=requirement_entity_id,
                requirement_text="NOT FOUND",
                linked_test_cases=[],
                test_results=[],
                is_fully_covered=False,
            )

        # Find test cases linked to this requirement
        test_stmt = (
            select(Entity)
            .join(EntityRelationship, EntityRelationship.source_entity_id == Entity.id)
            .where(EntityRelationship.target_entity_id == requirement_entity_id)
            .where(EntityRelationship.relationship_type == RelationshipType.TESTS)
            .where(Entity.workspace_id == self.workspace_id)
        )
        test_result = await self.db.execute(test_stmt)
        test_entities = test_result.scalars().all()

        linked = [te.name for te in test_entities]
        results = [
            {"test_case": te.name, "result": te.properties.get("result", "NOT_RUN")}
            for te in test_entities
        ]

        return TraceabilityRecord(
            requirement_ref=req_entity.name,
            requirement_text=req_entity.description or "",
            linked_test_cases=linked,
            test_results=results,
            is_fully_covered=len(linked) > 0,
        )

    # ─── Coverage Analysis ─────────────────────────────────────

    def analyze_test_coverage(
        self,
        requirements: list[dict[str, str]],
        tested_requirements: list[str],
    ) -> CoverageReport:
        """
        Analyzes requirement-to-test coverage (not code coverage)
        (PRD-0010 §61-§65).
        """
        total = len(requirements)
        covered = len(tested_requirements)
        uncovered = [
            req.get("id", "?")
            for req in requirements
            if req.get("id", "") not in tested_requirements
        ]

        coverage_pct = round((covered / max(total, 1)) * 100, 1)

        if coverage_pct >= 95:
            recommendation = "Excellent coverage. Proceed with confidence."
        elif coverage_pct >= 80:
            recommendation = f"Good coverage. Consider adding tests for {len(uncovered)} uncovered requirements."
        elif coverage_pct >= 60:
            recommendation = f"Moderate coverage. {len(uncovered)} requirements lack test coverage — prioritize high-risk items."
        else:
            recommendation = f"Insufficient coverage ({coverage_pct}%). {len(uncovered)} requirements untested. Block release until coverage improves."

        return CoverageReport(
            total_requirements=total,
            covered_requirements=covered,
            uncovered_requirements=uncovered,
            coverage_percent=coverage_pct,
            coverage_by_level={"integration": covered, "e2e": 0},
            recommendation=recommendation,
        )

    # ─── Production Incident Tracing ───────────────────────────

    def trace_production_incident(
        self,
        incident_description: str,
    ) -> IncidentTrace:
        """
        Traces a production incident back to test gaps and generates
        quality learning (PRD-0010 §66-§72).
        """
        text_lower = incident_description.lower()

        # Identify probable root cause
        if any(w in text_lower for w in ["null", "exception", "crash", "500"]):
            root_cause = "Unhandled exception / null reference in service layer"
        elif any(w in text_lower for w in ["timeout", "slow", "latency", "performance"]):
            root_cause = "Performance degradation under load"
        elif any(w in text_lower for w in ["auth", "permission", "unauthorized"]):
            root_cause = "Authorization bypass or misconfiguration"
        elif any(w in text_lower for w in ["data", "corrupt", "missing", "wrong value"]):
            root_cause = "Data integrity issue"
        else:
            root_cause = "Functional defect — behavior does not match requirement"

        # Identify test gaps
        test_gaps = []
        recommended_tests = []

        if "exception" in text_lower or "crash" in text_lower:
            test_gaps.append("Missing negative/error-handling test cases")
            recommended_tests.append("Add error-handling test for the affected code path")

        if "performance" in text_lower or "timeout" in text_lower:
            test_gaps.append("No performance test covering this scenario")
            recommended_tests.append("Add performance test with realistic load profile")

        if "auth" in text_lower or "permission" in text_lower:
            test_gaps.append("Insufficient authorization test coverage")
            recommended_tests.append("Add permission boundary tests for all roles")

        if "data" in text_lower or "corrupt" in text_lower:
            test_gaps.append("Missing data validation test cases")
            recommended_tests.append("Add data integrity tests with edge-case inputs")

        if not test_gaps:
            test_gaps.append("Test coverage appears adequate — investigate flaky tests or environment differences")
            recommended_tests.append("Review test environment parity with production")

        quality_learning = (
            f"Production incident: '{incident_description[:60]}'. "
            f"Root cause: {root_cause}. "
            f"Test gaps identified: {len(test_gaps)}. "
            f"Action: Add {len(recommended_tests)} new test(s) to prevent recurrence."
        )

        return IncidentTrace(
            incident_description=incident_description,
            probable_root_cause=root_cause,
            related_requirements=[],  # Would search graph in production
            test_gaps=test_gaps,
            existing_tests=[],  # Would search graph in production
            recommended_new_tests=recommended_tests,
            quality_learning=quality_learning,
        )
