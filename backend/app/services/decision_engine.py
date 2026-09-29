"""
Product Decision Engine (PDE) — PRD-0006

Implements:
1. Structured Decision Lifecycle (Context -> Options -> Trade-offs -> Decision -> Measurement)
2. Quantitative Trade-off Matrix & Opportunity Cost Scoring
3. Decision Record / ADR Synthesis (PRD-0006 §5)
4. Permanent Knowledge Graph Archival & Auditability (PRD-0001 P3/P4)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import (
    Entity,
    EntityRelationship,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
    RelationshipType,
)


class DecisionType(str, Enum):
    PRODUCT_INVESTMENT = "PRODUCT_INVESTMENT"
    FEATURE = "FEATURE"
    PRIORITIZATION = "PRIORITIZATION"
    MVP_SCOPE = "MVP_SCOPE"
    ARCHITECTURE = "ARCHITECTURE"
    BUILD_VS_BUY = "BUILD_VS_BUY"
    DEPRECATION = "DEPRECATION"
    EXPERIMENT = "EXPERIMENT"
    STRATEGY = "STRATEGY"
    RESOURCE = "RESOURCE"
    COMPLIANCE = "COMPLIANCE"


class DecisionOutcome(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"


@dataclass
class SolutionOption:
    name: str
    description: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    effort: float = 3.0       # 1.0 (trivial) to 5.0 (huge)
    impact: float = 3.0       # 1.0 (marginal) to 5.0 (transformative)
    risk: float = 2.0         # 1.0 (negligible) to 5.0 (severe)
    confidence: float = 0.8   # 0.0 to 1.0

    @property
    def score(self) -> float:
        """
        Constitutional scoring algorithm: (Impact * Confidence) / (Effort * Risk)
        Rewards high-confidence, high-impact moves while penalizing excessive effort and risk.
        """
        denominator = max(self.effort * self.risk, 0.5)
        return round((self.impact * self.confidence) / denominator, 3)


@dataclass
class DecisionRecord:
    title: str
    decision_type: DecisionType
    outcome: DecisionOutcome
    decision_question: str
    context: str
    rationale: str
    options: list[SolutionOption]
    tradeoffs: list[str]
    evidence_citations: list[str]
    risks: list[dict[str, str]]
    expected_outcomes: list[str]
    confidence: float
    decision_owner: str = "Product Leadership"


class ProductDecisionEngine:
    """
    Strategic Reasoning and Product Decision Engine.
    Converts dilemmas and competing priorities into immutable, evidence-backed
    organizational decisions.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    def evaluate_tradeoffs(self, options: list[SolutionOption]) -> list[tuple[SolutionOption, float, str]]:
        """
        Compares options and ranks them according to strategic efficiency score.
        Returns ranked list of (option, score, analysis).
        """
        ranked = sorted(options, key=lambda opt: opt.score, reverse=True)
        results = []
        for opt in ranked:
            analysis = (
                f"Impact: {opt.impact}/5, Effort: {opt.effort}/5, Risk: {opt.risk}/5, "
                f"Confidence: {int(opt.confidence * 100)}% -> Net Efficiency Score: {opt.score}"
            )
            results.append((opt, opt.score, analysis))
        return results

    def formulate_decision(
        self,
        title: str,
        decision_type: DecisionType,
        outcome: DecisionOutcome,
        decision_question: str,
        context: str,
        rationale: str,
        options: list[SolutionOption],
        evidence_citations: list[str],
        risks: list[dict[str, str]],
        expected_outcomes: list[str],
        decision_owner: str = "Product Leadership",
    ) -> DecisionRecord:
        """
        Constructs a structured, explainable decision record conforming to PRD-0006.
        """
        ranked_options = self.evaluate_tradeoffs(options)
        tradeoffs = [
            f"Chosen option scored {ranked_options[0][1]} vs alternate '{opt.name}' ({opt.score})"
            for opt, score, _ in ranked_options[1:]
        ]

        # Calculate blended decision confidence
        confidence = ranked_options[0][0].confidence if ranked_options else 0.75

        return DecisionRecord(
            title=title,
            decision_type=decision_type,
            outcome=outcome,
            decision_question=decision_question,
            context=context,
            rationale=rationale,
            options=options,
            tradeoffs=tradeoffs,
            evidence_citations=evidence_citations,
            risks=risks,
            expected_outcomes=expected_outcomes,
            confidence=confidence,
            decision_owner=decision_owner,
        )

    async def record_decision(
        self,
        record: DecisionRecord,
        initiative_id: str | None = None,
        problem_id: str | None = None,
        requirement_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Persists decision into the Knowledge Graph and links it to its
        governed initiative, problem, or requirement.
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized on ProductDecisionEngine.")

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=EntityType.DECISION,
            name=record.title,
            description=record.rationale,
            properties={
                "decision_type": record.decision_type.value,
                "outcome": record.outcome.value,
                "decision_question": record.decision_question,
                "context": record.context,
                "options": [
                    {
                        "name": o.name,
                        "description": o.description,
                        "effort": o.effort,
                        "impact": o.impact,
                        "risk": o.risk,
                        "confidence": o.confidence,
                        "score": o.score,
                    }
                    for o in record.options
                ],
                "tradeoffs": record.tradeoffs,
                "evidence_citations": record.evidence_citations,
                "risks": record.risks,
                "expected_outcomes": record.expected_outcomes,
                "decision_owner": record.decision_owner,
                "decided_at": datetime.now(timezone.utc).isoformat(),
            },
            source="decision_engine",
            confidence=ConfidenceLevel.CONFIRMED,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        # Link to Initiative (GOVERNS)
        if initiative_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=initiative_id,
                relationship_type=RelationshipType.BELONGS_TO,
                properties={"relationship_purpose": "decision_governs_initiative"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel)

        # Link to Problem (RESOLVES)
        if problem_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=problem_id,
                relationship_type=RelationshipType.RESOLVES,
                properties={"relationship_purpose": "decision_resolves_problem"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel)

        # Link to Requirement (SUPPORTS)
        if requirement_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=requirement_id,
                relationship_type=RelationshipType.SUPPORTS,
                properties={"relationship_purpose": "decision_supports_requirement"},
                confidence=ConfidenceLevel.CONFIRMED,
            )
            self.db.add(rel)

        await self.db.flush()

        return {
            "decision_id": entity.id,
            "title": entity.name,
            "outcome": record.outcome.value,
            "confidence": record.confidence,
            "tradeoffs_count": len(record.tradeoffs),
        }
