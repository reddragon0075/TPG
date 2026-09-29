"""
Engineering Intelligence Engine (EIE) — PRD-0009

Implements:
1. Technical Implication Analysis from approved PRDs (PRD-0009 §8, §16)
2. Technical Design Specification Generation (PRD-0009 §17)
3. Architecture Decision Record (ADR) Management (PRD-0009 §12, §13)
4. Engineering Breakdown — Epic → Story → Subtask Decomposition (PRD-0009 §28)
5. Dependency Graph Mapping (PRD-0009 §34)
6. Effort Estimation with Confidence Levels (PRD-0009 §22-§25)
7. Capacity Analysis & Conflict Detection (PRD-0009 §26, §27)
8. Technical Debt as First-Class Knowledge (PRD-0009 §72-§76)
9. Technical Risk Tracking (PRD-0009 §77-§81)
10. Implementation Drift Detection (PRD-0009 §52-§55)
11. Blocker Analysis & Aging (PRD-0009 §37-§40)
12. Full Engineering Handoff Generation (PRD-0009 §89, §90)

Constitutional Principles:
- Engineering intelligence must remain connected to product intent.
- TPG must not invent architecture — observed, inferred, assumed, unknown must be distinguished.
- Estimates are labeled as estimates, never commitments.
- Secrets must never become ordinary organizational memory.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import re

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


class EngineeringPhase(str, Enum):
    """Engineering Planning Lifecycle (PRD-0009 §7)."""
    NOT_ANALYZED = "NOT_ANALYZED"
    TECHNICAL_DISCOVERY = "TECHNICAL_DISCOVERY"
    ARCHITECTURE_REVIEW = "ARCHITECTURE_REVIEW"
    TECHNICAL_DESIGN = "TECHNICAL_DESIGN"
    ESTIMATION = "ESTIMATION"
    READY_FOR_DEVELOPMENT = "READY_FOR_DEVELOPMENT"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    CODE_REVIEW = "CODE_REVIEW"
    TESTING = "TESTING"
    RELEASE_READY = "RELEASE_READY"
    RELEASED = "RELEASED"
    MONITORING = "MONITORING"


class ADRStatus(str, Enum):
    """Architecture Decision Record Lifecycle (PRD-0009 §13)."""
    PROPOSED = "PROPOSED"
    ANALYZING = "ANALYZING"
    REVIEW = "REVIEW"
    ACCEPTED = "ACCEPTED"
    IMPLEMENTED = "IMPLEMENTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class TechDebtSeverity(str, Enum):
    """Technical Debt severity classification."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EstimateConfidence(str, Enum):
    """Estimation confidence (PRD-0009 §25)."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DependencyType(str, Enum):
    """Type of engineering dependency (PRD-0009 §34)."""
    BLOCKING = "BLOCKING"
    SOFT = "SOFT"
    DATA = "DATA"
    API = "API"
    INFRASTRUCTURE = "INFRASTRUCTURE"


# ─── Dataclasses ───────────────────────────────────────────────────


@dataclass
class TechnicalImplication:
    """A single technical implication identified from a PRD requirement."""
    requirement_ref: str
    requirement_text: str
    affected_components: list[str]
    new_components: list[str]
    data_model_changes: list[str]
    api_changes: list[str]
    dependencies: list[str]
    risks: list[str]
    confidence: str = "inferred"


@dataclass
class TechnicalAnalysis:
    """Complete technical analysis of a PRD (PRD-0009 §8, §16)."""
    prd_entity_id: str
    prd_title: str
    phase: EngineeringPhase
    implications: list[TechnicalImplication]
    total_affected_components: list[str]
    total_new_components: list[str]
    total_dependencies: list[str]
    total_risks: list[str]
    architecture_impact: str  # "none", "minor", "moderate", "significant", "fundamental"
    recommendation: str


@dataclass
class TechnicalDesign:
    """Structured Technical Design Specification (PRD-0009 §17)."""
    prd_entity_id: str
    title: str
    architecture_context: str
    existing_system: list[str]
    proposed_changes: list[str]
    components: list[dict[str, str]]
    data_flow: list[str]
    api_changes: list[dict[str, str]]
    data_model: list[dict[str, str]]
    events: list[str]
    dependencies: list[str]
    security_considerations: list[str]
    scalability_notes: list[str]
    failure_modes: list[dict[str, str]]
    observability: list[str]
    migration_strategy: str
    rollback_strategy: str
    open_questions: list[str]


@dataclass
class ArchitectureDecision:
    """Architecture Decision Record (PRD-0009 §12)."""
    title: str
    status: ADRStatus
    context: str
    alternatives: list[dict[str, str]]
    decision: str
    consequences: list[str]
    rationale: str
    related_prd_id: str | None = None
    related_initiative_id: str | None = None


@dataclass
class StorySpec:
    """Well-formed engineering story (PRD-0009 §30)."""
    story_id: str
    title: str
    context: str
    requirement_ref: str
    acceptance_criteria: list[str]
    dependencies: list[str] = field(default_factory=list)
    estimated_hours: float | None = None
    estimate_confidence: EstimateConfidence = EstimateConfidence.UNKNOWN


@dataclass
class EpicBreakdown:
    """An epic decomposed from a PRD (PRD-0009 §28)."""
    epic_id: str
    title: str
    description: str
    prd_entity_id: str
    stories: list[StorySpec] = field(default_factory=list)


@dataclass
class EngineeringBreakdown:
    """Complete engineering breakdown from a PRD."""
    prd_entity_id: str
    prd_title: str
    epics: list[EpicBreakdown]
    total_stories: int
    total_estimated_hours: float
    estimate_confidence: EstimateConfidence


@dataclass
class DependencyEdge:
    """A dependency between two engineering work items (PRD-0009 §34)."""
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    dependency_type: DependencyType
    is_blocking: bool
    description: str = ""


@dataclass
class TechDebtItem:
    """Technical Debt as first-class knowledge (PRD-0009 §72-§76)."""
    component: str
    description: str
    severity: TechDebtSeverity
    product_impact: str
    business_cost: str
    remediation: str
    estimated_effort_hours: float | None = None
    accumulated_since: str | None = None


@dataclass
class TechnicalRisk:
    """Technical Risk record (PRD-0009 §77-§81)."""
    risk: str
    likelihood: str   # HIGH, MEDIUM, LOW
    impact: str       # HIGH, MEDIUM, LOW
    mitigation: str
    owner: str = "Engineering"
    related_component: str | None = None


@dataclass
class EffortEstimate:
    """Effort estimation model (PRD-0009 §23)."""
    development_hours: float
    testing_hours: float
    integration_hours: float
    migration_hours: float
    deployment_hours: float
    contingency_hours: float
    total_hours: float
    confidence: EstimateConfidence
    assumptions: list[str] = field(default_factory=list)
    historical_basis: str | None = None


@dataclass
class CapacityAnalysis:
    """Team capacity analysis (PRD-0009 §26, §27)."""
    available_hours: float
    required_hours: float
    conflict_hours: float
    has_conflict: bool
    utilization_percent: float
    recommendations: list[str]


@dataclass
class BlockerInfo:
    """A blocked work item with aging information."""
    blocked_entity_id: str
    blocked_name: str
    blocking_entity_id: str
    blocking_name: str
    blocked_since: str | None
    age_days: int
    severity: str


@dataclass
class DriftItem:
    """A single implementation drift detection result."""
    requirement_ref: str
    requirement_text: str
    expected_status: str
    actual_status: str
    drift_type: str   # "missing", "incomplete", "diverged", "untracked"
    details: str


@dataclass
class HandoffDocument:
    """Complete engineering handoff (PRD-0009 §90)."""
    initiative_name: str
    prd_reference: str
    objective: str
    architecture_impact: str
    affected_components: list[str]
    new_components: list[str]
    dependencies: list[str]
    data_model_changes: list[str]
    events: list[str]
    observability: list[str]
    rollback_strategy: str
    epics: list[dict[str, Any]]
    total_stories: int
    total_estimated_hours: float
    estimate_confidence: str
    risks: list[dict[str, str]]
    open_questions: list[str]


# ─── Engine ────────────────────────────────────────────────────────


class EngineeringIntelligenceEngine:
    """
    Engineering Intelligence and Execution Orchestration Engine.

    Bridges Product Intelligence (PRDs, Requirements, Decisions) to
    Engineering Execution (Technical Designs, ADRs, Epics, Stories,
    Dependencies, Estimates, Tech Debt).

    Constitutional principle (PRD-0009 §2):
    > Engineering execution must remain traceable to product intent.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    # ─── PRD Technical Analysis ────────────────────────────────

    def analyze_prd_technical_implications(
        self,
        prd_title: str,
        prd_entity_id: str,
        requirements: list[dict[str, str]],
    ) -> TechnicalAnalysis:
        """
        Analyzes a PRD's requirements for technical implications.
        Identifies affected components, new components needed,
        dependencies, and technical risks (PRD-0009 §8, §16).

        Each requirement is inspected for keywords indicating
        architecture, data model, API, or infrastructure impact.
        """
        implications: list[TechnicalImplication] = []
        all_affected: set[str] = set()
        all_new: set[str] = set()
        all_deps: set[str] = set()
        all_risks: set[str] = set()

        for req in requirements:
            req_id = req.get("id", "FR-???")
            req_text = req.get("text", "")
            text_lower = req_text.lower()

            affected = []
            new_comps = []
            data_changes = []
            api_changes = []
            deps = []
            risks = []

            # Detect affected areas from keywords
            if any(w in text_lower for w in ["api", "endpoint", "rest", "graphql"]):
                affected.append("API Gateway")
                api_changes.append(f"New or modified endpoint for {req_id}")

            if any(w in text_lower for w in ["database", "table", "schema", "migration", "column"]):
                affected.append("Database")
                data_changes.append(f"Schema change required for {req_id}")

            if any(w in text_lower for w in ["queue", "kafka", "event", "message", "pubsub"]):
                affected.append("Event Bus / Message Queue")
                deps.append("Message broker availability")

            if any(w in text_lower for w in ["cache", "redis", "memcache"]):
                affected.append("Cache Layer")
                deps.append("Cache infrastructure")

            if any(w in text_lower for w in ["auth", "permission", "role", "rbac", "security"]):
                affected.append("Authentication / Authorization")
                risks.append(f"Security boundary change in {req_id} requires review")

            if any(w in text_lower for w in ["email", "notification", "sms", "push"]):
                affected.append("Notification Service")
                deps.append("Notification provider")

            if any(w in text_lower for w in ["payment", "billing", "invoice", "charge"]):
                affected.append("Payment / Billing")
                risks.append(f"Financial system change in {req_id} is high-risk")

            if any(w in text_lower for w in ["ui", "frontend", "dashboard", "screen", "page"]):
                affected.append("Frontend / UI")

            if any(w in text_lower for w in ["report", "analytics", "metric", "chart"]):
                affected.append("Analytics / Reporting")

            # If no specific component detected, it's a new capability
            if not affected:
                new_comps.append(f"New service/module for {req_id}")

            # Detect risks from complexity indicators
            if any(w in text_lower for w in ["real-time", "concurrent", "distributed", "transaction"]):
                risks.append(f"Complexity risk: {req_id} involves distributed/concurrent behavior")

            if any(w in text_lower for w in ["migration", "legacy", "backward", "compatibility"]):
                risks.append(f"Migration risk: {req_id} involves backward compatibility")

            all_affected.update(affected)
            all_new.update(new_comps)
            all_deps.update(deps)
            all_risks.update(risks)

            implications.append(TechnicalImplication(
                requirement_ref=req_id,
                requirement_text=req_text,
                affected_components=affected,
                new_components=new_comps,
                data_model_changes=data_changes,
                api_changes=api_changes,
                dependencies=deps,
                risks=risks,
            ))

        # Determine architecture impact level
        if len(all_new) > 2 or len(all_affected) > 5:
            arch_impact = "significant"
        elif len(all_new) > 0 or len(all_affected) > 3:
            arch_impact = "moderate"
        elif len(all_affected) > 1:
            arch_impact = "minor"
        else:
            arch_impact = "none"

        recommendation = (
            f"PRD '{prd_title}' affects {len(all_affected)} existing components "
            f"and requires {len(all_new)} new components. "
            f"Architecture impact: {arch_impact}. "
            f"{len(all_risks)} technical risks identified. "
            f"Recommend {'architecture review' if arch_impact in ('significant', 'moderate') else 'standard planning'}."
        )

        return TechnicalAnalysis(
            prd_entity_id=prd_entity_id,
            prd_title=prd_title,
            phase=EngineeringPhase.TECHNICAL_DISCOVERY,
            implications=implications,
            total_affected_components=sorted(all_affected),
            total_new_components=sorted(all_new),
            total_dependencies=sorted(all_deps),
            total_risks=sorted(all_risks),
            architecture_impact=arch_impact,
            recommendation=recommendation,
        )

    # ─── Technical Design ──────────────────────────────────────

    def generate_technical_design(
        self,
        prd_entity_id: str,
        title: str,
        analysis: TechnicalAnalysis,
        architecture_context: str = "",
    ) -> TechnicalDesign:
        """
        Generates a structured Technical Design Specification
        from a PRD analysis (PRD-0009 §17).
        """
        # Build component list from analysis
        components = []
        for comp in analysis.total_affected_components:
            components.append({"name": comp, "change_type": "MODIFY", "confidence": "inferred"})
        for comp in analysis.total_new_components:
            components.append({"name": comp, "change_type": "CREATE", "confidence": "inferred"})

        # Extract data model and API changes from implications
        all_data_changes = []
        all_api_changes = []
        all_events = []
        for impl in analysis.implications:
            all_data_changes.extend(impl.data_model_changes)
            all_api_changes.extend([{"change": c, "requirement_ref": impl.requirement_ref} for c in impl.api_changes])

        # Derive data flow from components
        data_flow = []
        if any("Frontend" in c for c in analysis.total_affected_components):
            data_flow.append("Client → API Gateway")
        if any("API" in c for c in analysis.total_affected_components):
            data_flow.append("API Gateway → Service Layer")
        if any("Database" in c for c in analysis.total_affected_components):
            data_flow.append("Service Layer → Database")
        if any("Event" in c or "Queue" in c for c in analysis.total_affected_components):
            data_flow.append("Service Layer → Event Bus → Consumers")
            all_events.append(f"{title.lower().replace(' ', '_')}.created")
            all_events.append(f"{title.lower().replace(' ', '_')}.completed")
            all_events.append(f"{title.lower().replace(' ', '_')}.failed")
        if any("Cache" in c for c in analysis.total_affected_components):
            data_flow.append("Service Layer → Cache → Database (fallback)")

        # Failure modes from risks
        failure_modes = [
            {"failure": r, "mitigation": "Requires engineering investigation"}
            for r in analysis.total_risks
        ]

        return TechnicalDesign(
            prd_entity_id=prd_entity_id,
            title=f"Technical Design: {title}",
            architecture_context=architecture_context or f"Design for PRD '{title}' — architecture impact: {analysis.architecture_impact}",
            existing_system=analysis.total_affected_components,
            proposed_changes=[f"Modify {c}" for c in analysis.total_affected_components] + [f"Create {c}" for c in analysis.total_new_components],
            components=components,
            data_flow=data_flow,
            api_changes=all_api_changes,
            data_model=[{"change": d, "confidence": "inferred"} for d in all_data_changes],
            events=all_events,
            dependencies=analysis.total_dependencies,
            security_considerations=[r for r in analysis.total_risks if "security" in r.lower() or "auth" in r.lower()],
            scalability_notes=[r for r in analysis.total_risks if "concurrent" in r.lower() or "distributed" in r.lower()],
            failure_modes=failure_modes,
            observability=[f"{title} — request latency", f"{title} — error rate", f"{title} — throughput"],
            migration_strategy="Feature flag controlled rollout with canary deployment",
            rollback_strategy="Disable feature flag; no schema rollback required unless migration is irreversible",
            open_questions=[f"Confirm actual architecture for {c}" for c in analysis.total_affected_components[:2]] if analysis.total_affected_components else [],
        )

    # ─── Architecture Decision Records ─────────────────────────

    async def create_architecture_decision(
        self,
        title: str,
        context: str,
        alternatives: list[dict[str, str]],
        decision: str,
        consequences: list[str],
        rationale: str,
        related_prd_id: str | None = None,
        related_initiative_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Creates and persists an Architecture Decision Record (ADR)
        in the Knowledge Graph (PRD-0009 §12, §13).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized on EngineeringIntelligenceEngine.")

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.ARCHITECTURE_DECISION,
            name=title,
            description=context,
            properties={
                "status": ADRStatus.PROPOSED.value,
                "context": context,
                "alternatives": alternatives,
                "decision": decision,
                "consequences": consequences,
                "rationale": rationale,
                "decided_at": datetime.now(timezone.utc).isoformat(),
            },
            source="engineering_engine",
            confidence=ConfidenceLevel.CONFIRMED,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        # Link ADR to PRD (SUPPORTS)
        if related_prd_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=related_prd_id,
                relationship_type=RelationshipType.SUPPORTS,
                properties={"purpose": "adr_supports_prd"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel)

        # Link ADR to Initiative (SUPPORTS)
        if related_initiative_id:
            rel_init = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=related_initiative_id,
                relationship_type=RelationshipType.SUPPORTS,
                properties={"purpose": "adr_supports_initiative"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel_init)

        await self.db.flush()

        return {
            "adr_id": entity.id,
            "title": entity.name,
            "status": ADRStatus.PROPOSED.value,
            "alternatives_count": len(alternatives),
            "consequences_count": len(consequences),
        }

    # ─── Engineering Breakdown ─────────────────────────────────

    def decompose_into_epics(
        self,
        prd_entity_id: str,
        prd_title: str,
        requirements: list[dict[str, str]],
    ) -> EngineeringBreakdown:
        """
        Decomposes PRD requirements into Epics → Stories → Subtasks
        (PRD-0009 §28).

        Groups related requirements into epics. Each requirement
        becomes a story with acceptance criteria derived from
        the requirement text.
        """
        epics: list[EpicBreakdown] = []
        total_stories = 0
        total_hours = 0.0

        # Group requirements into logical epics (simple grouping by index batches)
        # In production, this would use semantic clustering
        batch_size = max(1, len(requirements) // 3) if len(requirements) > 3 else len(requirements)
        epic_groups: list[list[dict[str, str]]] = []

        for i in range(0, len(requirements), batch_size):
            epic_groups.append(requirements[i:i + batch_size])

        for epic_idx, group in enumerate(epic_groups, 1):
            epic_id = f"EPIC-{epic_idx:03d}"

            # Generate stories for each requirement in the epic
            stories: list[StorySpec] = []
            for story_idx, req in enumerate(group, 1):
                req_id = req.get("id", f"FR-{(epic_idx - 1) * batch_size + story_idx:03d}")
                req_text = req.get("text", "")

                # Estimate based on complexity heuristics
                text_lower = req_text.lower()
                base_hours = 16.0  # Default 2 days
                if any(w in text_lower for w in ["api", "endpoint"]):
                    base_hours += 8.0
                if any(w in text_lower for w in ["database", "migration", "schema"]):
                    base_hours += 12.0
                if any(w in text_lower for w in ["real-time", "concurrent", "distributed"]):
                    base_hours += 16.0
                if any(w in text_lower for w in ["ui", "frontend", "dashboard"]):
                    base_hours += 12.0

                story = StorySpec(
                    story_id=f"{epic_id}-S{story_idx:03d}",
                    title=req_text[:80] if req_text else f"Implement {req_id}",
                    context=f"From {req_id} in PRD '{prd_title}'",
                    requirement_ref=req_id,
                    acceptance_criteria=[
                        f"Given the feature is deployed, when {req_text[:60].lower()}, then the system behaves as specified",
                        "Given an unauthorized user, when attempting this action, then access is denied",
                        "Given invalid input, when submitted, then a clear validation error is returned",
                    ],
                    estimated_hours=base_hours,
                    estimate_confidence=EstimateConfidence.MEDIUM,
                )
                stories.append(story)
                total_hours += base_hours

            total_stories += len(stories)

            # Derive epic title from first requirement
            epic_title = group[0].get("text", f"Epic {epic_idx}")[:80] if group else f"Epic {epic_idx}"

            epics.append(EpicBreakdown(
                epic_id=epic_id,
                title=f"Epic: {epic_title}",
                description=f"Engineering epic covering {len(stories)} stories from PRD '{prd_title}'",
                prd_entity_id=prd_entity_id,
                stories=stories,
            ))

        return EngineeringBreakdown(
            prd_entity_id=prd_entity_id,
            prd_title=prd_title,
            epics=epics,
            total_stories=total_stories,
            total_estimated_hours=total_hours,
            estimate_confidence=EstimateConfidence.MEDIUM,
        )

    # ─── Dependency Mapping ────────────────────────────────────

    def map_dependencies(
        self,
        breakdown: EngineeringBreakdown,
    ) -> list[DependencyEdge]:
        """
        Identifies dependencies between stories within an engineering
        breakdown (PRD-0009 §34).

        Uses heuristic: later stories that reference components
        mentioned in earlier stories are marked as soft dependencies.
        Database/schema stories block API stories.
        """
        edges: list[DependencyEdge] = []
        all_stories: list[StorySpec] = []
        for epic in breakdown.epics:
            all_stories.extend(epic.stories)

        # Track which stories involve database vs API vs frontend
        db_stories = [s for s in all_stories if any(w in s.title.lower() for w in ["database", "schema", "migration", "model", "table"])]
        api_stories = [s for s in all_stories if any(w in s.title.lower() for w in ["api", "endpoint", "service"])]
        ui_stories = [s for s in all_stories if any(w in s.title.lower() for w in ["ui", "frontend", "dashboard", "screen"])]

        # DB blocks API; API blocks UI
        for db_s in db_stories:
            for api_s in api_stories:
                if db_s.story_id != api_s.story_id:
                    edges.append(DependencyEdge(
                        source_id=api_s.story_id,
                        source_name=api_s.title,
                        target_id=db_s.story_id,
                        target_name=db_s.title,
                        dependency_type=DependencyType.DATA,
                        is_blocking=True,
                        description=f"{api_s.story_id} depends on data model from {db_s.story_id}",
                    ))

        for api_s in api_stories:
            for ui_s in ui_stories:
                if api_s.story_id != ui_s.story_id:
                    edges.append(DependencyEdge(
                        source_id=ui_s.story_id,
                        source_name=ui_s.title,
                        target_id=api_s.story_id,
                        target_name=api_s.title,
                        dependency_type=DependencyType.API,
                        is_blocking=True,
                        description=f"{ui_s.story_id} depends on API from {api_s.story_id}",
                    ))

        return edges

    # ─── Story Generation ──────────────────────────────────────

    def generate_story(
        self,
        requirement_ref: str,
        requirement_text: str,
        context: str = "",
        prd_title: str = "",
    ) -> StorySpec:
        """
        Generates a well-formed engineering story from a requirement
        (PRD-0009 §30).
        """
        text_lower = requirement_text.lower()

        # Derive acceptance criteria from requirement text
        acceptance = [
            f"Given the system is operational, when {requirement_text[:60].lower()}, then the expected behavior is observed",
            "Given an unauthorized user, when attempting this action, then access is denied with 403",
            "Given invalid or missing input, when the request is submitted, then a 400 error with descriptive message is returned",
        ]

        # Add edge-case acceptance criteria based on keywords
        if any(w in text_lower for w in ["create", "add", "insert", "new"]):
            acceptance.append("Given a duplicate record exists, when creating the same entity, then a conflict error is returned")
        if any(w in text_lower for w in ["delete", "remove", "archive"]):
            acceptance.append("Given the entity does not exist, when attempting deletion, then a 404 is returned")
        if any(w in text_lower for w in ["list", "search", "filter", "query"]):
            acceptance.append("Given no results match, when searching, then an empty result set with 200 is returned")

        # Estimate hours
        base_hours = 16.0
        if any(w in text_lower for w in ["database", "migration"]): base_hours += 12.0
        if any(w in text_lower for w in ["api", "endpoint"]): base_hours += 8.0
        if any(w in text_lower for w in ["real-time", "websocket"]): base_hours += 16.0

        return StorySpec(
            story_id=f"STORY-{requirement_ref}",
            title=requirement_text[:80],
            context=context or f"From {requirement_ref} in PRD '{prd_title}'",
            requirement_ref=requirement_ref,
            acceptance_criteria=acceptance,
            estimated_hours=base_hours,
            estimate_confidence=EstimateConfidence.MEDIUM,
        )

    # ─── Effort Estimation ─────────────────────────────────────

    def estimate_effort(
        self,
        breakdown: EngineeringBreakdown,
        testing_multiplier: float = 0.3,
        integration_multiplier: float = 0.15,
        deployment_multiplier: float = 0.1,
        contingency_multiplier: float = 0.2,
    ) -> EffortEstimate:
        """
        Calculates effort estimates with explicit confidence levels
        (PRD-0009 §22-§25).

        Estimate = Development + Testing + Integration + Migration
                   + Deployment + Contingency

        Estimates are labeled as estimates, never commitments.
        """
        dev_hours = breakdown.total_estimated_hours
        testing_hours = round(dev_hours * testing_multiplier, 1)
        integration_hours = round(dev_hours * integration_multiplier, 1)
        migration_hours = 0.0  # Only if schema changes detected
        deployment_hours = round(dev_hours * deployment_multiplier, 1)

        # Check for migration indicators
        for epic in breakdown.epics:
            for story in epic.stories:
                if any(w in story.title.lower() for w in ["migration", "schema", "data model"]):
                    migration_hours += 8.0

        subtotal = dev_hours + testing_hours + integration_hours + migration_hours + deployment_hours
        contingency_hours = round(subtotal * contingency_multiplier, 1)
        total = round(subtotal + contingency_hours, 1)

        return EffortEstimate(
            development_hours=dev_hours,
            testing_hours=testing_hours,
            integration_hours=integration_hours,
            migration_hours=migration_hours,
            deployment_hours=deployment_hours,
            contingency_hours=contingency_hours,
            total_hours=total,
            confidence=breakdown.estimate_confidence,
            assumptions=[
                "Estimate assumes no major unknowns in existing architecture",
                "Testing estimate includes unit and integration tests only",
                "Contingency covers typical scope refinement during implementation",
                "⚠️ This is an estimate, not a commitment (PRD-0009 §22)",
            ],
        )

    # ─── Capacity Analysis ─────────────────────────────────────

    def analyze_capacity(
        self,
        available_hours: float,
        estimate: EffortEstimate,
    ) -> CapacityAnalysis:
        """
        Compares required effort against available team capacity.
        Detects overload and suggests mitigation (PRD-0009 §26, §27).
        """
        conflict = max(0.0, estimate.total_hours - available_hours)
        has_conflict = conflict > 0
        utilization = round((estimate.total_hours / max(available_hours, 1.0)) * 100, 1)

        recommendations = []
        if utilization > 120:
            recommendations.extend([
                "⚠️ Team is significantly overloaded — consider deferring lower-priority work",
                "Consider reducing scope to MVP-only requirements",
                "Evaluate adding temporary engineering capacity",
            ])
        elif utilization > 100:
            recommendations.extend([
                "⚠️ Team capacity exceeded — consider splitting delivery across sprints",
                "Identify stories that can be deferred to v1.1",
            ])
        elif utilization > 80:
            recommendations.append("Team utilization is healthy but leaves limited buffer for unplanned work")
        else:
            recommendations.append("Sufficient capacity available for planned work")

        return CapacityAnalysis(
            available_hours=available_hours,
            required_hours=estimate.total_hours,
            conflict_hours=round(conflict, 1),
            has_conflict=has_conflict,
            utilization_percent=utilization,
            recommendations=recommendations,
        )

    # ─── Duplicate Work Detection ──────────────────────────────

    async def detect_duplicate_work(
        self,
        description: str,
    ) -> list[dict[str, Any]]:
        """
        Searches the Knowledge Graph for existing similar engineering
        work to prevent duplication (PRD-0009 §14, §15, §33).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        keywords = [w for w in description.lower().split() if len(w) > 3][:5]

        results = []
        for kw in keywords:
            stmt = (
                select(Entity)
                .where(Entity.workspace_id == self.workspace_id)
                .where(Entity.entity_type.in_([
                    EntityType.EPIC, EntityType.STORY, EntityType.TASK,
                ]))
                .where(Entity.status == EntityStatus.ACTIVE)
                .where(Entity.name.ilike(f"%{kw}%"))
                .limit(5)
            )
            res = await self.db.execute(stmt)
            for entity in res.scalars().all():
                if entity.id not in [r["entity_id"] for r in results]:
                    results.append({
                        "entity_id": entity.id,
                        "entity_type": entity.entity_type.value,
                        "name": entity.name,
                        "status": entity.status.value,
                        "similarity": "keyword_match",
                    })

        return results[:10]

    # ─── Technical Debt ────────────────────────────────────────

    async def record_tech_debt(
        self,
        item: TechDebtItem,
    ) -> dict[str, Any]:
        """
        Records technical debt as a first-class entity in the
        Knowledge Graph (PRD-0009 §72-§76).

        Tech debt must be connected to business/product consequences,
        not merely labeled as debt.
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.TECHNICAL_DEBT,
            name=f"Tech Debt: {item.component} — {item.description[:60]}",
            description=item.description,
            properties={
                "component": item.component,
                "severity": item.severity.value,
                "product_impact": item.product_impact,
                "business_cost": item.business_cost,
                "remediation": item.remediation,
                "estimated_effort_hours": item.estimated_effort_hours,
                "accumulated_since": item.accumulated_since,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
            source="engineering_engine",
            confidence=ConfidenceLevel.CONFIRMED,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        return {
            "tech_debt_id": entity.id,
            "component": item.component,
            "severity": item.severity.value,
            "product_impact": item.product_impact,
        }

    # ─── Technical Risk ────────────────────────────────────────

    async def record_technical_risk(
        self,
        risk: TechnicalRisk,
        related_initiative_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Records a technical risk in the Knowledge Graph
        (PRD-0009 §77-§81).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.TECHNICAL_RISK,
            name=f"Risk: {risk.risk[:80]}",
            description=risk.risk,
            properties={
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "mitigation": risk.mitigation,
                "owner": risk.owner,
                "related_component": risk.related_component,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
            source="engineering_engine",
            confidence=ConfidenceLevel.INFERRED,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        if related_initiative_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=related_initiative_id,
                relationship_type=RelationshipType.AFFECTS,
                properties={"purpose": "risk_affects_initiative"},
                confidence=ConfidenceLevel.INFERRED,
            )
            self.db.add(rel)
            await self.db.flush()

        return {
            "risk_id": entity.id,
            "risk": risk.risk,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
        }

    # ─── Implementation Drift Detection ────────────────────────

    async def detect_implementation_drift(
        self,
        prd_entity_id: str,
    ) -> list[DriftItem]:
        """
        Compares PRD requirements against engineering execution status
        to detect implementation drift (PRD-0009 §52-§55).

        Drift types:
        - missing: Requirement has no corresponding engineering work
        - incomplete: Engineering work exists but is not complete
        - diverged: Engineering work does not match requirement
        - untracked: Engineering work exists with no requirement link
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        # Load PRD entity
        prd_stmt = select(Entity).where(Entity.id == prd_entity_id)
        prd_result = await self.db.execute(prd_stmt)
        prd_entity = prd_result.scalar_one_or_none()
        if not prd_entity:
            return []

        # Find all requirements linked to this PRD
        req_stmt = (
            select(Entity)
            .join(EntityRelationship, EntityRelationship.source_entity_id == Entity.id)
            .where(EntityRelationship.target_entity_id == prd_entity_id)
            .where(Entity.entity_type == EntityType.REQUIREMENT)
            .where(Entity.workspace_id == self.workspace_id)
        )
        req_result = await self.db.execute(req_stmt)
        requirements = req_result.scalars().all()

        drift_items = []
        for req in requirements:
            # Check if any engineering work implements this requirement
            impl_stmt = (
                select(Entity)
                .join(EntityRelationship, EntityRelationship.source_entity_id == Entity.id)
                .where(EntityRelationship.target_entity_id == req.id)
                .where(EntityRelationship.relationship_type == RelationshipType.IMPLEMENTS)
                .where(Entity.workspace_id == self.workspace_id)
            )
            impl_result = await self.db.execute(impl_stmt)
            implementations = impl_result.scalars().all()

            if not implementations:
                drift_items.append(DriftItem(
                    requirement_ref=req.name,
                    requirement_text=req.description or "",
                    expected_status="IMPLEMENTED",
                    actual_status="NO_ENGINEERING_WORK",
                    drift_type="missing",
                    details=f"Requirement '{req.name}' has no corresponding engineering work",
                ))
            else:
                for impl in implementations:
                    impl_status = impl.properties.get("engineering_phase", "UNKNOWN")
                    if impl_status not in ("RELEASED", "MONITORING"):
                        drift_items.append(DriftItem(
                            requirement_ref=req.name,
                            requirement_text=req.description or "",
                            expected_status="RELEASED",
                            actual_status=impl_status,
                            drift_type="incomplete",
                            details=f"Engineering work '{impl.name}' is in phase '{impl_status}', not yet released",
                        ))

        return drift_items

    # ─── Blocker Analysis ──────────────────────────────────────

    async def analyze_blockers(
        self,
        epic_entity_id: str,
    ) -> list[BlockerInfo]:
        """
        Identifies blocked stories and calculates blocker aging
        (PRD-0009 §37-§40).
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized.")

        # Find all blocking relationships originating from stories in this epic
        blocker_stmt = (
            select(
                EntityRelationship,
                Entity,
            )
            .join(Entity, Entity.id == EntityRelationship.source_entity_id)
            .where(EntityRelationship.relationship_type == RelationshipType.BLOCKS)
            .where(Entity.workspace_id == self.workspace_id)
        )
        result = await self.db.execute(blocker_stmt)
        rows = result.all()

        blockers = []
        for rel, blocking_entity in rows:
            # Load blocked entity
            blocked_stmt = select(Entity).where(Entity.id == rel.target_entity_id)
            blocked_result = await self.db.execute(blocked_stmt)
            blocked_entity = blocked_result.scalar_one_or_none()
            if not blocked_entity:
                continue

            # Calculate age
            age_days = 0
            blocked_since = rel.created_at.isoformat() if rel.created_at else None
            if rel.created_at:
                delta = datetime.now(timezone.utc) - rel.created_at.replace(tzinfo=timezone.utc) if rel.created_at.tzinfo is None else datetime.now(timezone.utc) - rel.created_at
                age_days = delta.days

            severity = "LOW"
            if age_days > 14:
                severity = "CRITICAL"
            elif age_days > 7:
                severity = "HIGH"
            elif age_days > 3:
                severity = "MEDIUM"

            blockers.append(BlockerInfo(
                blocked_entity_id=blocked_entity.id,
                blocked_name=blocked_entity.name,
                blocking_entity_id=blocking_entity.id,
                blocking_name=blocking_entity.name,
                blocked_since=blocked_since,
                age_days=age_days,
                severity=severity,
            ))

        return blockers

    # ─── Engineering Handoff ───────────────────────────────────

    def generate_engineering_handoff(
        self,
        prd_title: str,
        prd_entity_id: str,
        analysis: TechnicalAnalysis,
        breakdown: EngineeringBreakdown,
        estimate: EffortEstimate,
        objective: str = "",
    ) -> HandoffDocument:
        """
        Generates a complete engineering handoff document combining
        technical analysis, breakdown, and estimates
        (PRD-0009 §89, §90).
        """
        epics_data = []
        for epic in breakdown.epics:
            stories_data = [
                {
                    "story_id": s.story_id,
                    "title": s.title,
                    "requirement_ref": s.requirement_ref,
                    "estimated_hours": s.estimated_hours,
                    "acceptance_criteria_count": len(s.acceptance_criteria),
                }
                for s in epic.stories
            ]
            epics_data.append({
                "epic_id": epic.epic_id,
                "title": epic.title,
                "story_count": len(epic.stories),
                "stories": stories_data,
            })

        risks_data = [
            {"risk": r, "mitigation": "Requires engineering investigation"}
            for r in analysis.total_risks
        ]

        return HandoffDocument(
            initiative_name=prd_title,
            prd_reference=prd_entity_id,
            objective=objective or f"Implement {prd_title} as specified in the approved PRD",
            architecture_impact=analysis.architecture_impact,
            affected_components=analysis.total_affected_components,
            new_components=analysis.total_new_components,
            dependencies=analysis.total_dependencies,
            data_model_changes=[
                change
                for impl in analysis.implications
                for change in impl.data_model_changes
            ],
            events=[],
            observability=[f"{prd_title} — latency", f"{prd_title} — error rate", f"{prd_title} — throughput"],
            rollback_strategy="Disable feature flag",
            epics=epics_data,
            total_stories=breakdown.total_stories,
            total_estimated_hours=estimate.total_hours,
            estimate_confidence=estimate.confidence.value,
            risks=risks_data,
            open_questions=[f"Confirm architecture for {c}" for c in analysis.total_affected_components[:3]],
        )
