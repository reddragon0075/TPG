"""
Memory API — The Knowledge Graph Interface

These endpoints are called by ChatGPT Actions to store and recall
knowledge. They form the core of TPG's persistent memory.

Design decisions:
- Phase 0 uses text-based search (ILIKE). Phase 1 adds pgvector semantic search.
- All queries are workspace-scoped. No cross-workspace leakage.
- Every stored entity includes source and confidence metadata.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.models.workspace import Workspace
from app.models.entity import (
    Entity,
    EntityRelationship,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
    RelationshipType,
)
from app.schemas import (
    MemoryStoreRequest,
    MemoryStoreResponse,
    MemoryRecallRequest,
    MemoryRecallResponse,
    EntityResponse,
    RelationshipCreateRequest,
    RelationshipResponse,
    GraphQueryRequest,
    GraphQueryResponse,
    GraphNeighbor,
)
from app.api.deps import get_workspace_id

router = APIRouter(prefix="/memory", tags=["Memory"])


# ─── Store Knowledge ───────────────────────────────────────────

@router.post("/store", response_model=MemoryStoreResponse)
async def store_knowledge(
    request: MemoryStoreRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Store a piece of knowledge in TPG's Knowledge Graph.

    This is the primary write path for all product intelligence.
    ChatGPT calls this whenever TPG needs to remember something.
    """
    # Enforce commercial tier entity limit
    settings = get_settings()
    ws = await db.get(Workspace, workspace_id)
    if ws and ws.entities_limit > 0:
        count_stmt = select(func.count(Entity.id)).where(Entity.workspace_id == workspace_id)
        current_count = (await db.execute(count_stmt)).scalar() or 0
        if current_count >= ws.entities_limit:
            raise HTTPException(
                status_code=402,
                detail=(
                    f"Entity limit reached ({current_count}/{ws.entities_limit} entities for {ws.subscription_tier} tier). "
                    f"Please upgrade your commercial subscription at {settings.billing_portal_url} to store more knowledge."
                ),
            )

    entity = Entity(
        workspace_id=workspace_id,
        entity_type=EntityType(request.entity_type.value),
        name=request.name,
        description=request.description,
        properties=request.properties,
        source=request.source,
        confidence=ConfidenceLevel(request.confidence.value),
        status=EntityStatus.ACTIVE,
    )

    db.add(entity)
    await db.flush()

    return MemoryStoreResponse(
        entity_id=entity.id,
        entity_type=entity.entity_type.value,
        name=entity.name,
        message=f"Stored {entity.entity_type.value}: '{entity.name}'",
    )


# ─── Recall Knowledge ─────────────────────────────────────────

