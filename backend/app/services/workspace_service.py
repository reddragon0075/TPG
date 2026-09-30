"""
Workspace & RBAC Security Service — PRD-0003, PRD-0001 §385-§416

Implements:
1. Personal & Organization Workspace Isolation (PRD-0003 §4-§6)
2. Workspace Memory Aggregation & Statistics (PRD-0003 §5)
3. Full Workspace Export & Portability (PRD-0003 §6)
4. Workspace Reset & Knowledge Purge (PRD-0003 §6)
5. Role-Based Access Control (RBAC) Permission Matrix Enforcement (PRD-0001 §406-§415)

Constitutional Principle:
- Organization owns memory; Personal workspaces are completely isolated.
- Zero authorization leakage.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.entity import Entity, EntityRelationship, EntityType
from app.models.connector import Connector


# ─── Roles & Permissions ───────────────────────────────────────────

class UserRole(str, Enum):
    CEO = "CEO"
    SR_PM = "SR_PM"
    JR_PM = "JR_PM"
    QA_LEAD = "QA_LEAD"
    VIEWER = "VIEWER"


class ResourceType(str, Enum):
    ROADMAP = "roadmap"
    PRD = "prd"
    CLIENT_CONTRACTS = "client_contracts"
    BUDGET = "budget"
    SPRINT_ANALYTICS = "sprint_analytics"
    DECISIONS = "decisions"


# Permission Matrix from PRD-0001 §406
ROLE_PERMISSIONS: dict[UserRole, dict[ResourceType, str]] = {
    UserRole.CEO: {
        ResourceType.ROADMAP: "FULL",
        ResourceType.PRD: "FULL",
        ResourceType.CLIENT_CONTRACTS: "FULL",
        ResourceType.BUDGET: "FULL",
        ResourceType.SPRINT_ANALYTICS: "FULL",
        ResourceType.DECISIONS: "FULL",
    },
    UserRole.SR_PM: {
        ResourceType.ROADMAP: "FULL",
        ResourceType.PRD: "FULL",
        ResourceType.CLIENT_CONTRACTS: "READ",
        ResourceType.BUDGET: "NONE",
        ResourceType.SPRINT_ANALYTICS: "FULL",
        ResourceType.DECISIONS: "FULL",
    },
    UserRole.JR_PM: {
        ResourceType.ROADMAP: "READ",
        ResourceType.PRD: "ASSIGNED",
        ResourceType.CLIENT_CONTRACTS: "NONE",
        ResourceType.BUDGET: "NONE",
        ResourceType.SPRINT_ANALYTICS: "FULL",
        ResourceType.DECISIONS: "RELEVANT",
    },
    UserRole.QA_LEAD: {
        ResourceType.ROADMAP: "NONE",
        ResourceType.PRD: "ASSIGNED",
        ResourceType.CLIENT_CONTRACTS: "NONE",
        ResourceType.BUDGET: "NONE",
        ResourceType.SPRINT_ANALYTICS: "FULL",
        ResourceType.DECISIONS: "READ",
    },
    UserRole.VIEWER: {
        ResourceType.ROADMAP: "READ",
        ResourceType.PRD: "READ",
        ResourceType.CLIENT_CONTRACTS: "NONE",
        ResourceType.BUDGET: "NONE",
        ResourceType.SPRINT_ANALYTICS: "READ",
        ResourceType.DECISIONS: "READ",
    },
}


# ─── Workspace Service Implementation ──────────────────────────────

class WorkspaceService:
    """
    Handles workspace health, export, purge, and RBAC authorization verification.
    """

    def __init__(self, db: AsyncSession, workspace_id: str):
        self.db = db
        self.workspace_id = workspace_id

    # ─── 1. Identity & Health ──────────────────────────────────────

    async def get_workspace_info(self) -> dict[str, Any] | None:
        """Retrieves details of the current active workspace."""
        stmt = select(Workspace).where(Workspace.id == self.workspace_id)
        res = await self.db.execute(stmt)
        ws = res.scalar_one_or_none()
        if not ws:
            return None

        return {
            "workspace_id": ws.id,
            "name": ws.name,
            "owner_email": ws.owner_email,
            "owner_name": ws.owner_name,
            "workspace_type": getattr(ws, "workspace_type", "personal"),
            "created_at": ws.created_at.isoformat() if ws.created_at else None,
        }

    async def get_aggregated_stats(self) -> dict[str, Any]:
        """Calculates total counts of all knowledge entities, relationships, and connectors."""
        # Count entities grouped by type
        stmt_entities = (
            select(Entity.entity_type, func.count(Entity.id))
            .where(Entity.workspace_id == self.workspace_id)
            .group_by(Entity.entity_type)
        )
        res_entities = await self.db.execute(stmt_entities)
        entity_counts = {str(k.value): count for k, count in res_entities.all()}

        # Total relationships
        stmt_rel = (
            select(func.count(EntityRelationship.id))
            .join(Entity, EntityRelationship.source_entity_id == Entity.id)
            .where(Entity.workspace_id == self.workspace_id)
        )
        res_rel = await self.db.execute(stmt_rel)
        total_relationships = res_rel.scalar() or 0

        # Total connectors
        stmt_conn = (
            select(func.count(Connector.id))
            .where(Connector.workspace_id == self.workspace_id)
        )
        res_conn = await self.db.execute(stmt_conn)
        total_connectors = res_conn.scalar() or 0

        total_entities = sum(entity_counts.values())

        return {
            "workspace_id": self.workspace_id,
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "total_connectors": total_connectors,
            "entities_by_type": entity_counts,
        }

    # ─── 2. Full Workspace Export & Portability ───────────────────

    async def export_workspace_snapshot(self) -> dict[str, Any]:
        """
        Exports the entire Knowledge Graph of the workspace for offline backup or migration.
        """
        # 1. Fetch all entities
        stmt_ent = select(Entity).where(Entity.workspace_id == self.workspace_id)
        res_ent = await self.db.execute(stmt_ent)
        entities = res_ent.scalars().all()

        entity_ids = {e.id for e in entities}

        # 2. Fetch all relationships
        stmt_rel = select(EntityRelationship).where(EntityRelationship.source_entity_id.in_(entity_ids))
        relationships = []
        if entity_ids:
            res_rel = await self.db.execute(stmt_rel)
            relationships = res_rel.scalars().all()

        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "workspace_id": self.workspace_id,
            "entities": [
                {
                    "id": e.id,
                    "entity_type": e.entity_type.value,
                    "name": e.name,
                    "description": e.description,
                    "properties": e.properties,
                    "confidence": e.confidence.value,
                    "status": e.status.value,
                }
                for e in entities
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source_id": r.source_entity_id,
                    "target_id": r.target_entity_id,
                    "relationship_type": r.relationship_type.value,
                    "properties": r.properties,
                }
                for r in relationships
            ],
        }

    # ─── 3. Workspace Purge / Reset ────────────────────────────────

    async def reset_workspace_knowledge(self) -> dict[str, Any]:
        """
        Deletes all entities and relationships in the workspace while preserving the workspace shell.
        """
        # Delete entities (cascades to relationships)
        stmt = delete(Entity).where(Entity.workspace_id == self.workspace_id)
        res = await self.db.execute(stmt)
        await self.db.flush()

        return {
            "workspace_id": self.workspace_id,
            "deleted_entities_count": res.rowcount or 0,
            "status": "PURGED",
        }

    # ─── 4. RBAC Authorization Evaluation ──────────────────────────

    @staticmethod
    def check_permission(role: UserRole, resource: ResourceType) -> dict[str, Any]:
        """
        Evaluates whether a role is authorized to access a given resource.
        Returns authorization decision and permission level (FULL, READ, ASSIGNED, NONE).
        """
        role_rules = ROLE_PERMISSIONS.get(role, {})
        level = role_rules.get(resource, "NONE")
        is_allowed = level in ("FULL", "READ", "ASSIGNED", "RELEVANT")

        return {
            "role": role.value,
            "resource": resource.value,
            "permission_level": level,
            "is_authorized": is_allowed,
        }
