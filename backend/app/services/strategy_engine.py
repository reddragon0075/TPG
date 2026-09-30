"""
Product Strategy & Roadmap Intelligence Engine (PSRIE) — PRD-0007

Implements:
1. Strategic Theme Management (PRD-0007 §5-§6)
2. Strategic Objective Tracking (PRD-0007 §7-§9)
3. Strategic Bet Formulation & Evaluation (PRD-0007 §13-§16)
4. Strategic Assumption Register (PRD-0007 §17)
5. Roadmap Horizon Generation (Now / Next / Later) (PRD-0007 §18-§22)
6. Strategic Alignment Scoring (PRD-0007 §23-§25)
7. Strategic Drift Detection (PRD-0007 §26-§28)
8. Portfolio Balance & Investment Allocation Analysis (PRD-0007 §29-§32)

Constitutional Principle:
- Strategy -> Outcomes -> Bets -> Roadmap (PRD-0007 §2)
- Never: Backlog -> Dates -> Roadmap -> Strategy
"""

import uuid
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
    EntityRelationship,
    RelationshipType,
)


# ─── Enums ─────────────────────────────────────────────────────────

class TimeHorizon(str, Enum):
    IMMEDIATE_0_3_MONTHS = "0_3_MONTHS"
    SHORT_3_6_MONTHS = "3_6_MONTHS"
    MEDIUM_6_12_MONTHS = "6_12_MONTHS"
    LONG_12_24_MONTHS = "12_24_MONTHS"
    VISIONARY_24_PLUS = "24_PLUS_MONTHS"


class ObjectiveType(str, Enum):
    REVENUE = "revenue"
    GROWTH = "growth"
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    ADOPTION = "adoption"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    CUSTOMER = "customer"
    MARKET = "market"
    STRATEGIC = "strategic"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"


class BetLifecycleStatus(str, Enum):
    IDEA = "IDEA"
    HYPOTHESIS = "HYPOTHESIS"
    EXPLORATION = "EXPLORATION"
    VALIDATION = "VALIDATION"
    INVESTMENT = "INVESTMENT"
    EXECUTION = "EXECUTION"
    MEASUREMENT = "MEASUREMENT"
    SCALED = "SCALED"
    STOPPED = "STOPPED"


class AssumptionStatus(str, Enum):
    UNVALIDATED = "UNVALIDATED"
    VALIDATED = "VALIDATED"
    INVALIDATED = "INVALIDATED"


class RoadmapHorizon(str, Enum):
    NOW = "NOW"
    NEXT = "NEXT"
    LATER = "LATER"


class PortfolioCategory(str, Enum):
    GROWTH = "growth"
    RETENTION = "retention"
    EFFICIENCY = "efficiency"
    TECH_DEBT = "tech_debt"
    COMPLIANCE = "compliance"


# ─── Dataclasses ───────────────────────────────────────────────────

@dataclass
class StrategicThemeData:
    name: str
    description: str
    priority: str = "HIGH"
    time_horizon: TimeHorizon = TimeHorizon.MEDIUM_6_12_MONTHS
    success_metrics: list[str] = field(default_factory=list)


@dataclass
class StrategicObjectiveData:
    name: str
    theme_id: str | None = None
    objective_type: ObjectiveType = ObjectiveType.GROWTH
    description: str = ""
    baseline: float = 0.0
    target: float = 0.0
    unit: str = "%"
    deadline: str | None = None
    owner: str = "Product Office"


@dataclass
class StrategicBetData:
    name: str
    hypothesis: str
    strategic_theme_id: str | None = None
    expected_outcomes: list[str] = field(default_factory=list)
    investment_size: str = "MEDIUM"  # SMALL, MEDIUM, LARGE
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    confidence: float = 0.70
    status: BetLifecycleStatus = BetLifecycleStatus.HYPOTHESIS


@dataclass
class StrategicAssumptionData:
    statement: str
    category: str = "MARKET"  # MARKET, TECHNICAL, BEHAVIORAL, FINANCIAL
    confidence: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    status: AssumptionStatus = AssumptionStatus.UNVALIDATED
    validation_criteria: str = ""