@router.post("/recall", response_model=MemoryRecallResponse)
async def recall_knowledge(
    request: MemoryRecallRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Search TPG's Knowledge Graph.

    Phase 0: Text-based search (ILIKE on name + description).
    Phase 1: Will add semantic search via pgvector embeddings.
    """
    query = request.query.strip()
    search_pattern = f"%{query}%"

    # Multi-term token matching (matches full string or individual words)
    words = [w for w in query.replace("/", " ").replace("-", " ").split() if len(w) >= 2]
    conditions = [
        Entity.name.ilike(search_pattern),
        Entity.description.ilike(search_pattern),
    ]
    for w in words:
        conditions.append(Entity.name.ilike(f"%{w}%"))
        conditions.append(Entity.description.ilike(f"%{w}%"))

    stmt = (
        select(Entity)
        .where(Entity.workspace_id == workspace_id)
        .where(Entity.status == EntityStatus.ACTIVE)
        .where(or_(*conditions))
        .order_by(Entity.updated_at.desc())
        .limit(request.limit)
    )

    if request.entity_type:
        stmt = stmt.where(
            Entity.entity_type == EntityType(request.entity_type.value)
        )

    result = await db.execute(stmt)
    entities = result.scalars().all()

    return MemoryRecallResponse(
        query=query,
        total_results=len(entities),
        entities=[
            EntityResponse.model_validate(e) for e in entities
        ],
    )


# ─── Get Entity ────────────────────────────────────────────────

@router.get("/entity/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a specific entity by ID."""
    stmt = (
        select(Entity)
        .where(Entity.id == entity_id)
        .where(Entity.workspace_id == workspace_id)
    )
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return EntityResponse.model_validate(entity)


# ─── List Entities by Type ─────────────────────────────────────

@router.get("/entities/{entity_type}", response_model=list[EntityResponse])
async def list_entities(
    entity_type: str,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
):
    """List all active entities of a given type."""
    try:
        et = EntityType(entity_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown entity type: {entity_type}",
        )

    stmt = (
        select(Entity)
        .where(Entity.workspace_id == workspace_id)
        .where(Entity.entity_type == et)
        .where(Entity.status == EntityStatus.ACTIVE)
        .order_by(Entity.updated_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    entities = result.scalars().all()
    return [EntityResponse.model_validate(e) for e in entities]


# ─── Update Entity ─────────────────────────────────────────────

@router.patch("/entity/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    request: MemoryStoreRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing entity."""
    stmt = (
        select(Entity)
        .where(Entity.id == entity_id)
        .where(Entity.workspace_id == workspace_id)
    )
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    entity.name = request.name
    entity.description = request.description
    entity.properties = {**entity.properties, **request.properties}
    entity.confidence = ConfidenceLevel(request.confidence.value)
    entity.version += 1

    await db.flush()
    return EntityResponse.model_validate(entity)


# ─── Delete (Archive) Entity ──────────────────────────────────

@router.delete("/entity/{entity_id}")
async def archive_entity(
    entity_id: str,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Archive an entity (soft delete).
    TPG never hard-deletes knowledge — it archives.
    """
    stmt = (
        select(Entity)
        .where(Entity.id == entity_id)
        .where(Entity.workspace_id == workspace_id)
    )
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    entity.status = EntityStatus.ARCHIVED
    await db.flush()

    return {"message": f"Archived entity: {entity.name}"}


# ─── Create Relationship ──────────────────────────────────────

@router.post("/relationship", response_model=RelationshipResponse)
async def create_relationship(
    request: RelationshipCreateRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a typed relationship between two entities."""
    # Verify both entities exist in this workspace
    for eid in [request.source_entity_id, request.target_entity_id]:
        stmt = (
            select(Entity)
            .where(Entity.id == eid)
            .where(Entity.workspace_id == workspace_id)
        )
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"Entity {eid} not found in workspace",
            )

    rel = EntityRelationship(
        source_entity_id=request.source_entity_id,
        target_entity_id=request.target_entity_id,
        relationship_type=RelationshipType(request.relationship_type.value),
        properties=request.properties,
        confidence=ConfidenceLevel(request.confidence.value),
    )

    db.add(rel)
    await db.flush()

    return RelationshipResponse.model_validate(rel)


# ─── Graph Traversal ──────────────────────────────────────────

@router.post("/graph", response_model=GraphQueryResponse)
async def query_graph(
    request: GraphQueryRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Traverse the Knowledge Graph from a starting entity.

    Returns the center entity and all connected neighbors
    within the specified depth (Phase 0: depth=1 only).
    """
    # Load center entity
    stmt = (
        select(Entity)
        .where(Entity.id == request.entity_id)
        .where(Entity.workspace_id == workspace_id)
    )
    result = await db.execute(stmt)
    center = result.scalar_one_or_none()

    if not center:
        raise HTTPException(status_code=404, detail="Entity not found")

    neighbors: list[GraphNeighbor] = []

    # Outgoing relationships
    out_stmt = (
        select(EntityRelationship)
        .where(EntityRelationship.source_entity_id == request.entity_id)
        .options(selectinload(EntityRelationship.target_entity))
    )
    if request.relationship_types:
        rt_values = [
            RelationshipType(rt.value) for rt in request.relationship_types
        ]
        out_stmt = out_stmt.where(
            EntityRelationship.relationship_type.in_(rt_values)
        )

    out_result = await db.execute(out_stmt)
    for rel in out_result.scalars().all():
        if rel.target_entity and rel.target_entity.workspace_id == workspace_id:
            neighbors.append(
                GraphNeighbor(
                    entity=EntityResponse.model_validate(rel.target_entity),
                    relationship_type=rel.relationship_type.value,
                    direction="outgoing",
                )
            )

    # Incoming relationships
    in_stmt = (
        select(EntityRelationship)
        .where(EntityRelationship.target_entity_id == request.entity_id)
        .options(selectinload(EntityRelationship.source_entity))
    )
    if request.relationship_types:
        in_stmt = in_stmt.where(
            EntityRelationship.relationship_type.in_(rt_values)
        )

    in_result = await db.execute(in_stmt)
    for rel in in_result.scalars().all():
        if rel.source_entity and rel.source_entity.workspace_id == workspace_id:
            neighbors.append(
                GraphNeighbor(
                    entity=EntityResponse.model_validate(rel.source_entity),
                    relationship_type=rel.relationship_type.value,
                    direction="incoming",
                )
            )

    return GraphQueryResponse(
        center_entity=EntityResponse.model_validate(center),
        neighbors=neighbors,
        total_connections=len(neighbors),
    )


# ─── Stats ─────────────────────────────────────────────────────

@router.get("/stats")
async def memory_stats(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Return Knowledge Graph statistics for this workspace."""
    # Total entities
    total_stmt = (
        select(func.count(Entity.id))
        .where(Entity.workspace_id == workspace_id)
        .where(Entity.status == EntityStatus.ACTIVE)
    )
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0

    # Count by type
    type_stmt = (
        select(Entity.entity_type, func.count(Entity.id))
        .where(Entity.workspace_id == workspace_id)
        .where(Entity.status == EntityStatus.ACTIVE)
        .group_by(Entity.entity_type)
    )
    type_result = await db.execute(type_stmt)
    by_type = {row[0].value: row[1] for row in type_result.all()}

    # Total relationships
    rel_stmt = select(func.count(EntityRelationship.id))
    rel_result = await db.execute(rel_stmt)
    total_rels = rel_result.scalar() or 0

    return {
        "total_entities": total,
        "total_relationships": total_rels,
        "entities_by_type": by_type,
    }
