"""
Commercial SaaS Licensing & Paywall Test Suite

Tests:
1. Customer provisioning (Pro, Trial)
2. License key generation and validation
3. Strict Paywall HTTP enforcement (401, 402, 403)
4. Subscription renewal & recovery
5. Quota limit enforcement (Entities, Connectors)
6. Multi-tenant customer data isolation
7. Commercial License Status API
8. Stripe webhook handling
"""

import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import get_db
from app.models.workspace import Workspace
from app.models.entity import Entity, EntityType, ConfidenceLevel, EntityStatus
from app.services.commercial_service import CommercialService
from app.config import get_settings


settings = get_settings()


@pytest.mark.asyncio
async def test_commercial_provisioning_pro(test_session):
    """Verifies provisioning a Pro commercial customer."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="founder@acmeproducts.io",
        owner_name="Alice Founder",
        company_name="Acme Products",
        subscription_tier="pro",
        duration_days=365,
    )
    await test_session.commit()

    assert ws.id is not None
    assert ws.license_key.startswith("tpg_live_")
    assert ws.subscription_tier == "pro"
    assert ws.subscription_status == "active"
    assert ws.entities_limit == 10000
    assert ws.connectors_limit == 10
    assert ws.valid_until is not None

    is_valid, msg = ws.is_license_valid()
    assert is_valid is True
    assert msg == "License valid"


@pytest.mark.asyncio
async def test_commercial_provisioning_trial(test_session):
    """Verifies provisioning a 14-day Trial customer."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="tester@startup.com",
        owner_name="Bob Tester",
        company_name="Bob Startup",
        subscription_tier="trial",
        duration_days=14,
    )
    await test_session.commit()

    assert ws.license_key.startswith("tpg_trial_")
    assert ws.subscription_tier == "trial"
    assert ws.subscription_status == "trialing"
    assert ws.entities_limit == 500
    assert ws.connectors_limit == 2
    assert ws.trial_ends_at is not None

    is_valid, _ = ws.is_license_valid()
    assert is_valid is True


@pytest.mark.asyncio
async def test_strict_paywall_enforcement(test_session):
    """Verifies 401 Unauthorized for missing or invalid license keys."""
    # We create an isolated client WITHOUT dependency overrides on get_workspace_id
    # to test the real paywall dependency.
    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    # Save original overrides
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. No auth headers -> 401
            resp = await client.get("/workspace/me")
            assert resp.status_code == 401
            assert "Authentication required" in resp.json()["detail"]

            # 2. Invalid license key -> 401
            resp = await client.get(
                "/workspace/me",
                headers={"Authorization": "Bearer tpg_live_invalidkey1234567890"},
            )
            assert resp.status_code == 401
            assert "Unrecognized commercial license" in resp.json()["detail"]
    finally:
        app.dependency_overrides = orig_overrides


@pytest.mark.asyncio
async def test_strict_paywall_status_gating(test_session):
    """Verifies 402 Payment Required when expired, canceled, or past due, and 403 when suspended."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="customer@saas.com",
        owner_name="Carol SaaS",
        company_name="SaaS Corp",
        subscription_tier="pro",
        duration_days=365,
    )
    await test_session.commit()
    license_key = ws.license_key

    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": f"Bearer {license_key}"}

            # 1. Active license -> 200 OK
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["owner_email"] == "customer@saas.com"
            assert data["subscription_tier"] == "pro"
            assert data["is_license_active"] is True

            # 2. Expired license period -> 402 Payment Required
            ws.valid_until = datetime.now(timezone.utc) - timedelta(days=2)
            await test_session.commit()
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 402
            assert "Commercial License Inactive" in resp.json()["detail"]

            # 3. Renewed license -> 200 OK restored
            await service.renew_subscription(ws.id, extend_days=30)
            await test_session.commit()
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 200

            # 4. Canceled subscription -> 402 Payment Required
            ws.subscription_status = "canceled"
            await test_session.commit()
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 402

            # 5. Past due payment -> 402 Payment Required
            ws.subscription_status = "past_due"
            await test_session.commit()
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 402

            # 6. Suspended account -> 403 Forbidden
            ws.subscription_status = "active"
            ws.is_active = False
            await test_session.commit()
            resp = await client.get("/workspace/me", headers=headers)
            assert resp.status_code == 403
            assert "suspended" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides = orig_overrides


@pytest.mark.asyncio
async def test_commercial_quota_enforcement(test_session):
    """Verifies that exceeding entity limit triggers 402 Payment Required."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="capped@startup.com",
        owner_name="Dave Capped",
        company_name="Capped Co",
        subscription_tier="trial",
        duration_days=14,
    )
    # Set artificial tight limit of 2 entities for test
    ws.entities_limit = 2
    await test_session.commit()
    license_key = ws.license_key

    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"Authorization": f"Bearer {license_key}"}

            # Store entity 1 -> 200
            resp1 = await client.post(
                "/memory/store",
                headers=headers,
                json={
                    "entity_type": "requirement",
                    "name": "Feature One",
                    "description": "First feature",
                },
            )
            assert resp1.status_code == 200

            # Store entity 2 -> 200
            resp2 = await client.post(
                "/memory/store",
                headers=headers,
                json={
                    "entity_type": "requirement",
                    "name": "Feature Two",
                    "description": "Second feature",
                },
            )
            assert resp2.status_code == 200

            # Store entity 3 -> 402 Payment Required (quota exceeded)
            resp3 = await client.post(
                "/memory/store",
                headers=headers,
                json={
                    "entity_type": "requirement",
                    "name": "Feature Three",
                    "description": "Third feature over quota",
                },
            )
            assert resp3.status_code == 402
            assert "Entity limit reached" in resp3.json()["detail"]
    finally:
        app.dependency_overrides = orig_overrides


