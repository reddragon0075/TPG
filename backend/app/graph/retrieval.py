"""
Multi-Stage Graph Retrieval Engine — PRD-0002 §9

Executes structured retrieval over the Knowledge Graph:
1. Authorization & Scoping: Enforce strict workspace boundaries.
2. Intent Classification: Detect decision query, impact analysis, lineage, or general search.
3. Entity Resolution: Locate seed entities using exact, type, and keyword heuristics.
4. Graph Traversal: Pull contextual subgraphs using GraphTraversalEngine.
5. Response Assembly: Synthesize structured evidence, timeline, and confidence.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity, EntityType, EntityStatus
from app.graph.traversal import GraphTraversalEngine, NodeData, EdgeData, LineageResult


class RetrievalIntent(str, Enum):
    WHY_DECISION = "why_decision"           # "Why was X built / approved?"
    IMPACT_ANALYSIS = "impact_analysis"     # "What happens if we change X?"
    LINEAGE_TRACE = "lineage_trace"         # "Trace origin / history of X"
    BLOCKER_ANALYSIS = "blocker_analysis"   # "What is blocking X?"
    GENERAL_SEARCH = "general_search"       # Standard semantic/keyword recall


@dataclass
class EvidenceItem:
    entity_id: str
    entity_type: str
    name: str
    relationship: str
    source: str | None = None
    confidence: str = "confirmed"


@dataclass
class RetrievalResponse:
    query: str
    intent: RetrievalIntent
    seed_entities: list[NodeData]
    evidence: list[EvidenceItem]
    narrative_summary: str
    subgraph_nodes: list[NodeData] = field(default_factory=list)
    subgraph_edges: list[EdgeData] = field(default_factory=list)
    confidence: str = "confirmed"


class GraphRetrievalEngine:
    """
    Executes constitutional retrieval as specified by PRD-0001 (P3: Evidence Before Opinion)
    and PRD-0002 (§9: Retrieval Engine).
    """

    def __init__(self, db: AsyncSession, workspace_id: str):
        self.db = db
        self.workspace_id = workspace_id
        self.traversal = GraphTraversalEngine(db=db, workspace_id=workspace_id)

    def classify_intent(self, query: str) -> RetrievalIntent:
        """
        Classifies the query intent to select the optimal graph traversal strategy.
        """
        q = query.lower()
        if re.search(r"\b(why|reason|rationale|justify|approved)\b", q):
            return RetrievalIntent.WHY_DECISION
        if re.search(r"\b(impact|affect|consequence|break|depend on)\b", q):
            return RetrievalIntent.IMPACT_ANALYSIS
        if re.search(r"\b(trace|history|origin|lineage|provenance|source)\b", q):
            return RetrievalIntent.LINEAGE_TRACE
        if re.search(r"\b(block|blocked|blocker|dependency|obstacle)\b", q):
            return RetrievalIntent.BLOCKER_ANALYSIS
        return RetrievalIntent.GENERAL_SEARCH

    async def resolve_entities(
        self,
        query: str,
        limit: int = 5,
        entity_type: EntityType | None = None,
    ) -> list[Entity]:
        """
        Resolves query text to matching seed entities within the workspace.
        Uses exact, case-insensitive substring, and tag matches.
        """
        stmt = (
            select(Entity)
            .where(Entity.workspace_id == self.workspace_id)
            .where(Entity.status != EntityStatus.ARCHIVED)
        )

        if entity_type:
            stmt = stmt.where(Entity.entity_type == entity_type)

        # Keyword filtering on name and description
        search_term = query.strip()
        # Extract potential entity names or words
        words = [w for w in re.findall(r"\b\w{3,}\b", search_term) if w.lower() not in {"why", "did", "we", "build", "what", "is", "the", "are"}]
        
        conditions = [Entity.name.ilike(f"%{search_term}%")]
        for word in words[:3]:
            conditions.append(Entity.name.ilike(f"%{word}%"))
            conditions.append(Entity.description.ilike(f"%{word}%"))

        stmt = stmt.where(or_(*conditions)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def retrieve(
        self,
        query: str,
        entity_id: str | None = None,
        entity_type: EntityType | None = None,
    ) -> RetrievalResponse:
        """
        Full 5-stage retrieval pipeline.
        """
        intent = self.classify_intent(query)
        seeds: list[Entity] = []

        if entity_id:
            res = await self.db.execute(
                select(Entity)
                .where(Entity.id == entity_id)
                .where(Entity.workspace_id == self.workspace_id)
            )
            entity = res.scalar_one_or_none()
            if entity:
                seeds.append(entity)

        if not seeds:
            seeds = await self.resolve_entities(query, limit=3, entity_type=entity_type)

        if not seeds:
            return RetrievalResponse(
                query=query,
                intent=intent,
                seed_entities=[],
                evidence=[],
                narrative_summary=f"No matching entities found in workspace for query: '{query}'.",
                confidence="unknown",
            )

        seed_node = self.traversal._entity_to_node_data(seeds[0])
        seed_nodes = [self.traversal._entity_to_node_data(s) for s in seeds]

        if intent in (RetrievalIntent.WHY_DECISION, RetrievalIntent.LINEAGE_TRACE):
            # Lineage trace: reconstruct upstream rationale & downstream specs
            lineage = await self.traversal.trace_lineage(seed_node.id, max_depth=4)
            if not lineage:
                return RetrievalResponse(
                    query=query,
                    intent=intent,
                    seed_entities=seed_nodes,
                    evidence=[],
                    narrative_summary=f"Found entity '{seed_node.name}' but could not trace relationships.",
                )

            evidence_items: list[EvidenceItem] = []
            for u in lineage.upstream_nodes:
                evidence_items.append(
                    EvidenceItem(
                        entity_id=u.id,
                        entity_type=u.entity_type,
                        name=u.name,
                        relationship="upstream_driver",
                        source=u.source,
                        confidence=u.confidence,
                    )
                )
            for d in lineage.downstream_nodes:
                evidence_items.append(
                    EvidenceItem(
                        entity_id=d.id,
                        entity_type=d.entity_type,
                        name=d.name,
                        relationship="downstream_outcome",
                        source=d.source,
                        confidence=d.confidence,
                    )
                )

            # Build narrative explanation
            problems = [e.name for e in evidence_items if e.entity_type == "problem"]
            decisions = [e.name for e in evidence_items if e.entity_type == "decision"]
            kpis = [e.name for e in evidence_items if e.entity_type in ("kpi", "metric")]

            summary_parts = [
                f"Knowledge provenance for '{seed_node.name}' ({seed_node.entity_type}):",
            ]
            if problems:
                summary_parts.append(f"• Root Problem(s): {', '.join(problems)}")
            if decisions:
                summary_parts.append(f"• Governing Decision(s): {', '.join(decisions)}")
            if kpis:
                summary_parts.append(f"• Target Metric(s): {', '.join(kpis)}")
            if not problems and not decisions:
                summary_parts.append(f"• Connected entities: {len(evidence_items)} upstream/downstream nodes discovered.")

            narrative = "\n".join(summary_parts)

            all_subgraph_nodes = [seed_node] + lineage.upstream_nodes + lineage.downstream_nodes

            return RetrievalResponse(
                query=query,
                intent=intent,
                seed_entities=seed_nodes,
                evidence=evidence_items,
                narrative_summary=narrative,
                subgraph_nodes=all_subgraph_nodes,
                subgraph_edges=lineage.all_edges,
                confidence=seed_node.confidence,
            )

        elif intent == RetrievalIntent.BLOCKER_ANALYSIS:
            blockers = await self.traversal.find_blockers(seed_node.id)
            evidence_items = [
                EvidenceItem(
                    entity_id=b.id,
                    entity_type=b.entity_type,
                    name=b.name,
                    relationship="blocks",
                    source=b.source,
                    confidence=b.confidence,
                )
                for b in blockers
            ]
            narrative = (
                f"Found {len(blockers)} blocker(s) for '{seed_node.name}': "
                + (", ".join(b.name for b in blockers) if blockers else "None. Clear to proceed.")
            )
            return RetrievalResponse(
                query=query,
                intent=intent,
                seed_entities=seed_nodes,
                evidence=evidence_items,
                narrative_summary=narrative,
                subgraph_nodes=[seed_node] + blockers,
                confidence=seed_node.confidence,
            )

        else:
            # General search / Impact analysis: 2-hop neighborhood exploration
            subgraph = await self.traversal.get_subgraph(seed_node.id, max_depth=2)
            evidence_items = [
                EvidenceItem(
                    entity_id=node.id,
                    entity_type=node.entity_type,
                    name=node.name,
                    relationship="connected",
                    source=node.source,
                    confidence=node.confidence,
                )
                for nid, node in subgraph.nodes.items()
                if nid != seed_node.id
            ]
            narrative = (
                f"Retrieved '{seed_node.name}' ({seed_node.entity_type}) with "
                f"{len(evidence_items)} connected knowledge nodes."
            )
            return RetrievalResponse(
                query=query,
                intent=intent,
                seed_entities=seed_nodes,
                evidence=evidence_items,
                narrative_summary=narrative,
                subgraph_nodes=list(subgraph.nodes.values()),
                subgraph_edges=subgraph.edges,
                confidence=seed_node.confidence,
            )
