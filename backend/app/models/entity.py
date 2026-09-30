"""
Entity & Relationship Models — PRD-0002

The Knowledge Graph is the foundation of TPG's memory.
Every piece of product intelligence is stored as a typed Entity
with explicit Relationships to other entities.

Design decisions:
- Single polymorphic `entities` table with `entity_type` discriminator.
  This keeps the graph queryable and avoids 30+ separate tables in Phase 0.
  As the system matures, high-volume entity types may graduate to dedicated tables.
- Properties are stored as JSONB for schema flexibility. Each entity_type
  has its own expected property shape, validated at the application layer.
- Embeddings stored via pgvector for semantic search across all knowledge.
- Every entity has confidence, source, and status — TPG never stores
  unqualified facts (PRD-0001 principle: Evidence Before Opinion).
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    String,
    DateTime,
    Text,
    ForeignKey,
    Index,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ─── Entity Types ──────────────────────────────────────────────────
# These map directly to the Knowledge Graph entity types from PRD-0002.
# New types are added as each PRD phase is implemented.

class EntityType(str, Enum):
    # ── Phase 0–1: Core ──
    FACT = "fact"                         # Generic remembered fact
    WORKSPACE_CONFIG = "workspace_config" # Workspace settings

    # ── Phase 1: Strategy & Product ──
    STRATEGY = "strategy"
    STRATEGIC_THEME = "strategic_theme"
    OBJECTIVE = "objective"
    STRATEGIC_BET = "strategic_bet"
    ASSUMPTION = "assumption"
    INITIATIVE = "initiative"
    REQUIREMENT = "requirement"
    DECISION = "decision"
    PRD = "prd"

    # ── Phase 2: Customers ──
    CUSTOMER = "customer"
    CONTACT = "contact"
    SIGNAL = "signal"
    PROBLEM = "problem"
    OPPORTUNITY = "opportunity"
    COMMITMENT = "commitment"

    # ── Phase 3: Engineering ──
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    PULL_REQUEST = "pull_request"
    ARCHITECTURE_DECISION = "adr"
    TECHNICAL_DEBT = "technical_debt"
    TECHNICAL_RISK = "technical_risk"

    # ── Phase 4: Quality ──
    TEST_STRATEGY = "test_strategy"
    TEST_CASE = "test_case"
    DEFECT = "defect"
    RELEASE = "release"

    # ── Phase 5: Analytics ──
    METRIC = "metric"
    KPI = "kpi"
    EXPERIMENT = "experiment"
    OUTCOME = "outcome"
    LEARNING = "learning"


class ConfidenceLevel(str, Enum):
    """How confident is TPG in this piece of knowledge?"""
    CONFIRMED = "confirmed"     # Verified from authoritative source
    INFERRED = "inferred"       # Derived from evidence
    ASSUMED = "assumed"          # Reasonable assumption, not verified
    UNKNOWN = "unknown"         # Confidence not assessed


class EntityStatus(str, Enum):
    """Lifecycle status of a knowledge entity."""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    INVALID = "invalid"


class Entity(Base):
    """
    A single node in the TPG Knowledge Graph.

    Every piece of product intelligence — a strategy, a customer problem,
    a requirement, a decision, a defect — is an Entity.

    Properties are stored as flexible JSONB. The expected shape depends
    on entity_type and is validated at the service layer, not the DB layer.
    """

    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ─── Classification ────────────────────────────────────────
    workspace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[EntityType] = mapped_column(
        SAEnum(EntityType, native_enum=False, length=50),
        nullable=False,
        index=True,
    )

    # ─── Identity ──────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Flexible Properties ───────────────────────────────────
    properties: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )

    # ─── Provenance ────────────────────────────────────────────
    source: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Where this knowledge came from: user, gmail, jira, slack, etc."
    )
    source_reference: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="External ID or URL for traceability"
    )
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        SAEnum(ConfidenceLevel, native_enum=False, length=20),
        default=ConfidenceLevel.CONFIRMED,
    )
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(EntityStatus, native_enum=False, length=20),
        default=EntityStatus.ACTIVE,
    )

    # ─── Versioning ────────────────────────────────────────────
    version: Mapped[int] = mapped_column(default=1)

    # ─── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ─── Relationships ─────────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship(
        "Workspace", back_populates="entities"
    )

    # Relationships where this entity is the source
    outgoing_relationships: Mapped[list["EntityRelationship"]] = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )

    # Relationships where this entity is the target
    incoming_relationships: Mapped[list["EntityRelationship"]] = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )

    # ─── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_entities_workspace_type", "workspace_id", "entity_type"),
        Index("ix_entities_workspace_status", "workspace_id", "status"),
        Index(
            "ix_entities_properties",
            "properties",
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        return f"<Entity {self.entity_type.value}:{self.name[:40]}>"


# ─── Relationship Types ────────────────────────────────────────────

class RelationshipType(str, Enum):
    """Types of edges in the Knowledge Graph."""
    # Structural
    BELONGS_TO = "belongs_to"
    CONTAINS = "contains"
    PART_OF = "part_of"

    # Causal / Logical
    CREATED_FROM = "created_from"
    DEPENDS_ON = "depends_on"
    BLOCKS = "blocks"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"

    # Traceability
    IMPLEMENTS = "implements"
    TESTS = "tests"
    TRACES_TO = "traces_to"
    MEASURED_BY = "measured_by"

    # Product
    REQUESTED_BY = "requested_by"
    AFFECTS = "affects"
    RESOLVES = "resolves"
    CAUSED_BY = "caused_by"

    # Generic
    RELATES_TO = "relates_to"


class EntityRelationship(Base):
    """
    An edge in the TPG Knowledge Graph.

    Connects two entities with a typed, directional relationship.
    Relationships carry their own metadata (confidence, properties)
    because the nature of a connection can be uncertain.
    """

    __tablename__ = "entity_relationships"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ─── Edge ──────────────────────────────────────────────────
    source_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SAEnum(RelationshipType, native_enum=False, length=30),
        nullable=False,
    )

    # ─── Metadata ──────────────────────────────────────────────
    properties: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        SAEnum(ConfidenceLevel, native_enum=False, length=20),
        default=ConfidenceLevel.CONFIRMED,
    )

    # ─── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # ─── ORM Relationships ─────────────────────────────────────
    source_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="outgoing_relationships",
    )
    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="incoming_relationships",
    )

    # ─── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index(
            "ix_relationships_source_type",
            "source_entity_id",
            "relationship_type",
        ),
        Index(
            "ix_relationships_target_type",
            "target_entity_id",
            "relationship_type",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Relationship {self.source_entity_id[:8]}"
            f" --{self.relationship_type.value}--> "
            f"{self.target_entity_id[:8]}>"
        )
