"""
Commercial SaaS Licensing & Subscription Service

Handles customer provisioning, license issuance, cryptographic key generation,
multi-tenant workspace allocation, tier enforcement, renewals, and billing webhooks.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.workspace import Workspace
from app.models.entity import Entity
from app.models.connector import Connector


settings = get_settings()

TIER_LIMITS: dict[str, dict[str, int]] = {
    "trial": {"entities": 500, "connectors": 2, "default_days": 14},
    "starter": {"entities": 1500, "connectors": 3, "default_days": 30},
    "pro": {"entities": 10000, "connectors": 10, "default_days": 365},
    "enterprise": {"entities": 100000, "connectors": 50, "default_days": 365},
}


class CommercialService:
    """Service layer managing commercial licenses, subscriptions, and paywall rules."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_license_key(tier: str = "pro") -> str:
        """Generates a secure commercial license key."""
        prefix = "tpg_trial" if tier == "trial" else "tpg_live"
        return f"{prefix}_{secrets.token_hex(16)}"

    async def provision_customer(
        self,
        owner_email: str,
        owner_name: str,
        company_name: str = "Product Office",
        subscription_tier: str = "pro",
        duration_days: int | None = None,
        stripe_customer_id: str | None = None,
    ) -> Workspace:
        """
        Provisions a new paying or trialing customer account with a dedicated Personal Workspace.
        Generates an active commercial license key.
        """
        tier = subscription_tier.lower()
        tier_cfg = TIER_LIMITS.get(tier, TIER_LIMITS["pro"])
        days = duration_days if duration_days is not None else tier_cfg["default_days"]

        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=days)
        trial_ends_at = valid_until if tier == "trial" else None
        status = "trialing" if tier == "trial" else "active"
        license_key = self.generate_license_key(tier=tier)

        # Check if workspace already exists for this email
        stmt = select(Workspace).where(Workspace.owner_email == owner_email)
        res = await self.db.execute(stmt)
        workspace = res.scalar_one_or_none()

        if workspace:
            # Upgrade / re-issue existing workspace
            workspace.owner_name = owner_name
            workspace.name = company_name
            workspace.subscription_tier = tier
            workspace.subscription_status = status
            workspace.license_key = license_key
            workspace.valid_until = valid_until
            workspace.trial_ends_at = trial_ends_at
            workspace.entities_limit = tier_cfg["entities"]
            workspace.connectors_limit = tier_cfg["connectors"]
            workspace.is_active = True
            if stripe_customer_id:
                workspace.stripe_customer_id = stripe_customer_id
        else:
            workspace = Workspace(
                owner_email=owner_email,
                owner_name=owner_name,
                name=company_name,
                subscription_tier=tier,
                subscription_status=status,
                license_key=license_key,
                valid_until=valid_until,
                trial_ends_at=trial_ends_at,
                stripe_customer_id=stripe_customer_id,
                entities_limit=tier_cfg["entities"],
                connectors_limit=tier_cfg["connectors"],
                is_active=True,
            )
            self.db.add(workspace)

        await self.db.flush()
        return workspace

    async def get_license_status(self, workspace_id: str) -> dict[str, Any]:
        """Retrieves comprehensive license status, metrics, and limits for a workspace."""
        ws = await self.db.get(Workspace, workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found.")

        # Entity and Connector counts
        count_e_stmt = select(func.count(Entity.id)).where(Entity.workspace_id == workspace_id)
        e_count = (await self.db.execute(count_e_stmt)).scalar() or 0

        count_c_stmt = select(func.count(Connector.id)).where(Connector.workspace_id == workspace_id)
        c_count = (await self.db.execute(count_c_stmt)).scalar() or 0

        # Calculate validity and days remaining
        is_valid, reason = ws.is_license_valid()
        days_remaining = None
        if ws.valid_until:
            now = datetime.now(timezone.utc)
            vu = ws.valid_until if ws.valid_until.tzinfo else ws.valid_until.replace(tzinfo=timezone.utc)
            delta = vu - now
            days_remaining = max(0, delta.days)

        masked_key = "None"
        if ws.license_key:
            prefix = ws.license_key[:12]
            masked_key = f"{prefix}...{ws.license_key[-4:]}"

        return {
            "workspace_id": ws.id,
            "owner_email": ws.owner_email,
            "owner_name": ws.owner_name,
            "company_name": ws.name,
            "subscription_tier": ws.subscription_tier,
            "subscription_status": ws.subscription_status,
            "license_key_masked": masked_key,
            "valid_until": ws.valid_until.isoformat() if ws.valid_until else None,
            "days_remaining": days_remaining,
            "is_valid": is_valid,
            "status_message": reason,
            "entities_count": e_count,
            "entities_limit": ws.entities_limit,
            "connectors_count": c_count,
            "connectors_limit": ws.connectors_limit,
            "billing_portal_url": settings.billing_portal_url,
        }

    async def renew_subscription(
        self,
        workspace_id: str,
        extend_days: int = 365,
        new_tier: str | None = None,
    ) -> Workspace:
        """Extends subscription validity period and restores active status."""
        ws = await self.db.get(Workspace, workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found.")

        now = datetime.now(timezone.utc)
        base_time = now
        if ws.valid_until:
            vu = ws.valid_until if ws.valid_until.tzinfo else ws.valid_until.replace(tzinfo=timezone.utc)
            if vu > now:
                base_time = vu

        ws.valid_until = base_time + timedelta(days=extend_days)
        ws.subscription_status = "active"
        ws.is_active = True

        if new_tier:
            tier = new_tier.lower()
            tier_cfg = TIER_LIMITS.get(tier, TIER_LIMITS["pro"])
            ws.subscription_tier = tier
            ws.entities_limit = tier_cfg["entities"]
            ws.connectors_limit = tier_cfg["connectors"]

        await self.db.flush()
        return ws

    async def revoke_license(self, workspace_id: str, reason: str = "canceled") -> Workspace:
        """Revokes or suspends a commercial license."""
        ws = await self.db.get(Workspace, workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found.")

        if reason == "suspended":
            ws.is_active = False
        else:
            ws.subscription_status = reason

        await self.db.flush()
        return ws

    async def handle_stripe_event(self, event_type: str, event_data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes Stripe subscription lifecycle events.
        """
        obj = event_data.get("object", {})
        customer_id = obj.get("customer")
        subscription_id = obj.get("id")

        if not customer_id:
            return {"status": "ignored", "reason": "no_customer_id"}

        stmt = select(Workspace).where(Workspace.stripe_customer_id == customer_id)
        res = await self.db.execute(stmt)
        ws = res.scalar_one_or_none()
        if not ws:
            return {"status": "ignored", "reason": f"no_workspace_for_stripe_customer_{customer_id}"}

        if event_type == "invoice.payment_succeeded":
            # Renew subscription for 30 or 365 days
            await self.renew_subscription(ws.id, extend_days=30)
            return {"status": "processed", "action": "renewed", "workspace_id": ws.id}

        elif event_type == "customer.subscription.deleted":
            await self.revoke_license(ws.id, reason="canceled")
            return {"status": "processed", "action": "canceled", "workspace_id": ws.id}

        elif event_type == "customer.subscription.updated":
            status = obj.get("status")
            if status == "past_due":
                ws.subscription_status = "past_due"
            elif status == "active":
                ws.subscription_status = "active"
            await self.db.flush()
            return {"status": "processed", "action": f"status_updated_to_{status}", "workspace_id": ws.id}

        return {"status": "unhandled_event", "event_type": event_type}
