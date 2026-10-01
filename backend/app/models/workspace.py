"""
Workspace Model — PRD-0003

Every TPG V1 subscription creates one private Personal Workspace.
All entities belong to exactly one workspace. Orphan entities are invalid.
The workspace is the privacy boundary — zero cross-workspace data leakage.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Text, Integer
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

    # ─── Commercial Licensing & Subscription ───────────────────
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default="pro", nullable=False
    )  # trial, starter, pro, enterprise
    subscription_status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # trialing, active, past_due, canceled, expired
    license_key: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    entities_limit: Mapped[int] = mapped_column(
        Integer, default=5000, nullable=False
    )
    connectors_limit: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False
    )

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

    def is_license_valid(self) -> tuple[bool, str]:
        """
        Validates the workspace's commercial license.
        Returns (is_valid, reason).
        """
        if not self.is_active:
            return False, "Workspace account has been suspended."

        if self.subscription_status == "canceled":
            return False, "Commercial subscription has been canceled."

        if self.subscription_status == "past_due":
            return False, "Commercial subscription payment is past due."

        if self.subscription_status == "expired":
            return False, "Commercial subscription has expired."

        now = datetime.now(timezone.utc)
        if self.valid_until is not None:
            vu = self.valid_until if self.valid_until.tzinfo else self.valid_until.replace(tzinfo=timezone.utc)
            if now > vu:
                return False, f"Commercial license expired on {vu.strftime('%Y-%m-%d')}."

        if self.subscription_status == "trialing" and self.trial_ends_at is not None:
            te = self.trial_ends_at if self.trial_ends_at.tzinfo else self.trial_ends_at.replace(tzinfo=timezone.utc)
            if now > te:
                return False, f"Commercial trial expired on {te.strftime('%Y-%m-%d')}."

        return True, "License valid"

    # ─── Relationships ─────────────────────────────────────────
    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="workspace", cascade="all, delete-orphan"
    )
    connectors: Mapped[list["Connector"]] = relationship(
        "Connector", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace {self.id} owner={self.owner_email}>"
