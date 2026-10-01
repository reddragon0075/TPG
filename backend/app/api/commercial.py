"""
Commercial Licensing & Subscription API

Endpoints:
- POST /commercial/licenses/provision: Issue new customer license & personal workspace (Admin)
- GET /commercial/license/status: Check license status and resource limits (Authenticated customer)
- POST /commercial/licenses/{workspace_id}/renew: Extend subscription period (Admin)
- POST /commercial/licenses/{workspace_id}/revoke: Cancel or suspend license (Admin)
- POST /commercial/webhook/stripe: Process automated payment and subscription webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id, verify_admin_key
from app.services.commercial_service import CommercialService
from app.schemas import (
    CommercialLicenseProvisionRequest,
    CommercialLicenseProvisionResponse,
    CommercialLicenseStatusResponse,
    CommercialLicenseRenewRequest,
    CommercialLicenseRevokeRequest,
)

router = APIRouter(prefix="/commercial", tags=["Commercial Licensing & SaaS"])


@router.post("/licenses/provision", response_model=CommercialLicenseProvisionResponse)
async def provision_customer_license(
    request: CommercialLicenseProvisionRequest,
    admin_token: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Provisions a new paying or trialing customer account.
    Generates a secure commercial license key and isolated Personal Workspace.
    """
    service = CommercialService(db=db)
    ws = await service.provision_customer(
        owner_email=request.owner_email,
        owner_name=request.owner_name,
        company_name=request.company_name,
        subscription_tier=request.subscription_tier,
        duration_days=request.duration_days,
        stripe_customer_id=request.stripe_customer_id,
    )
    await db.commit()

    instructions = (
        f"1. In your OpenAI Custom GPT or ChatGPT Action setup, configure Authentication as 'API Key' -> 'Bearer'. "
        f"2. Enter the generated license key as the token value. "
        f"3. All requests will automatically resolve to your private '{ws.name}' workspace."
    )

    return CommercialLicenseProvisionResponse(
        workspace_id=ws.id,
        license_key=ws.license_key or "",
        owner_email=ws.owner_email,
        owner_name=ws.owner_name,
        company_name=ws.name,
        subscription_tier=ws.subscription_tier,
        subscription_status=ws.subscription_status,
        valid_until=ws.valid_until.isoformat() if ws.valid_until else None,
        entities_limit=ws.entities_limit,
        connectors_limit=ws.connectors_limit,
        setup_instructions=instructions,
    )


@router.get("/license/status", response_model=CommercialLicenseStatusResponse)
async def check_current_license_status(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns live commercial license status, expiration, and resource limits for the calling customer.
    """
    service = CommercialService(db=db)
    try:
        status = await service.get_license_status(workspace_id)
        return CommercialLicenseStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/licenses/{workspace_id}/renew")
async def renew_customer_subscription(
    workspace_id: str,
    request: CommercialLicenseRenewRequest,
    admin_token: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Extends a customer's subscription period and re-activates access.
    """
    service = CommercialService(db=db)
    try:
        ws = await service.renew_subscription(
            workspace_id=workspace_id,
            extend_days=request.extend_days,
            new_tier=request.new_tier,
        )
        await db.commit()
        return {
            "status": "success",
            "message": f"Subscription renewed for {request.extend_days} days.",
            "workspace_id": ws.id,
            "subscription_tier": ws.subscription_tier,
            "subscription_status": ws.subscription_status,
            "valid_until": ws.valid_until.isoformat() if ws.valid_until else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/licenses/{workspace_id}/revoke")
async def revoke_customer_license(
    workspace_id: str,
    request: CommercialLicenseRevokeRequest,
    admin_token: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Immediately revokes or suspends a customer's commercial license.
    """
    service = CommercialService(db=db)
    try:
        ws = await service.revoke_license(
            workspace_id=workspace_id,
            reason=request.reason,
        )
        await db.commit()
        return {
            "status": "success",
            "message": f"License updated with status '{request.reason}'.",
            "workspace_id": ws.id,
            "subscription_status": ws.subscription_status,
            "is_active": ws.is_active,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/webhook/stripe")
async def stripe_billing_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Receives and processes automated Stripe billing lifecycle events.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    event_type = payload.get("type", "")
    data = payload.get("data", {})

    service = CommercialService(db=db)
    result = await service.handle_stripe_event(event_type=event_type, event_data=data)
    await db.commit()

    return {"received": True, "result": result}