@pytest.mark.asyncio
async def test_multi_tenant_complete_data_isolation(test_session):
    """Verifies Customer A and Customer B cannot access or leak each other's memories."""
    service = CommercialService(db=test_session)
    ws_a = await service.provision_customer(
        owner_email="tenant_a@corp.com",
        owner_name="Tenant A",
        company_name="Corp A",
        subscription_tier="pro",
    )
    ws_b = await service.provision_customer(
        owner_email="tenant_b@corp.com",
        owner_name="Tenant B",
        company_name="Corp B",
        subscription_tier="pro",
    )
    await test_session.commit()

    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers_a = {"Authorization": f"Bearer {ws_a.license_key}"}
            headers_b = {"Authorization": f"Bearer {ws_b.license_key}"}

            # Tenant A stores secret strategy
            resp_store = await client.post(
                "/memory/store",
                headers=headers_a,
                json={
                    "entity_type": "strategy",
                    "name": "Confidential AI Roadmap",
                    "description": "Tenant A Secret Plan",
                },
            )
            assert resp_store.status_code == 200
            entity_id_a = resp_store.json()["entity_id"]

            # Tenant B searches memory for "Confidential"
            resp_search_b = await client.post(
                "/memory/recall",
                headers=headers_b,
                json={"query": "Confidential AI Roadmap"},
            )
            assert resp_search_b.status_code == 200
            assert len(resp_search_b.json()["entities"]) == 0  # Zero leakage!

            # Tenant B directly attempts to fetch Tenant A's entity by ID
            resp_get_b = await client.get(
                f"/memory/entity/{entity_id_a}",
                headers=headers_b,
            )
            assert resp_get_b.status_code == 404  # Inaccessible and undiscoverable!
    finally:
        app.dependency_overrides = orig_overrides


@pytest.mark.asyncio
async def test_commercial_license_status_endpoint(test_session):
    """Verifies GET /commercial/license/status returns accurate diagnostics."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="diagnostics@test.com",
        owner_name="Diag Tester",
        company_name="Diag Org",
        subscription_tier="pro",
        duration_days=100,
    )
    await test_session.commit()

    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get(
                "/commercial/license/status",
                headers={"Authorization": f"Bearer {ws.license_key}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["owner_email"] == "diagnostics@test.com"
            assert data["subscription_tier"] == "pro"
            assert data["is_valid"] is True
            assert data["days_remaining"] >= 99
            assert data["entities_limit"] == 10000
            assert "tpg_live_" in data["license_key_masked"]
    finally:
        app.dependency_overrides = orig_overrides


@pytest.mark.asyncio
async def test_stripe_webhook_flow(test_session):
    """Verifies Stripe payment webhook automatically renews customer license."""
    service = CommercialService(db=test_session)
    ws = await service.provision_customer(
        owner_email="stripe_user@client.com",
        owner_name="Stripe Client",
        company_name="Stripe Org",
        subscription_tier="pro",
        duration_days=30,
        stripe_customer_id="cus_test_12345",
    )
    await test_session.commit()

    # Expire the user
    ws.valid_until = datetime.now(timezone.utc) - timedelta(days=5)
    ws.subscription_status = "past_due"
    await test_session.commit()

    async def override_db():
        yield test_session

    transport = ASGITransport(app=app)
    orig_overrides = dict(app.dependency_overrides)
    app.dependency_overrides = {get_db: override_db}

    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Simulate Stripe invoice.payment_succeeded event
            payload = {
                "type": "invoice.payment_succeeded",
                "data": {
                    "object": {
                        "customer": "cus_test_12345",
                        "id": "sub_test_67890",
                    }
                },
            }
            resp = await client.post("/commercial/webhook/stripe", json=payload)
            assert resp.status_code == 200
            assert resp.json()["result"]["action"] == "renewed"

            # Check that workspace is now active and renewed
            await test_session.refresh(ws)
            assert ws.subscription_status == "active"
            vu = ws.valid_until if ws.valid_until.tzinfo else ws.valid_until.replace(tzinfo=timezone.utc)
            assert vu > datetime.now(timezone.utc)
    finally:
        app.dependency_overrides = orig_overrides
