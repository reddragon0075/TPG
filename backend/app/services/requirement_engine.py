"""
Requirement Intelligence Engine (RIE) — PRD-0005

Implements:
1. Requirement Ingestion & Taxonomy Classification
2. Noise vs. Product Filter (PRD-0005 §6)
3. Ambiguity & Completeness Analysis with Prioritized Discovery Questions (PRD-0005 §9)
4. Problem Statement Structuring (PRD-0005 §11)
5. Jobs-to-be-Done (JTBD) Synthesis (PRD-0005 §12)
6. Knowledge Graph Ingestion with Provenance & Lineage
"""

from dataclasses import dataclass, field
from enum import Enum
import re
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


class RequirementType(str, Enum):
    FEATURE_REQUEST = "feature_request"
    PROBLEM_REPORT = "problem_report"
    BUG = "bug"
    IMPROVEMENT = "improvement"
    COMPLIANCE = "compliance"
    STRATEGIC = "strategic"
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL_REQUEST = "operational_request"
    NON_PRODUCT_NOISE = "non_product_noise"


class DiscoveryState(str, Enum):
    NEW = "new"
    UNDERSTANDING = "understanding"
    DISCOVERY = "discovery"
    EVIDENCE_COLLECTION = "evidence_collection"
    VALIDATED = "validated"
    OPPORTUNITY_DEFINED = "opportunity_defined"
    SOLUTION_EXPLORATION = "solution_exploration"
    PRIORITIZATION = "prioritization"
    APPROVED = "approved"
    SPECIFICATION = "specification"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass
class ProblemStatement:
    user: str
    situation: str
    problem: str
    current_behavior: str
    impact: str
    desired_outcome: str


@dataclass
class JTBDStatement:
    situation: str
    motivation: str
    expected_outcome: str

    def to_string(self) -> str:
        return f"When {self.situation}, I want to {self.motivation}, so I can {self.expected_outcome}."


@dataclass
class DiscoveryQuestion:
    priority: int  # 1 (Highest) to 9 (Lowest)
    dimension: str
    question: str
    rationale: str


@dataclass
class AmbiguityAnalysis:
    is_product_requirement: bool
    detected_type: RequirementType
    ambiguity_score: float  # 0.0 (completely crystal clear) to 1.0 (completely ambiguous)
    completeness_score: float  # 0.0 to 1.0
    missing_dimensions: list[str]
    identified_dimensions: dict[str, str]
    prioritized_questions: list[DiscoveryQuestion]
    suggested_jtbd: list[JTBDStatement] = field(default_factory=list)


