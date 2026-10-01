# TPG (The Product Guy)

> **The Invisible Autonomous Product Office for Modern Organizations**  
> *Embedded digital Chief Product Officer inside the tools organizations already use.*

---

## 🎯 Master Product Charter

TPG is governed by [PRD-0001: Master Product Charter](file:///d:/SkynetORG/TPG/docs/prds/PRD-0001-Master-Product-Charter.md).

### Core Principles
- **P1 — Invisible First**: Users never change their workflow. Operates through ChatGPT as primary interface and Slack, Gmail, Jira, GitHub, Calendar as execution channels.
- **P2 — Organization Owns Memory**: Strict separation between Personal Workspaces and Organization Workspaces. Zero data leakage.
- **P3 — Evidence Before Opinion**: Every recommendation is backed by customer interviews, revenue metrics, Jira trends, or analytics.
- **P4 — Explainability**: Black-box reasoning is prohibited. Every recommendation includes why, evidence, risks, alternatives, and confidence.

---

## 📋 Design Freeze Roadmap (Companion Specifications)

As mandated by PRD-0001, engineering implementation begins once companion specifications are authored and approved. The scope expanded from the original 9 PRDs to 12 as the architecture crystallized in PRD-0006:

| ID | Specification | Status | Target Document |
| :--- | :--- | :--- | :--- |
| **PRD-0001** | **Master Product Charter** | ✅ Approved | [`docs/prds/PRD-0001-Master-Product-Charter.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0001-Master-Product-Charter.md) |
| **PRD-0002** | **Organizational Memory Schema** | ✅ Approved | [`docs/prds/PRD-0002-Organizational-Memory-Schema.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0002-Organizational-Memory-Schema.md) |
| **PRD-0003** | **Identity, Personal Workspace & Privacy (V1)** | ✅ Approved | [`docs/prds/PRD-0003-RBAC-and-Security-Architecture.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0003-RBAC-and-Security-Architecture.md) |
| **PRD-0004** | **Connector Intelligence Framework** | ✅ Approved | [`docs/prds/PRD-0004-Connector-Framework.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0004-Connector-Framework.md) |
| **PRD-0005** | **Requirement Intelligence Engine** | ✅ Approved | [`docs/prds/PRD-0005-Requirement-Intelligence-Engine.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0005-Requirement-Intelligence-Engine.md) |
| **PRD-0006** | **Product Decision Engine** | ✅ Approved | [`docs/prds/PRD-0006-Decision-Engine.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0006-Decision-Engine.md) |
| **PRD-0007** | **Product Strategy / Roadmap Intelligence** | ✅ Approved | [`docs/prds/PRD-0007-Product-Strategy-Roadmap.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0007-Product-Strategy-Roadmap.md) |
| **PRD-0008** | **PRD & Product Specification Engine** | ✅ Approved | [`docs/prds/PRD-0008-PRD-Specification-Engine.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0008-PRD-Specification-Engine.md) |
| **PRD-0009** | **Execution & Engineering Intelligence** | ✅ Approved | [`docs/prds/PRD-0009-Execution-Engineering-Intelligence.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0009-Execution-Engineering-Intelligence.md) |
| **PRD-0010** | **Quality / QA / Release Intelligence** | ✅ Approved | [`docs/prds/PRD-0010-QA-Release-Intelligence.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0010-QA-Release-Intelligence.md) |
| **PRD-0011** | **Product Analytics & Outcome Intelligence** | ✅ Approved | [`docs/prds/PRD-0011-Analytics-Outcome-Intelligence.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0011-Analytics-Outcome-Intelligence.md) |
| **PRD-0012** | **Autonomous Product Office Orchestration** | ✅ Approved | [`docs/prds/PRD-0012-Customer-Intelligence.md`](file:///d:/SkynetORG/TPG/docs/prds/PRD-0012-Customer-Intelligence.md) |
| **Commercial** | **Commercial SaaS & Paywall Architecture** | ✅ Active | [`docs/COMMERCIAL_ARCHITECTURE.md`](file:///d:/SkynetORG/TPG/docs/COMMERCIAL_ARCHITECTURE.md) |

---

## 🏛️ Architecture Overview

```text
               +-------------------------------------------------+
               |              ChatGPT (Primary UI)               |
               +-------------------------------------------------+
                                       │ Authorization: Bearer tpg_live_...
                                       ▼
                     +───────────────────────────────────+
                     |    Commercial Paywall Gateway     |
                     |         (HTTP 401 / 402 / 403)    |
                     +───────────────────────────────────+
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
          +──────────────────────+            +──────────────────────+
          | Personal Workspace   |            | Org Workspace (RBAC) |
          | (Private isolation)  |            | (Multi-tenant graph) |
          +──────────────────────+            +──────────────────────+
                     │                                   │
                     └─────────────────┬─────────────────┘
                                       ▼
                     +───────────────────────────────────+
                     |    Requirement & Decision Engine  |
                     |         (PRD-0005 / PRD-0006)     |
                     +───────────────────────────────────+
                                       │
                                       ▼
                     +───────────────────────────────────+
                     |    Organizational Memory Graph    |
                     |             (PRD-0002)            |
                     +───────────────────────────────────+
                                       │
                                       ▼
                     +───────────────────────────────────+
                     |   Connector & Sync Framework      |
                     |             (PRD-0004)            |
                     +-----------------------------------+
                       │        │        │        │      │
                       ▼        ▼        ▼        ▼      ▼
                     Slack    Gmail    Jira    GitHub  Calendar
```

---

## 💳 Commercial SaaS Platform & Strict Paywall

TPG operates as a **commercial, multi-tenant Cloud SaaS platform**. Every customer subscribes to receive their dedicated Personal Workspace, authenticated via a cryptographically secure commercial license key (`tpg_live_<32-hex>`).

Authoritative specification: [`docs/COMMERCIAL_ARCHITECTURE.md`](file:///d:/SkynetORG/TPG/docs/COMMERCIAL_ARCHITECTURE.md)

### Commercial Tiers & Quotas

| Tier | Entity Quota | Connector Quota | Billing Model | Highlights |
| :--- | :--- | :--- | :--- | :--- |
| **Trial** | 500 nodes | 2 tools | 14-day strict trial | Free evaluation, ADR decisions, 5 PRDs |
| **Starter** | 1,500 nodes | 3 tools | Monthly subscription | Solo founders, full graph, PRD engine |
| **Pro** (Flagship) | 10,000 nodes | 10 tools | Annual subscription | Decision Tradeoff Engine, Lineage, QA |
| **Enterprise** | 100,000+ nodes | 50 tools | Custom Enterprise | High-volume streaming, multi-org, SLA |

### Strict Paywall Gating

Every request passing through `app.api.deps:get_workspace_id` is strictly validated:
- **`401 Unauthorized`**: Missing, invalid, or forged license key.
- **`402 Payment Required`**: Expired license, canceled/past-due subscription, or exceeded tier quota.
- **`403 Forbidden`**: Administratively suspended workspace account.
- **`200 OK`**: Valid license key resolves to the customer's isolated workspace (zero cross-tenant data leakage).

---

## 🛠️ Commercial License Management CLI

SkynetOrg operators use `scripts/manage_commercial.py` to provision, inspect, renew, and revoke customer accounts:

```powershell
# 1. Provision a paying customer with an annual Pro license
python scripts/manage_commercial.py provision \
  --email "founder@acmecorp.com" \
  --name "Jane Founder" \
  --org "Acme Corp" \
  --tier pro \
  --days 365

# 2. List all customer workspaces & live subscription states
python scripts/manage_commercial.py list

# 3. Inspect quota usage and license diagnostics
python scripts/manage_commercial.py inspect --email "founder@acmecorp.com"

# 4. Renew or extend a subscription
python scripts/manage_commercial.py renew --email "founder@acmecorp.com" --days 365

# 5. Revoke or suspend a license
python scripts/manage_commercial.py revoke --email "founder@acmecorp.com" --reason canceled
```

---

## 🧪 Testing & Verification

The automated test suite covers all intelligence engines, APIs, graph traversal, and commercial paywall gating:

```powershell
# Run the complete test suite (83 tests)
python -m pytest

# Run commercial paywall & licensing tests only
python -m pytest tests/test_commercial.py -v
```

---

## 🚀 Running Locally

```powershell
# Run the FastAPI server locally
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
