"""
TPG Commercial License Manager CLI

Admin utility for SkynetOrg to issue, inspect, renew, and revoke customer
commercial licenses and Personal Workspaces.

Usage:
    python scripts/manage_commercial.py provision --email client@company.com --name "Jane Doe" --org "Acme Corp" --tier pro --days 365
    python scripts/manage_commercial.py list
    python scripts/manage_commercial.py inspect --email client@company.com
    python scripts/manage_commercial.py renew --email client@company.com --days 365
    python scripts/manage_commercial.py revoke --email client@company.com --reason suspended
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Ensure stdout handles UTF-8 safely
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path so backend imports work cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.database import async_session_factory, ensure_db_schema
from app.models.workspace import Workspace
from app.services.commercial_service import CommercialService, TIER_LIMITS


async def cmd_provision(args):
    await ensure_db_schema()
    async with async_session_factory() as session:
        service = CommercialService(db=session)
        print(f"\n[+] Provisioning commercial customer workspace for '{args.email}'...")
        ws = await service.provision_customer(
            owner_email=args.email,
            owner_name=args.name,
            company_name=args.org,
            subscription_tier=args.tier,
            duration_days=args.days,
        )
        await session.commit()

        print("=" * 60)
        print("[SUCCESS] CUSTOMER PROVISIONED SUCCESSFULLY")
        print("=" * 60)
        print(f"Workspace ID       : {ws.id}")
        print(f"Customer Name      : {ws.owner_name} <{ws.owner_email}>")
        print(f"Organization       : {ws.name}")
        print(f"Subscription Tier  : {ws.subscription_tier.upper()}")
        print(f"Status             : {ws.subscription_status.upper()}")
        print(f"Valid Until        : {ws.valid_until.strftime('%Y-%m-%d %H:%M:%S UTC') if ws.valid_until else 'Never'}")
        print(f"Entities Limit     : {ws.entities_limit:,}")
        print(f"Connectors Limit   : {ws.connectors_limit}")
        print("-" * 60)
        print(f"COMMERCIAL KEY     : {ws.license_key}")
        print("-" * 60)
        print("\nCUSTOMER ONBOARDING INSTRUCTIONS FOR CHATGPT:")
        print("1. In OpenAI Custom GPT settings, select 'Configure Actions'.")
        print("2. Set Authentication to 'API Key' -> 'Bearer'.")
        print(f"3. Paste the License Key: {ws.license_key}")
        print("4. Done! Every conversation is now strictly gated and saved into their private workspace.\n")


async def cmd_list(args):
    await ensure_db_schema()
    async with async_session_factory() as session:
        stmt = select(Workspace).order_by(Workspace.created_at.desc())
        res = await session.execute(stmt)
        workspaces = res.scalars().all()

        print(f"\nACTIVE CUSTOMER WORKSPACES ({len(workspaces)} total):\n")
        header = f"{'EMAIL':<30} {'TIER':<10} {'STATUS':<12} {'VALID UNTIL':<14} {'LICENSE KEY':<28}"
        print(header)
        print("-" * len(header))

        for ws in workspaces:
            is_valid, _ = ws.is_license_valid()
            status_indicator = "[OK]" if is_valid else "[ERR]"
            valid_str = ws.valid_until.strftime("%Y-%m-%d") if ws.valid_until else "Perpetual"
            key_preview = ws.license_key[:22] + "..." if ws.license_key else "None"
            print(
                f"{ws.owner_email:<30} "
                f"{ws.subscription_tier:<10} "
                f"{status_indicator} {ws.subscription_status:<6} "
                f"{valid_str:<14} "
                f"{key_preview:<28}"
            )
        print()


async def cmd_inspect(args):
    await ensure_db_schema()
    async with async_session_factory() as session:
        service = CommercialService(db=session)
        stmt = select(Workspace).where(
            (Workspace.owner_email == args.email) | (Workspace.license_key == args.email)
        )
        res = await session.execute(stmt)
        ws = res.scalar_one_or_none()
        if not ws:
            print(f"[ERROR] No workspace found for identifier '{args.email}'.")
            return

        status = await service.get_license_status(ws.id)
        print("\nCOMMERCIAL LICENSE DIAGNOSTICS:")
        print("=" * 50)
        for k, v in status.items():
            print(f"  {k:<22}: {v}")
        print("=" * 50 + "\n")


async def cmd_renew(args):
    await ensure_db_schema()
    async with async_session_factory() as session:
        service = CommercialService(db=session)
        stmt = select(Workspace).where(
            (Workspace.owner_email == args.email) | (Workspace.license_key == args.email)
        )
        res = await session.execute(stmt)
        ws = res.scalar_one_or_none()
        if not ws:
            print(f"[ERROR] No workspace found for identifier '{args.email}'.")
            return

        renewed = await service.renew_subscription(ws.id, extend_days=args.days, new_tier=args.tier)
        await session.commit()

        print(f"\n[OK] Renewed subscription for '{renewed.owner_email}' for +{args.days} days.")
        print(f"     New Expiration: {renewed.valid_until.strftime('%Y-%m-%d')}")
        print(f"     Status        : {renewed.subscription_status}")
        print(f"     Tier          : {renewed.subscription_tier.upper()}\n")


async def cmd_revoke(args):
    await ensure_db_schema()
    async with async_session_factory() as session:
        service = CommercialService(db=session)
        stmt = select(Workspace).where(
            (Workspace.owner_email == args.email) | (Workspace.license_key == args.email)
        )
        res = await session.execute(stmt)
        ws = res.scalar_one_or_none()
        if not ws:
            print(f"[ERROR] No workspace found for identifier '{args.email}'.")
            return

        revoked = await service.revoke_license(ws.id, reason=args.reason)
        await session.commit()
        print(f"\n[ALERT] Revoked / suspended license for '{revoked.owner_email}'. Status: {args.reason}\n")


def main():
    parser = argparse.ArgumentParser(description="TPG Commercial License Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # provision
    p_prov = subparsers.add_parser("provision", help="Provision new commercial customer")
    p_prov.add_argument("--email", required=True, help="Customer email")
    p_prov.add_argument("--name", required=True, help="Customer name")
    p_prov.add_argument("--org", default="Product Office", help="Organization name")
    p_prov.add_argument("--tier", default="pro", choices=list(TIER_LIMITS.keys()), help="Subscription tier")
    p_prov.add_argument("--days", type=int, default=365, help="Validity duration in days")

    # list
    subparsers.add_parser("list", help="List all customer workspaces and license statuses")

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect a customer license")
    p_insp.add_argument("--email", required=True, help="Customer email or license key")

    # renew
    p_ren = subparsers.add_parser("renew", help="Renew or extend customer license")
    p_ren.add_argument("--email", required=True, help="Customer email or license key")
    p_ren.add_argument("--days", type=int, default=365, help="Days to extend")
    p_ren.add_argument("--tier", default=None, choices=list(TIER_LIMITS.keys()), help="Optional tier change")

    # revoke
    p_rev = subparsers.add_parser("revoke", help="Revoke or suspend customer license")
    p_rev.add_argument("--email", required=True, help="Customer email or license key")
    p_rev.add_argument("--reason", default="canceled", choices=["canceled", "suspended", "expired"], help="Reason")

    args = parser.parse_args()

    if args.command == "provision":
        asyncio.run(cmd_provision(args))
    elif args.command == "list":
        asyncio.run(cmd_list(args))
    elif args.command == "inspect":
        asyncio.run(cmd_inspect(args))
    elif args.command == "renew":
        asyncio.run(cmd_renew(args))
    elif args.command == "revoke":
        asyncio.run(cmd_revoke(args))


if __name__ == "__main__":
    main()
