"""
Workspace Model — PRD-0003

Every TPG V1 subscription creates one private Personal Workspace.
All entities belong to exactly one workspace. Orphan entities are invalid.
The workspace is the privacy boundary — zero cross-workspace data leakage.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Workspace(Base):
    """
    A Personal Workspace is the atomic privacy unit in TPG V1.

    One user = one workspace = one TPG.
    All knowledge, connectors, and intelligence belong to this workspace.
    """

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ─── Owner Identity ────────────────────────────────────────
    owner_email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    owner_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # ─── Workspace Metadata ────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, default="My Product Office"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="workspace", cascade="all, delete-orphan"
    )
    connectors: Mapped[list["Connector"]] = relationship(
        "Connector", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace {self.id} owner={self.owner_email}>"
