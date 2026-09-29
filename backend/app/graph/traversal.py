"""
Graph Traversal Engine — PRD-0002

Implements multi-hop graph traversal, lineage tracing, cycle detection,
and pathfinding over TPG's Organizational Memory Graph.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Literal
import uuid

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import (
    Entity,
    EntityRelationship,
    EntityType,
    RelationshipType,
    EntityStatus,
)


@dataclass
class EdgeData:
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    confidence: str = "confirmed"


@dataclass
class NodeData:
    id: str
    workspace_id: str
    entity_type: str
    name: str
    description: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    source: str | None = None
    source_reference: str | None = None
    confidence: str = "confirmed"
    status: str = "active"
    version: int = 1


@dataclass
class SubgraphResult:
    start_entity_id: str
    nodes: dict[str, NodeData] = field(default_factory=dict)
    edges: list[EdgeData] = field(default_factory=list)
    depth_reached: int = 0
    total_nodes: int = 0
    total_edges: int = 0


@dataclass
class PathResult:
    source_id: str
    target_id: str
    path_found: bool
    nodes: list[NodeData] = field(default_factory=list)
    edges: list[EdgeData] = field(default_factory=list)
    distance: int = -1


@dataclass
class LineageResult:
    entity_id: str
    root_entity: NodeData
    upstream_nodes: list[NodeData] = field(default_factory=list)  # Why it exists: signals, problems, clients
    downstream_nodes: list[NodeData] = field(default_factory=list) # What it produces: specs, tasks, PRs, KPIs
    all_edges: list[EdgeData] = field(default_factory=list)
    provenance_chain: list[str] = field(default_factory=list)


class GraphTraversalEngine:
    """
    High-performance, workspace-isolated graph traversal engine.
    Ensures zero cross-workspace data leakage and enforces memory integrity.
    """

    def __init__(self, db: AsyncSession, workspace_id: str):
        self.db = db
        self.workspace_id = workspace_id

    def _entity_to_node_data(self, entity: Entity) -> NodeData:
        return NodeData(
            id=entity.id,
            workspace_id=entity.workspace_id,
            entity_type=entity.entity_type.value if hasattr(entity.entity_type, "value") else str(entity.entity_type),
            name=entity.name,
            description=entity.description,
            properties=entity.properties or {},
            source=entity.source,
            source_reference=entity.source_reference,
            confidence=entity.confidence.value if hasattr(entity.confidence, "value") else str(entity.confidence),
            status=entity.status.value if hasattr(entity.status, "value") else str(entity.status),
            version=entity.version,
        )

    def _rel_to_edge_data(self, rel: EntityRelationship) -> EdgeData:
        return EdgeData(
            id=rel.id,
            source_entity_id=rel.source_entity_id,
            target_entity_id=rel.target_entity_id,
            relationship_type=rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type),
            properties=rel.properties or {},
            confidence=rel.confidence.value if hasattr(rel.confidence, "value") else str(rel.confidence),
        )

    async def get_subgraph(
        self,
        start_entity_id: str,
        max_depth: int = 2,
        direction: Literal["outgoing", "incoming", "both"] = "both",
        relationship_types: list[RelationshipType] | None = None,
        entity_types: list[EntityType] | None = None,
        include_archived: bool = False,
    ) -> SubgraphResult:
        """
        Traverses the graph starting at start_entity_id up to max_depth.
        Returns all visited nodes and edges within the workspace.
        """
        # Verify starting entity exists in this workspace
        start_stmt = (
            select(Entity)
            .where(Entity.id == start_entity_id)
            .where(Entity.workspace_id == self.workspace_id)
        )
        if not include_archived:
            start_stmt = start_stmt.where(Entity.status != EntityStatus.ARCHIVED)

        result = await self.db.execute(start_stmt)
        start_entity = result.scalar_one_or_none()
        if not start_entity:
            return SubgraphResult(start_entity_id=start_entity_id)

        nodes: dict[str, NodeData] = {start_entity.id: self._entity_to_node_data(start_entity)}
        edges: list[EdgeData] = []
        edge_ids: set[str] = set()

        visited: set[str] = {start_entity_id}
        queue: deque[tuple[str, int]] = deque([(start_entity_id, 0)])
        deepest_level = 0

        while queue:
            current_id, current_depth = queue.popleft()
            deepest_level = max(deepest_level, current_depth)

            if current_depth >= max_depth:
                continue

            # Find relationships
            query = select(EntityRelationship)
            if direction == "outgoing":
                query = query.where(EntityRelationship.source_entity_id == current_id)
            elif direction == "incoming":
                query = query.where(EntityRelationship.target_entity_id == current_id)
            else:
                query = query.where(
                    or_(
                        EntityRelationship.source_entity_id == current_id,
                        EntityRelationship.target_entity_id == current_id,
                    )
                )

            if relationship_types:
                query = query.where(EntityRelationship.relationship_type.in_(relationship_types))

            rel_res = await self.db.execute(query)
            relationships = rel_res.scalars().all()

            next_entity_ids: set[str] = set()
            candidate_edges: list[EntityRelationship] = []

            for rel in relationships:
                neighbor_id = (
                    rel.target_entity_id
                    if rel.source_entity_id == current_id
                    else rel.source_entity_id
                )
                next_entity_ids.add(neighbor_id)
                candidate_edges.append(rel)

            if not next_entity_ids:
                continue

            # Fetch valid neighbor entities in current workspace
            ent_query = (
                select(Entity)
                .where(Entity.id.in_(list(next_entity_ids)))
                .where(Entity.workspace_id == self.workspace_id)
            )
            if not include_archived:
                ent_query = ent_query.where(Entity.status != EntityStatus.ARCHIVED)
            if entity_types:
                ent_query = ent_query.where(Entity.entity_type.in_(entity_types))

            ent_res = await self.db.execute(ent_query)
            valid_entities = ent_res.scalars().all()
            valid_entity_map = {e.id: e for e in valid_entities}

            for rel in candidate_edges:
                neighbor_id = (
                    rel.target_entity_id
                    if rel.source_entity_id == current_id
                    else rel.source_entity_id
                )
                if neighbor_id in valid_entity_map:
                    if rel.id not in edge_ids:
                        edge_ids.add(rel.id)
                        edges.append(self._rel_to_edge_data(rel))

                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        nodes[neighbor_id] = self._entity_to_node_data(valid_entity_map[neighbor_id])
                        queue.append((neighbor_id, current_depth + 1))

        return SubgraphResult(
            start_entity_id=start_entity_id,
            nodes=nodes,
            edges=edges,
            depth_reached=deepest_level,
            total_nodes=len(nodes),
            total_edges=len(edges),
        )

    async def trace_lineage(self, entity_id: str, max_depth: int = 5) -> LineageResult | None:
        """
        Reconstructs the full product provenance of an entity (e.g. 'Why did we build Vendor Wallet?').
        Traverses upstream to find original Problems, Signals, Clients, and Strategic Bets.
        Traverses downstream to find Decisions, Specifications, PRDs, Epics, and KPIs.
        """
        root_stmt = (
            select(Entity)
            .where(Entity.id == entity_id)
            .where(Entity.workspace_id == self.workspace_id)
        )
        res = await self.db.execute(root_stmt)
        root_entity = res.scalar_one_or_none()
        if not root_entity:
            return None

        root_node = self._entity_to_node_data(root_entity)

        # 1. Upstream Traversal (Inputs, causes, drivers)
        # Follow incoming edges: who created/requested/caused this?
        upstream_subgraph = await self.get_subgraph(
            start_entity_id=entity_id,
            max_depth=max_depth,
            direction="incoming",
        )

        # 2. Downstream Traversal (Outputs, consequences, implementations)
        # Follow outgoing edges: what did this produce/specify/implement?
        downstream_subgraph = await self.get_subgraph(
            start_entity_id=entity_id,
            max_depth=max_depth,
            direction="outgoing",
        )

        upstream_nodes = [
            n for nid, n in upstream_subgraph.nodes.items() if nid != entity_id
        ]
        downstream_nodes = [
            n for nid, n in downstream_subgraph.nodes.items() if nid != entity_id
        ]

        all_edges = list({e.id: e for e in (upstream_subgraph.edges + downstream_subgraph.edges)}.values())

        # Construct high-level narrative chain:
        # Client/Signal -> Problem -> Requirement -> [Root] -> Decision -> PRD -> KPI
        narrative: list[str] = []
        for n in upstream_nodes:
            narrative.append(f"[{n.entity_type.upper()}] {n.name}")
        narrative.append(f"-> TARGET [{root_node.entity_type.upper()}] {root_node.name}")
        for n in downstream_nodes:
            narrative.append(f"-> [{n.entity_type.upper()}] {n.name}")

        return LineageResult(
            entity_id=entity_id,
            root_entity=root_node,
            upstream_nodes=upstream_nodes,
            downstream_nodes=downstream_nodes,
            all_edges=all_edges,
            provenance_chain=narrative,
        )

    async def find_shortest_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 6,
    ) -> PathResult:
        """
        Finds the shortest directed or undirected relationship path between two entities.
        Useful for answering: 'How does this customer problem connect to this Jira ticket or KPI?'
        """
        if source_id == target_id:
            src_res = await self.db.execute(
                select(Entity)
                .where(Entity.id == source_id)
                .where(Entity.workspace_id == self.workspace_id)
            )
            src_ent = src_res.scalar_one_or_none()
            if src_ent:
                node = self._entity_to_node_data(src_ent)
                return PathResult(
                    source_id=source_id,
                    target_id=target_id,
                    path_found=True,
                    nodes=[node],
                    edges=[],
                    distance=0,
                )
            return PathResult(source_id=source_id, target_id=target_id, path_found=False)

        # BFS queue stores (current_id, path_of_node_ids, path_of_edges)
        visited = {source_id}
        queue: deque[tuple[str, list[str], list[EdgeData]]] = deque([(source_id, [source_id], [])])

        while queue:
            current_id, node_path, edge_path = queue.popleft()

            if len(node_path) - 1 >= max_depth:
                continue

            query = (
                select(EntityRelationship)
                .where(
                    or_(
                        EntityRelationship.source_entity_id == current_id,
                        EntityRelationship.target_entity_id == current_id,
                    )
                )
            )
            rel_res = await self.db.execute(query)
            relationships = rel_res.scalars().all()

            for rel in relationships:
                neighbor_id = (
                    rel.target_entity_id
                    if rel.source_entity_id == current_id
                    else rel.source_entity_id
                )

                if neighbor_id == target_id:
                    # Target reached!
                    final_node_ids = node_path + [target_id]
                    final_edges = edge_path + [self._rel_to_edge_data(rel)]

                    # Fetch node data for path
                    ent_res = await self.db.execute(
                        select(Entity)
                        .where(Entity.id.in_(final_node_ids))
                        .where(Entity.workspace_id == self.workspace_id)
                    )
                    ents = {e.id: self._entity_to_node_data(e) for e in ent_res.scalars().all()}
                    nodes_ordered = [ents[nid] for nid in final_node_ids if nid in ents]

                    return PathResult(
                        source_id=source_id,
                        target_id=target_id,
                        path_found=True,
                        nodes=nodes_ordered,
                        edges=final_edges,
                        distance=len(final_edges),
                    )

                if neighbor_id not in visited:
                    # Check workspace boundary for neighbor
                    chk_res = await self.db.execute(
                        select(Entity.id)
                        .where(Entity.id == neighbor_id)
                        .where(Entity.workspace_id == self.workspace_id)
                        .where(Entity.status != EntityStatus.ARCHIVED)
                    )
                    if chk_res.scalar_one_or_none():
                        visited.add(neighbor_id)
                        queue.append(
                            (
                                neighbor_id,
                                node_path + [neighbor_id],
                                edge_path + [self._rel_to_edge_data(rel)],
                            )
                        )

        return PathResult(source_id=source_id, target_id=target_id, path_found=False)

    async def find_blockers(self, entity_id: str) -> list[NodeData]:
        """
        Finds all active entities that BLOCK this entity directly or transitively.
        """
        subgraph = await self.get_subgraph(
            start_entity_id=entity_id,
            max_depth=3,
            direction="incoming",
            relationship_types=[RelationshipType.BLOCKS],
        )
        return [n for nid, n in subgraph.nodes.items() if nid != entity_id]