@dataclass
class RoadmapItem:
    initiative_id: str
    name: str
    horizon: RoadmapHorizon
    strategic_theme: str | None
    alignment_score: float
    dependencies: list[str] = field(default_factory=list)
    target_period: str = "Q1"


# ─── Strategy Engine Implementation ────────────────────────────────

class StrategyIntelligenceEngine:
    """
    Core engine managing company strategy, strategic bets, assumptions,
    roadmap horizon sequencing, and portfolio alignment (PRD-0007).
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    # ─── 1. Strategic Themes ───────────────────────────────────────

    async def create_theme(self, data: StrategicThemeData) -> dict[str, Any]:
        """Creates and records a strategic theme in the Knowledge Graph."""
        theme_id = str(uuid.uuid4())
        props = {
            "priority": data.priority,
            "time_horizon": data.time_horizon.value if isinstance(data.time_horizon, TimeHorizon) else data.time_horizon,
            "success_metrics": data.success_metrics,
        }

        if self.db and self.workspace_id:
            entity = Entity(
                id=theme_id,
                workspace_id=self.workspace_id,
                entity_type=EntityType.STRATEGIC_THEME,
                name=data.name,
                description=data.description,
                properties=props,
                confidence=ConfidenceLevel.CONFIRMED,
                status=EntityStatus.ACTIVE,
            )
            self.db.add(entity)
            await self.db.flush()

        return {
            "theme_id": theme_id,
            "name": data.name,
            "description": data.description,
            "priority": data.priority,
            "time_horizon": data.time_horizon.value if isinstance(data.time_horizon, TimeHorizon) else data.time_horizon,
            "success_metrics": data.success_metrics,
        }

    # ─── 2. Strategic Objectives ───────────────────────────────────

    async def create_objective(self, data: StrategicObjectiveData) -> dict[str, Any]:
        """Creates an objective tied to a strategic theme."""
        obj_id = str(uuid.uuid4())
        props = {
            "objective_type": data.objective_type.value if isinstance(data.objective_type, ObjectiveType) else data.objective_type,
            "theme_id": data.theme_id,
            "baseline": data.baseline,
            "target": data.target,
            "unit": data.unit,
            "deadline": data.deadline,
            "owner": data.owner,
        }

        if self.db and self.workspace_id:
            entity = Entity(
                id=obj_id,
                workspace_id=self.workspace_id,
                entity_type=EntityType.OBJECTIVE,
                name=data.name,
                description=data.description,
                properties=props,
                confidence=ConfidenceLevel.CONFIRMED,
                status=EntityStatus.ACTIVE,
            )
            self.db.add(entity)

            # Link to Theme if provided
            if data.theme_id:
                rel = EntityRelationship(
                    source_entity_id=obj_id,
                    target_entity_id=data.theme_id,
                    relationship_type=RelationshipType.SUPPORTS,
                    properties={"intent": "theme_support"},
                )
                self.db.add(rel)

            await self.db.flush()

        return {
            "objective_id": obj_id,
            "name": data.name,
            "theme_id": data.theme_id,
            "objective_type": data.objective_type.value if isinstance(data.objective_type, ObjectiveType) else data.objective_type,
            "baseline": data.baseline,
            "target": data.target,
            "unit": data.unit,
            "deadline": data.deadline,
            "owner": data.owner,
        }

    # ─── 3. Strategic Bets ─────────────────────────────────────────

    async def create_bet(self, data: StrategicBetData) -> dict[str, Any]:
        """Formulates and stores a strategic bet hypothesis."""
        bet_id = str(uuid.uuid4())
        props = {
            "hypothesis": data.hypothesis,
            "strategic_theme_id": data.strategic_theme_id,
            "expected_outcomes": data.expected_outcomes,
            "investment_size": data.investment_size,
            "assumptions": data.assumptions,
            "risks": data.risks,
            "confidence": data.confidence,
            "bet_status": data.status.value if isinstance(data.status, BetLifecycleStatus) else data.status,
        }

        if self.db and self.workspace_id:
            entity = Entity(
                id=bet_id,
                workspace_id=self.workspace_id,
                entity_type=EntityType.STRATEGIC_BET,
                name=data.name,
                description=data.hypothesis,
                properties=props,
                confidence=ConfidenceLevel.INFERRED if data.confidence < 0.8 else ConfidenceLevel.CONFIRMED,
                status=EntityStatus.ACTIVE,
            )
            self.db.add(entity)

            if data.strategic_theme_id:
                rel = EntityRelationship(
                    source_entity_id=bet_id,
                    target_entity_id=data.strategic_theme_id,
                    relationship_type=RelationshipType.SUPPORTS,
                    properties={"intent": "strategic_bet_alignment"},
                )
                self.db.add(rel)

            await self.db.flush()

        return {
            "bet_id": bet_id,
            "name": data.name,
            "hypothesis": data.hypothesis,
            "strategic_theme_id": data.strategic_theme_id,
            "investment_size": data.investment_size,
            "confidence": data.confidence,
            "status": data.status.value if isinstance(data.status, BetLifecycleStatus) else data.status,
            "expected_outcomes": data.expected_outcomes,
        }

    def evaluate_bet(
        self,
        name: str,
        hypothesis: str,
        evidence_strength: float,  # 0.0 to 1.0
        investment_size: str,       # SMALL, MEDIUM, LARGE
        market_uncertainty: float,  # 0.0 to 1.0
    ) -> dict[str, Any]:
        """
        Evaluates a strategic bet against evidence and uncertainty (PRD-0007 §16).
        """
        size_weights = {"SMALL": 1.0, "MEDIUM": 1.5, "LARGE": 2.5}
        cost_weight = size_weights.get(investment_size.upper(), 1.5)

        # Viability Score: higher evidence, lower uncertainty, normalized by investment
        viability = round(min(100.0, max(0.0, ((evidence_strength * 1.5) / (market_uncertainty * 0.8 + 0.2 * cost_weight)) * 50)), 1)

        recommendation = "EXPLORE"
        if viability >= 75.0:
            recommendation = "INVEST"
        elif viability < 40.0:
            recommendation = "DE-PRIORITIZE"

        validation_milestones = [
            f"Run customer discovery interviews to validate: '{hypothesis[:60]}...'",
            "Build low-cost prototype or concierge MVP to test demand",
            "Establish quantifiable leading indicator metric before full resource allocation",
        ]

        return {
            "bet_name": name,
            "viability_score": viability,
            "recommendation": recommendation,
            "evidence_strength": evidence_strength,
            "market_uncertainty": market_uncertainty,
            "validation_milestones": validation_milestones,
        }

    # ─── 4. Strategic Assumptions ──────────────────────────────────

    async def record_assumption(self, data: StrategicAssumptionData) -> dict[str, Any]:
        """Records an assumption in the Strategic Assumption Register."""
        assumption_id = str(uuid.uuid4())
        props = {
            "category": data.category,
            "confidence": data.confidence,
            "assumption_status": data.status.value if isinstance(data.status, AssumptionStatus) else data.status,
            "validation_criteria": data.validation_criteria,
        }

        if self.db and self.workspace_id:
            entity = Entity(
                id=assumption_id,
                workspace_id=self.workspace_id,
                entity_type=EntityType.ASSUMPTION,
                name=data.statement[:120],
                description=data.statement,
                properties=props,
                confidence=ConfidenceLevel.ASSUMED,
                status=EntityStatus.ACTIVE,
            )
            self.db.add(entity)
            await self.db.flush()

        return {
            "assumption_id": assumption_id,
            "statement": data.statement,
            "category": data.category,
            "confidence": data.confidence,
            "status": data.status.value if isinstance(data.status, AssumptionStatus) else data.status,
        }

    # ─── 5. Strategic Alignment Scoring ────────────────────────────

    def score_strategic_alignment(
        self,
        initiative_name: str,
        problem_statement: str,
        linked_theme: str | None = None,
        linked_objective: str | None = None,
        has_validated_evidence: bool = False,
    ) -> dict[str, Any]:
        """
        Calculates strategic alignment score (0-100) for an initiative (PRD-0007 §23-§25).
        Enforces: Every initiative must justify its place on the roadmap.
        """
        score = 0.0
        breakdown = {}

        # Theme linkage (+35)
        if linked_theme and linked_theme.strip():
            score += 35.0
            breakdown["theme_alignment"] = 35.0
        else:
            breakdown["theme_alignment"] = 0.0

        # Objective linkage (+30)
        if linked_objective and linked_objective.strip():
            score += 30.0
            breakdown["objective_alignment"] = 30.0
        else:
            breakdown["objective_alignment"] = 0.0

        # Problem statement rigor (+20)
        if problem_statement and len(problem_statement.strip()) > 30:
            score += 20.0
            breakdown["problem_definition"] = 20.0
        else:
            breakdown["problem_definition"] = 5.0
            score += 5.0

        # Validated customer evidence (+15)
        if has_validated_evidence:
            score += 15.0
            breakdown["evidence_backing"] = 15.0
        else:
            breakdown["evidence_backing"] = 0.0

        level = "STRONG" if score >= 75.0 else ("MODERATE" if score >= 50.0 else "WEAK")
        gap_notes = []
        if breakdown["theme_alignment"] == 0:
            gap_notes.append("No linked strategic theme identified.")
        if breakdown["objective_alignment"] == 0:
            gap_notes.append("No quantified strategic objective linked.")
        if breakdown["evidence_backing"] == 0:
            gap_notes.append("Lacks validated customer/market evidence.")

        return {
            "initiative_name": initiative_name,
            "alignment_score": score,
            "alignment_level": level,
            "dimension_scores": breakdown,
            "gap_analysis": gap_notes,
            "is_constitutionally_sound": score >= 50.0,
        }

    # ─── 6. Roadmap Generation (Now / Next / Later) ────────────────

    async def generate_roadmap(
        self,
        initiatives: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Sequences initiatives into living Now/Next/Later horizons based on
        validation state, dependencies, and alignment (PRD-0007 §18-§22).
        """
        items_to_process = []

        if initiatives:
            items_to_process = initiatives
        elif self.db and self.workspace_id:
            # Query initiatives from Knowledge Graph
            stmt = (
                select(Entity)
                .where(Entity.workspace_id == self.workspace_id)
                .where(Entity.entity_type == EntityType.INITIATIVE)
            )
            res = await self.db.execute(stmt)
            entities = res.scalars().all()
            for ent in entities:
                items_to_process.append({
                    "id": ent.id,
                    "name": ent.name,
                    "status": ent.status.value,
                    "theme": ent.properties.get("strategic_theme"),
                    "objective": ent.properties.get("objective"),
                    "confidence": ent.confidence.value,
                    "dependencies": ent.properties.get("dependencies", []),
                })

        now_list: list[dict[str, Any]] = []
        next_list: list[dict[str, Any]] = []
        later_list: list[dict[str, Any]] = []

        for item in items_to_process:
            name = item.get("name", "Untitled Initiative")
            conf = item.get("confidence", "confirmed")
            status = item.get("status", "active")
            theme = item.get("theme")
            objective = item.get("objective")
            deps = item.get("dependencies", [])

            align = self.score_strategic_alignment(
                initiative_name=name,
                problem_statement="Validated initiative in portfolio",
                linked_theme=theme,
                linked_objective=objective,
                has_validated_evidence=conf == "confirmed",
            )

            # Heuristic for horizon:
            # High alignment + confirmed + active -> NOW
            # Moderate alignment or inferred -> NEXT
            # Later or assumed or exploratory -> LATER
            if status in ("active", "ACTIVE") and conf in ("confirmed", "CONFIRMED") and align["alignment_score"] >= 65:
                horizon = RoadmapHorizon.NOW
                now_list.append({
                    "initiative_id": item.get("id", str(uuid.uuid4())),
                    "name": name,
                    "theme": theme,
                    "alignment_score": align["alignment_score"],
                    "dependencies": deps,
                    "horizon": horizon.value,
                })
            elif align["alignment_score"] >= 45:
                horizon = RoadmapHorizon.NEXT
                next_list.append({
                    "initiative_id": item.get("id", str(uuid.uuid4())),
                    "name": name,
                    "theme": theme,
                    "alignment_score": align["alignment_score"],
                    "dependencies": deps,
                    "horizon": horizon.value,
                })
            else:
                horizon = RoadmapHorizon.LATER
                later_list.append({
                    "initiative_id": item.get("id", str(uuid.uuid4())),
                    "name": name,
                    "theme": theme,
                    "alignment_score": align["alignment_score"],
                    "dependencies": deps,
                    "horizon": horizon.value,
                })

        return {
            "summary": f"Roadmap generated across {len(items_to_process)} initiatives",
            "horizons": {
                "NOW": now_list,
                "NEXT": next_list,
                "LATER": later_list,
            },
            "total_initiatives": len(items_to_process),
            "now_count": len(now_list),
            "next_count": len(next_list),
            "later_count": len(later_list),
        }

    # ─── 7. Strategic Drift Detection ──────────────────────────────

    def detect_strategic_drift(
        self,
        initiatives: list[dict[str, Any]],
        active_themes: list[str],
    ) -> dict[str, Any]:
        """
        Detects drift where ongoing execution diverges from declared strategy (PRD-0007 §26-§28).
        """
        if not initiatives:
            return {
                "drift_percentage": 0.0,
                "drift_level": "NONE",
                "aligned_initiatives": [],
                "unaligned_initiatives": [],
                "recommendation": "No initiatives to assess.",
            }

        aligned = []
        unaligned = []
        normalized_themes = [t.lower().strip() for t in active_themes]

        for init in initiatives:
            theme = init.get("theme", "")
            if theme and theme.lower().strip() in normalized_themes:
                aligned.append(init.get("name", "Unknown"))
            else:
                unaligned.append(init.get("name", "Unknown"))

        drift_pct = round((len(unaligned) / len(initiatives)) * 100.0, 1)
        level = "HIGH" if drift_pct >= 40.0 else ("MODERATE" if drift_pct >= 20.0 else "LOW")

        recommendations = []
        if drift_pct >= 20.0:
            recommendations.append(f"{len(unaligned)} initiatives do not align to any active strategic theme.")
            recommendations.append("Conduct portfolio pruning or re-evaluate strategic themes.")
        else:
            recommendations.append("Portfolio is well-anchored to active strategic themes.")

        return {
            "total_initiatives": len(initiatives),
            "aligned_count": len(aligned),
            "unaligned_count": len(unaligned),
            "drift_percentage": drift_pct,
            "drift_level": level,
            "aligned_initiatives": aligned,
            "unaligned_initiatives": unaligned,
            "recommendations": recommendations,
        }

    # ─── 8. Portfolio Balance Analysis ─────────────────────────────

    def analyze_portfolio_balance(
        self,
        allocations: dict[str, float],  # Category -> Percentage or Effort Points
    ) -> dict[str, Any]:
        """
        Evaluates portfolio investment across Growth, Retention, Efficiency,
        Tech Debt, and Compliance (PRD-0007 §29-§32).
        """
        total = sum(allocations.values())
        if total == 0:
            return {"error": "Total allocation must be greater than zero."}

        normalized = {k.lower(): round((v / total) * 100.0, 1) for k, v in allocations.items()}

        growth = normalized.get("growth", 0.0)
        retention = normalized.get("retention", 0.0)
        efficiency = normalized.get("efficiency", 0.0)
        tech_debt = normalized.get("tech_debt", 0.0)
        compliance = normalized.get("compliance", 0.0)

        warnings = []
        if growth > 65.0:
            warnings.append("Over-investment warning: Growth consumes >65% of capacity; retention and debt may suffer.")
        if retention < 10.0:
            warnings.append("Under-investment risk: Retention allocation is under 10%; high risk of customer churn.")
        if tech_debt < 10.0:
            warnings.append("Technical risk: Technical debt allocation is under 10%; engineering velocity may degrade.")

        status = "BALANCED" if len(warnings) == 0 else ("WARNING" if len(warnings) == 1 else "CRITICAL_IMBALANCE")

        return {
            "status": status,
            "distribution": normalized,
            "warnings": warnings,
            "is_sustainable": status != "CRITICAL_IMBALANCE",
        }
