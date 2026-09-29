"""
PRD & Product Specification Engine — PRD-0008

Implements:
1. PRD Readiness Gate & Assessment (PRD-0008 §7, §8, §9)
2. Constitutional PRD Structuring & Drafting (PRD-0008 §10-§33)
3. Non-Goals / Scope Fencing enforcement
4. Functional Requirement & Gherkin Acceptance Criteria generation
5. Markdown Rendering
6. Immutable Knowledge Graph Archival & Version Management
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import re
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


class PRDReadinessLevel(str, Enum):
    NOT_READY = "NOT_READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    READY = "READY"
    EXECUTION_READY = "EXECUTION_READY"


class PRDStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class FunctionalRequirement:
    req_id: str           # e.g. "FR-001"
    title: str
    description: str
    edge_cases: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)


@dataclass
class AcceptanceCriterion:
    scenario: str
    given: str
    when: str
    then: str


@dataclass
class PRDScope:
    mvp: list[str] = field(default_factory=list)
    v1: list[str] = field(default_factory=list)
    future: list[str] = field(default_factory=list)
    non_goals: list[str] = field(default_factory=list)


@dataclass
class PRDReadinessAssessment:
    level: PRDReadinessLevel
    overall_score: float  # 0.0 to 1.0
    dimension_scores: dict[str, str]  # e.g. {"problem": "READY", "evidence": "MEDIUM"}
    missing_critical_items: list[str]
    readiness_notes: str


@dataclass
class PRDDocument:
    title: str
    initiative_id: str | None
    decision_id: str | None
    version: int
    status: PRDStatus
    executive_summary: dict[str, str]
    problem_statement: str
    evidence: list[str]
    opportunity: str
    strategic_alignment: dict[str, str]
    target_personas: list[dict[str, Any]]
    jobs_to_be_done: list[str]
    goals: list[str]
    non_goals: list[str]
    scope: PRDScope
    functional_requirements: list[FunctionalRequirement]
    acceptance_criteria: list[AcceptanceCriterion]
    technical_constraints: list[str]
    security_and_compliance: list[str]
    success_metrics: list[dict[str, Any]]
    risks_and_mitigations: list[dict[str, str]]
    open_questions: list[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PRDSpecificationEngine:
    """
    Autonomous PRD and Specification Engine conforming to PRD-0008.
    Converts upstream organizational intelligence (Problems, Requirements, Decisions)
    into execution-ready product specifications.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    def assess_readiness(
        self,
        problem: str | None,
        requirements: list[str],
        decision_rationale: str | None = None,
        evidence: list[str] | None = None,
        success_metric: str | None = None,
    ) -> PRDReadinessAssessment:
        """
        Evaluates whether sufficient organizational intelligence exists to draft an execution-ready PRD.
        (PRD-0008 §7, §8, §9)
        """
        missing = []
        dim = {}

        # 1. Problem Check
        if problem and len(problem.strip()) > 15:
            dim["problem"] = "READY"
        else:
            dim["problem"] = "NOT_READY"
            missing.append("Validated Problem Statement is missing or too brief")

        # 2. Requirements Check
        if requirements and len(requirements) >= 1:
            dim["requirements"] = "READY" if len(requirements) >= 3 else "PARTIAL"
        else:
            dim["requirements"] = "NOT_READY"
            missing.append("No specific functional capabilities/requirements provided")

        # 3. Decision Check
        if decision_rationale and len(decision_rationale.strip()) > 10:
            dim["decision"] = "READY"
        else:
            dim["decision"] = "PARTIAL"
            missing.append("Executive decision rationale / ADR not linked")

        # 4. Evidence Check
        if evidence and len(evidence) >= 1:
            dim["evidence"] = "READY"
        else:
            dim["evidence"] = "LOW"
            missing.append("Customer/Data evidence citations missing (PRD-0001 P3)")

        # 5. Success Metric Check
        if success_metric:
            dim["metrics"] = "READY"
        else:
            dim["metrics"] = "PARTIAL"
            missing.append("Quantifiable target success KPI not specified")

        # Calculate Readiness Level
        if not problem or not requirements:
            level = PRDReadinessLevel.NOT_READY
            score = 0.2
        elif len(missing) >= 3:
            level = PRDReadinessLevel.PARTIALLY_READY
            score = 0.5
        elif len(missing) >= 1:
            level = PRDReadinessLevel.READY
            score = 0.75
        else:
            level = PRDReadinessLevel.EXECUTION_READY
            score = 1.0

        notes = (
            f"Readiness Status: {level.value}. "
            + (f"Prerequisites met with {len(missing)} warnings." if missing else "All PRD prerequisites satisfied.")
        )

        return PRDReadinessAssessment(
            level=level,
            overall_score=score,
            dimension_scores=dim,
            missing_critical_items=missing,
            readiness_notes=notes,
        )

    def generate_prd(
        self,
        title: str,
        problem: str,
        raw_requirements: list[str],
        decision_rationale: str | None = None,
        evidence: list[str] | None = None,
        target_personas: list[str] | None = None,
        non_goals: list[str] | None = None,
        success_metric: str | None = None,
        initiative_id: str | None = None,
        decision_id: str | None = None,
        version: int = 1,
    ) -> PRDDocument:
        """
        Synthesizes a complete constitutional PRD document conforming to PRD-0008 §10.
        """
        evidence = evidence or ["Internal stakeholder request", "Discovery observation notes"]
        personas_list = target_personas or ["Enterprise Administrator", "End Operator"]
        non_goals_list = non_goals or [
            "External public API access (deferred to v2)",
            "Custom report builder / drag-and-drop designer",
            "Third-party webhook integrations in MVP",
        ]

        # 1. Executive Summary
        exec_summary = {
            "what": f"Implement {title} to automate critical product workflows and eliminate friction.",
            "why": problem,
            "who": ", ".join(personas_list),
            "outcome": success_metric or "50% reduction in operational latency and error rates.",
            "scope": "MVP release focused on core functional flow.",
            "status": "DRAFT",
        }

        # 2. Strategic Alignment
        strat = {
            "theme": "Operational Excellence & Retention",
            "objective": "Eliminate critical enterprise operational friction",
            "decision_context": decision_rationale or "Approved based on high impact-to-effort ratio.",
        }

        # 3. Personas
        structured_personas = [
            {
                "role": p,
                "responsibilities": f"Executes daily workflows related to {title}.",
                "pain_points": [problem],
                "frequency": "Daily",
            }
            for p in personas_list
        ]

        # 4. Jobs To Be Done
        jtbd = [
            f"When managing operational tasks, I want to {title.lower()} so that I can eliminate manual errors and save turnaround time."
        ]

        # 5. Goals & Non-Goals
        goals = [
            f"Deliver reliable, audited workflow for {title}",
            success_metric or "Reduce turnaround time by at least 40%",
            "Zero data loss or unhandled transaction exceptions",
        ]

        # 6. Scope
        scope = PRDScope(
            mvp=raw_requirements[:3] if raw_requirements else [f"Core engine for {title}"],
            v1=raw_requirements[3:6] if len(raw_requirements) > 3 else ["Audit logging & notifications"],
            future=["Self-service configuration", "Advanced analytics dashboard"],
            non_goals=non_goals_list,
        )

        # 7. Functional Requirements with Edge Cases
        func_reqs: list[FunctionalRequirement] = []
        for idx, req_text in enumerate(raw_requirements, 1):
            req_id = f"FR-{idx:03d}"
            func_reqs.append(
                FunctionalRequirement(
                    req_id=req_id,
                    title=f"{req_text.split('.')[0][:60]}",
                    description=req_text,
                    edge_cases=[
                        "Network timeout during external request -> Must retry with exponential backoff",
                        "Duplicate payload submission -> Idempotency key must prevent duplicate action",
                    ],
                    failure_modes=[
                        "Database connection drop -> Return 503 Service Unavailable with Retry-After header",
                    ],
                )
            )

        # 8. Acceptance Criteria (Gherkin syntax)
        acceptance: list[AcceptanceCriterion] = []
        for idx, fr in enumerate(func_reqs, 1):
            acceptance.append(
                AcceptanceCriterion(
                    scenario=f"Successful execution of {fr.title}",
                    given="an authorized user with valid session credentials",
                    when=f"the user triggers action for '{fr.title}'",
                    then=f"the system executes successfully, returns 200 OK, and persists state in the database",
                )
            )

        # 9. Technical Constraints & Security
        constraints = [
            "All mutations must be wrapped in atomic database transactions",
            "Response latency SLA: 95th percentile under 250ms",
            "Multi-tenant workspace isolation must be strictly enforced at repository query layer",
        ]
        security = [
            "Role-Based Access Control (RBAC) authorization required on every mutation",
            "Zero PII logged in application traces",
            "Audit event emitted for every create/update/archive operation",
        ]

        # 10. Success Metrics
        metrics = [
            {
                "kpi": success_metric or "Operational turnaround time",
                "baseline": "Manual / 24-48 hours",
                "target": "< 5 minutes",
            }
        ]

        # 11. Risks & Mitigations
        risks = [
            {
                "risk": "User resistance to new automated workflow",
                "mitigation": "Parallel run period with clear visual status indicators and rollback flag",
            },
            {
                "risk": "Edge case data anomalies in legacy records",
                "mitigation": "Pre-flight validation step with explicit error reporting",
            },
        ]

        open_questions = [
            "What is the maximum expected batch volume during peak hours?",
            "Are there country-specific regulatory constraints for historical audit retention?",
        ]

        return PRDDocument(
            title=title,
            initiative_id=initiative_id,
            decision_id=decision_id,
            version=version,
            status=PRDStatus.DRAFT,
            executive_summary=exec_summary,
            problem_statement=problem,
            evidence=evidence,
            opportunity=f"By addressing this problem, the team can eliminate manual overhead and build scalable foundational capability.",
            strategic_alignment=strat,
            target_personas=structured_personas,
            jobs_to_be_done=jtbd,
            goals=goals,
            non_goals=non_goals_list,
            scope=scope,
            functional_requirements=func_reqs,
            acceptance_criteria=acceptance,
            technical_constraints=constraints,
            security_and_compliance=security,
            success_metrics=metrics,
            risks_and_mitigations=risks,
            open_questions=open_questions,
        )

    def render_markdown(self, prd: PRDDocument) -> str:
        """
        Renders the PRD document into standard Markdown matching PRD-0008 specifications.
        """
        lines = [
            f"# PRD: {prd.title}",
            "",
            f"**Version:** v{prd.version} | **Status:** {prd.status.value} | **Initiative:** {prd.initiative_id or 'Unassigned'}",
            f"**Created:** {prd.created_at}",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            f"* **What:** {prd.executive_summary.get('what', '')}",
            f"* **Why:** {prd.executive_summary.get('why', '')}",
            f"* **Who:** {prd.executive_summary.get('who', '')}",
            f"* **Target Outcome:** {prd.executive_summary.get('outcome', '')}",
            f"* **Scope:** {prd.executive_summary.get('scope', '')}",
            "",
            "## 2. Problem Statement & Evidence",
            f"> {prd.problem_statement}",
            "",
            "**Supporting Evidence:**",
        ]
        for ev in prd.evidence:
            lines.append(f"- {ev}")

        lines.extend([
            "",
            "## 3. Scope Fencing (Goals vs. Non-Goals)",
            "### Goals",
        ])
        for g in prd.goals:
            lines.append(f"- [x] {g}")

        lines.extend([
            "",
            "### Explicit Non-Goals (Scope Boundary)",
        ])
        for ng in prd.non_goals:
            lines.append(f"- [ ] **OUT OF SCOPE:** {ng}")

        lines.extend([
            "",
            "## 4. Functional Requirements",
        ])
        for fr in prd.functional_requirements:
            lines.append(f"### {fr.req_id}: {fr.title}")
            lines.append(f"{fr.description}")
            if fr.edge_cases:
                lines.append("**Edge Cases:**")
                for ec in fr.edge_cases:
                    lines.append(f"  * {ec}")
            lines.append("")

        lines.extend([
            "## 5. Acceptance Criteria (Gherkin)",
        ])
        for ac in prd.acceptance_criteria:
            lines.append(f"#### Scenario: {ac.scenario}")
            lines.append(f"* **Given** {ac.given}")
            lines.append(f"* **When** {ac.when}")
            lines.append(f"* **Then** {ac.then}")
            lines.append("")

        lines.extend([
            "## 6. Technical & Security Constraints",
            "**Technical:**",
        ])
        for tc in prd.technical_constraints:
            lines.append(f"- {tc}")

        lines.extend([
            "",
            "**Security & Compliance:**",
        ])
        for sc in prd.security_and_compliance:
            lines.append(f"- {sc}")

        lines.extend([
            "",
            "## 7. Success Metrics & KPIs",
        ])
        for sm in prd.success_metrics:
            lines.append(f"- **{sm.get('kpi')}:** Baseline: `{sm.get('baseline')}` → Target: `{sm.get('target')}`")

        lines.extend([
            "",
            "## 8. Risks & Mitigations",
        ])
        for rm in prd.risks_and_mitigations:
            lines.append(f"* **Risk:** {rm.get('risk')}  ")
            lines.append(f"  *Mitigation:* {rm.get('mitigation')}")

        lines.extend([
            "",
            "## 9. Open Questions",
        ])
        for oq in prd.open_questions:
            lines.append(f"- [ ] {oq}")

        return "\n".join(lines)

    async def save_prd(
        self,
        prd: PRDDocument,
        markdown_content: str | None = None,
    ) -> dict[str, Any]:
        """
        Saves PRD as an immutable Entity in the Knowledge Graph with version management.
        Creates SPECIFIES and IMPLEMENTS relationships to parent initiative and requirements.
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized on PRDSpecificationEngine.")

        md = markdown_content or self.render_markdown(prd)

        # Check existing PRDs with same title to increment version
        count_stmt = (
            select(func.count(Entity.id))
            .where(Entity.workspace_id == self.workspace_id)
            .where(Entity.entity_type == EntityType.PRD)
            .where(Entity.name == prd.title)
        )
        count_res = await self.db.execute(count_stmt)
        existing_versions = count_res.scalar() or 0
        new_version = existing_versions + 1

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.PRD,
            name=prd.title,
            description=prd.problem_statement,
            properties={
                "version": new_version,
                "status": prd.status.value,
                "executive_summary": prd.executive_summary,
                "non_goals": prd.non_goals,
                "goals": prd.goals,
                "functional_requirements_count": len(prd.functional_requirements),
                "acceptance_criteria_count": len(prd.acceptance_criteria),
                "markdown": md,
            },
            source="prd_engine",
            confidence=ConfidenceLevel.CONFIRMED,
            status=EntityStatus.ACTIVE,
            version=new_version,
        )
        self.db.add(entity)
        await self.db.flush()

        # Link to Initiative (SPECIFIES)
        if prd.initiative_id:
            rel = EntityRelationship(
                source_entity_id=prd.initiative_id,
                target_entity_id=entity.id,
                relationship_type=RelationshipType.CONTAINS,
                properties={"purpose": "initiative_specifies_prd"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel)

        # Link to Decision (IMPLEMENTS)
        if prd.decision_id:
            rel_dec = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=prd.decision_id,
                relationship_type=RelationshipType.IMPLEMENTS,
                properties={"purpose": "prd_implements_decision"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel_dec)

        await self.db.flush()

        return {
            "prd_id": entity.id,
            "title": entity.name,
            "version": new_version,
            "status": prd.status.value,
            "markdown_length": len(md),
        }