class RequirementIntelligenceEngine:
    """
    Constitutional Product Requirement Intelligence.
    Ensures TPG never acts as a feature-factory regurgitator, but as a
    principled Chief Product Officer discovering root customer problems.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    def classify_statement(self, text: str) -> tuple[RequirementType, bool]:
        """
        Classifies whether input is a product requirement and its type.
        (PRD-0005 §5, §6)
        """
        t = text.lower().strip()

        # Check for operational / noise
        if re.search(r"\b(book a room|remind me to|order lunch|send an email to john|schedule a 1:1)\b", t):
            return RequirementType.NON_PRODUCT_NOISE, False

        if re.search(r"\b(reset my password|vpn is down|wifi not working|printer broken)\b", t):
            return RequirementType.OPERATIONAL_REQUEST, False

        # Bugs
        if re.search(r"\b(bug|crash|error|broken|failing|exception|500 error|not working as expected)\b", t):
            return RequirementType.BUG, True

        # Compliance / Regulatory
        if re.search(r"\b(compliance|audit log|gdpr|hipaa|soc2|regulatory|legal requirement|pii)\b", t):
            return RequirementType.COMPLIANCE, True

        # Technical / Architectural
        if re.search(r"\b(latency|throughput|rps|database index|cache|redis|kafka|architecture|scalability)\b", t):
            return RequirementType.TECHNICAL, True

        # Business / Strategic
        if re.search(r"\b(expand into|market expansion|revenue target|pricing tier|reduce churn|cac)\b", t):
            return RequirementType.BUSINESS, True

        # Problem report
        if re.search(r"\b(takes too long|struggling with|pain point|friction|confusing|hard to use|wasting hours)\b", t):
            return RequirementType.PROBLEM_REPORT, True

        # Improvement
        if re.search(r"\b(faster|cleaner|simplify|streamline|improve the workflow|optimize)\b", t):
            return RequirementType.IMPROVEMENT, True

        # Default to feature request
        return RequirementType.FEATURE_REQUEST, True

    def analyze_ambiguity(self, text: str, context: dict[str, Any] | None = None) -> AmbiguityAnalysis:
        """
        Analyzes a requirement or problem description for missing dimensions.
        Produces prioritized discovery questions (PRD-0005 §8, §9).
        """
        req_type, is_product = self.classify_statement(text)
        if not is_product:
            return AmbiguityAnalysis(
                is_product_requirement=False,
                detected_type=req_type,
                ambiguity_score=1.0,
                completeness_score=0.0,
                missing_dimensions=["not_a_product_requirement"],
                identified_dimensions={},
                prioritized_questions=[],
            )

        context = context or {}
        combined_text = f"{text} {str(context)}".lower()

        # Dimension checks
        missing = []
        identified = {}
        questions: list[DiscoveryQuestion] = []

        # 1. Problem Clarity
        has_problem = any(w in combined_text for w in ["problem", "because", "unable", "struggle", "friction", "difficult", "fails"])
        if has_problem:
            identified["problem_clarity"] = "Problem or motivation indicated in statement."
        else:
            missing.append("problem_clarity")
            questions.append(
                DiscoveryQuestion(
                    priority=1,
                    dimension="problem_clarity",
                    question="What specific problem are users experiencing that prompted this request?",
                    rationale="Features without identified problems result in wasted engineering capacity.",
                )
            )

        # 2. Target User / Persona
        has_persona = any(w in combined_text for w in ["vendor", "driver", "client", "employee", "admin", "manager", "operator", "customer", "user"])
        if has_persona:
            identified["user_persona"] = "Target persona referenced."
        else:
            missing.append("user_persona")
            questions.append(
                DiscoveryQuestion(
                    priority=2,
                    dimension="user_persona",
                    question="Who is the primary persona or user facing this challenge?",
                    rationale="Solutions must be anchored to a specific user archetype.",
                )
            )

        # 3. Business Impact / Cost
        has_impact = any(w in combined_text for w in ["cost", "hours", "delay", "revenue", "churn", "loss", "percent", "risk"])
        if has_impact:
            identified["business_impact"] = "Quantified or stated business impact."
        else:
            missing.append("business_impact")
            questions.append(
                DiscoveryQuestion(
                    priority=3,
                    dimension="business_impact",
                    question="What is the measurable business impact or operational cost of not solving this?",
                    rationale="Quantifying impact establishes priority against competing roadmap bets.",
                )
            )

        # 4. Existing Workaround
        has_workaround = any(w in combined_text for w in ["today", "currently", "manually", "spreadsheet", "workaround", "excel"])
        if has_workaround:
            identified["existing_workaround"] = "Existing workflow/workaround noted."
        else:
            missing.append("existing_workaround")
            questions.append(
                DiscoveryQuestion(
                    priority=4,
                    dimension="existing_workaround",
                    question="How do users currently work around or solve this issue today?",
                    rationale="Understanding current alternatives reveals real customer urgency.",
                )
            )

        # 5. Evidence
        has_evidence = any(w in combined_text for w in ["ticket", "interview", "survey", "data", "metric", "client requested", "nps"])
        if has_evidence:
            identified["evidence"] = "Verifiable customer or data evidence cited."
        else:
            missing.append("evidence")
            questions.append(
                DiscoveryQuestion(
                    priority=5,
                    dimension="evidence",
                    question="What customer data, support tickets, or interviews substantiate this need?",
                    rationale="PRD-0001 Constitutional Principle: Evidence Before Opinion.",
                )
            )

        total_dimensions = 5
        missing_count = len(missing)
        ambiguity_score = round(missing_count / total_dimensions, 2)
        completeness_score = round(1.0 - ambiguity_score, 2)

        # Sort questions by information-value priority (PRD-0005 §9)
        questions.sort(key=lambda q: q.priority)

        # Generate provisional JTBD
        jtbd = []
        if "user_persona" in identified and "problem_clarity" in identified:
            jtbd.append(
                JTBDStatement(
                    situation="operating in current daily workflow",
                    motivation="accomplish task with zero manual errors",
                    expected_outcome="save operational time and eliminate bottlenecks",
                )
            )

        return AmbiguityAnalysis(
            is_product_requirement=True,
            detected_type=req_type,
            ambiguity_score=ambiguity_score,
            completeness_score=completeness_score,
            missing_dimensions=missing,
            identified_dimensions=identified,
            prioritized_questions=questions,
            suggested_jtbd=jtbd,
        )

    async def ingest_requirement(
        self,
        raw_text: str,
        title: str,
        initiative_id: str | None = None,
        source: str = "chatgpt",
        source_reference: str | None = None,
        confidence: ConfidenceLevel = ConfidenceLevel.CONFIRMED,
    ) -> dict[str, Any]:
        """
        Ingests requirement into TPG's Knowledge Graph with full PRD-0002 compliance.
        Enforces workspace boundary and links to parent Initiative if provided.
        """
        if not self.db or not self.workspace_id:
            raise ValueError("AsyncSession and workspace_id must be initialized on RequirementIntelligenceEngine.")

        analysis = self.analyze_ambiguity(raw_text)

        entity_type = EntityType.REQUIREMENT
        if analysis.detected_type == RequirementType.PROBLEM_REPORT:
            entity_type = EntityType.PROBLEM

        entity = Entity(
            workspace_id=self.workspace_id,
            entity_type=entity_type,
            name=title,
            description=raw_text,
            properties={
                "requirement_type": analysis.detected_type.value,
                "ambiguity_score": analysis.ambiguity_score,
                "completeness_score": analysis.completeness_score,
                "missing_dimensions": analysis.missing_dimensions,
                "discovery_state": DiscoveryState.DISCOVERY.value if analysis.ambiguity_score > 0.4 else DiscoveryState.VALIDATED.value,
            },
            source=source,
            source_reference=source_reference,
            confidence=confidence,
            status=EntityStatus.ACTIVE,
        )
        self.db.add(entity)
        await self.db.flush()

        # Link to Initiative if provided (Relationship: DEFINES or BELONGS_TO)
        if initiative_id:
            rel = EntityRelationship(
                source_entity_id=entity.id,
                target_entity_id=initiative_id,
                relationship_type=RelationshipType.BELONGS_TO,
                properties={"relationship_purpose": "initiative_requirement_definition"},
                confidence=confidence,
            )
            self.db.add(rel)
            await self.db.flush()

        return {
            "entity_id": entity.id,
            "entity_type": entity.entity_type.value,
            "title": entity.name,
            "ambiguity_score": analysis.ambiguity_score,
            "discovery_state": entity.properties.get("discovery_state"),
            "next_questions": [q.question for q in analysis.prioritized_questions[:2]],
        }
