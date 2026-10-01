"""
API Dependencies — Commercial SaaS Multi-Tenant Authentication & Paywall

Shared dependencies injected into API route handlers:
- get_workspace_id: Authenticates the customer's license key, enforces strict
  commercial subscription gating (trial/active/past_due/expired), and resolves
  the request to the customer's isolated Personal Workspace.
- verify_admin_key: Authorizes internal SkynetOrg admin operations (provisioning, renewals).
- verify_api_key: General API key validation.
"""

from datetime import datetime, timezone
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.workspace import Workspace


settings = get_settings()


def _extract_token(x_api_key: str | None, authorization: str | None) -> str | None:
    """Extracts raw token from X-API-Key or Authorization Bearer header."""
    if x_api_key:
        return x_api_key.strip()
    if authorization:
        if authorization.lower().startswith("bearer "):
            return authorization[7:].strip()
        return authorization.strip()
    return None


async def verify_admin_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> str:
    """
    Verifies that the caller possesses the Master Admin API key.
    Used for customer provisioning, license renewals, and administrative controls.
    """
    token = _extract_token(x_api_key, authorization)
    admin_key = settings.admin_api_key or settings.api_key

    # In dev mode with no key configured, permit access for bootstrapping
    if not admin_key and settings.debug:
        return "admin_dev"

    if token and token == admin_key:
        return token

    raise HTTPException(
        status_code=403,
        detail="Admin authorization required. Access denied.",
    )


async def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Validates either the master API key or an active customer license key.
    """
    token = _extract_token(x_api_key, authorization)
    if not token:
        if settings.debug and not settings.api_key and not settings.enforce_commercial_licensing:
            return "dev"
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid commercial license key.",
        )

    # Master key match
    if settings.api_key and token == settings.api_key:
        return token
    if settings.admin_api_key and token == settings.admin_api_key:
        return token

    # Check commercial license
    stmt = select(Workspace).where(Workspace.license_key == token)
    res = await db.execute(stmt)
    ws = res.scalar_one_or_none()
    if not ws:
        raise HTTPException(status_code=401, detail="Invalid API key. Unrecognized commercial license.")

    is_valid, reason = ws.is_license_valid()
    if not is_valid:
        if not ws.is_active:
            raise HTTPException(status_code=403, detail=f"Access Denied: {reason}")
        raise HTTPException(
            status_code=402,
            detail=f"Commercial License Inactive: {reason} Renew at {settings.billing_portal_url} to continue.",
        )

    return token


async def get_workspace_id(
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-ID"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Primary multi-tenant resolution and commercial paywall enforcement dependency.

    1. Resolves token from headers (X-API-Key or Authorization Bearer).
    2. Identifies workspace by unique commercial license key.
    3. Enforces strict paywall:
       - Account suspension -> 403 Forbidden
       - Inactive / past_due / canceled / expired -> 402 Payment Required
    4. Automatically scopes the calling request to the customer's isolated workspace.
    """
    token = _extract_token(x_api_key, authorization)

    # ─── 1. Admin / Master Key Authentication ──────────────────────────
    is_admin = False
    if token:
        if settings.admin_api_key and token == settings.admin_api_key:
            is_admin = True
        elif settings.api_key and token == settings.api_key:
            is_admin = True

    if is_admin:
        # Admin can explicitly target any workspace via X-Workspace-ID
        if x_workspace_id:
            stmt = select(Workspace).where(Workspace.id == x_workspace_id)
            res = await db.execute(stmt)
            ws = res.scalar_one_or_none()
            if ws:
                return ws.id
            raise HTTPException(status_code=404, detail=f"Workspace '{x_workspace_id}' not found.")

        # Default workspace for internal admin testing
        stmt = select(Workspace).limit(1)
        res = await db.execute(stmt)
        ws = res.scalar_one_or_none()
        if ws:
            return ws.id

        # Bootstrap default admin workspace if completely empty
        ws = Workspace(
            owner_email="admin@skynetorg.com",
            owner_name="Skynet Admin",
            name="Skynet Internal Office",
            subscription_tier="enterprise",
            subscription_status="active",
        )
        db.add(ws)
        await db.flush()
        return ws.id

    # ─── 2. Commercial Customer License Authentication ─────────────────
    if token:
        stmt = select(Workspace).where(Workspace.license_key == token)
        res = await db.execute(stmt)
        ws = res.scalar_one_or_none()

        if not ws:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key. Unrecognized commercial license.",
            )

        # Strict Paywall Enforcement
        if settings.enforce_commercial_licensing:
            is_valid, reason = ws.is_license_valid()
            if not is_valid:
                if not ws.is_active:
                    raise HTTPException(
                        status_code=403,
                        detail="Access Denied: Workspace account has been suspended. Please contact support@skynetorg.com.",
                    )
                raise HTTPException(
                    status_code=402,
                    detail=(
                        f"Commercial License Inactive: {reason} "
                        f"Please renew your subscription at {settings.billing_portal_url} to continue using TPG."
                    ),
                )

        return ws.id

    # ─── 3. No Token Provided ──────────────────────────────────────────
    if settings.enforce_commercial_licensing:
        # In development mode with no API keys configured, allow local testing fallback
        if settings.debug and not settings.api_key and not settings.admin_api_key:
            stmt = select(Workspace).limit(1)
            res = await db.execute(stmt)
            ws = res.scalar_one_or_none()
            if ws:
                return ws.id

        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide your TPG commercial license key via the Authorization header.",
        )

    # Legacy/dev fallback when enforcement is disabled
    if x_workspace_id:
        stmt = select(Workspace).where(Workspace.id == x_workspace_id)
        res = await db.execute(stmt)
        ws = res.scalar_one_or_none()
        if ws:
            return ws.id

    stmt = select(Workspace).limit(1)
    res = await db.execute(stmt)
    ws = res.scalar_one_or_none()
    if ws:
        return ws.id

    ws = Workspace(
        owner_email="owner@tpg.local",
        owner_name="Product Owner",
        name="My Product Office",
    )
    db.add(ws)
    await db.flush()
    return ws.id
