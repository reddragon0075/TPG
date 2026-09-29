"""
Connector Model — PRD-0004

Represents an authorized connection to an external data source.
Connectors belong to a workspace and carry OAuth tokens.

IMPORTANT: Token values are encrypted at rest. TPG never stores
raw secrets as ordinary knowledge (PRD-0001, PRD-0003).
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConnectorType(str, Enum):
    """Supported external data sources."""
    GMAIL = "gmail"
    CALENDAR = "calendar"
    SLACK = "slack"
    JIRA = "jira"
    GITHUB = "github"


class ConnectorStatus(str, Enum):
    """Health state of a connector."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"
    RATE_LIMITED = "rate_limited"


class Connector(Base):
    """
    An authorized read-only connection to an external system.

    Connectors observe the user's ecosystem and extract signals
    into the Knowledge Graph. They never write to external systems
    unless explicitly authorized by workspace policy.
    """

    __tablename__ = "connectors"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ─── Ownership ─────────────────────────────────────────────
    workspace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ─── Connector Identity ────────────────────────────────────
    connector_type: Mapped[ConnectorType] = mapped_column(
        SAEnum(ConnectorType, native_enum=False, length=20),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    # ─── Authentication ────────────────────────────────────────
    # Tokens stored encrypted. In V1, encryption uses Fernet
    # with a key derived from the workspace secret.
    access_token_encrypted: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    refresh_token_encrypted: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ─── Sync State ────────────────────────────────────────────
    status: Mapped[ConnectorStatus] = mapped_column(
        SAEnum(ConnectorStatus, native_enum=False, length=20),
        default=ConnectorStatus.DISCONNECTED,
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_cursor: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict,
        comment="Connector-specific sync state (page tokens, timestamps, etc.)",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # ─── Configuration ─────────────────────────────────────────
    config: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict,
        comment="Connector-specific settings (channels, repos, projects, etc.)",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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
        "Workspace", back_populates="connectors"
    )

    def __repr__(self) -> str:
        return f"<Connector {self.connector_type.value} status={self.status.value}>"
