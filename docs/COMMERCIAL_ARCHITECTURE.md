# TPG Commercial SaaS & Licensing Architecture

> **Authoritative Specification & Operational Handbook**  
> *Version:* 1.0 Commercial Release  
> *Governing Specifications:* [PRD-0001 §Commercial Model](file:///d:/SkynetORG/TPG/docs/prds/PRD-0001-Master-Product-Charter.md), [PRD-0003 §Identity & Security](file:///d:/SkynetORG/TPG/docs/prds/PRD-0003-RBAC-and-Security-Architecture.md)

---

## 1. Executive Summary

TPG (The Product Guy) operates as a **commercial managed Cloud SaaS platform**. 
While customers experience TPG seamlessly inside their daily workflow (primarily via OpenAI Custom GPT Actions, Slack, Jira, GitHub, and Email connectors), the underlying intelligence engine enforces a **strict commercial subscription paywall**.

Without an active, valid commercial license key:
- Requests from unauthenticated or forged clients are rejected with `401 Unauthorized`.
- Requests from expired, canceled, or past-due subscriptions are blocked with `402 Payment Required`.
- Requests exceeding tier memory quotas or connector limits are blocked with `402 Payment Required`.
- Requests from administratively suspended workspaces are rejected with `403 Forbidden`.

Every valid license key automatically scopes all operations to that specific customer's isolated Personal Workspace, providing a **100% mathematical zero-leakage guarantee**.

---

## 2. System Architecture

```text
               ChatGPT Custom GPT Action / Connected Tools
                                   │
               Authorization: Bearer tpg_live_<32-hex>
                                   │
                                   ▼
        +──────────────────────────────────────────────────────+
        |                 FastAPI Gateway Layer                |
        |              (`backend/app/api/deps.py`)             |
        +──────────────────────────────────────────────────────+
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
        Token Missing?       Status Check?          Quota Check?
       [401 Unauthorized]  [402 Payment Required]  [402 Payment Required]
                           [403 Forbidden]
                                   │ (All Checks Passed)
                                   ▼
        +──────────────────────────────────────────────────────+
        |        Tenant Resolver (`Workspace.license_key`)      |
        |          Resolves Customer's Dedicated UUID          |
        +──────────────────────────────────────────────────────+
                                   │
                                   ▼
        +──────────────────────────────────────────────────────+
        |       Isolated Personal Workspace (Memory Graph)     |
        |       - Strict Tenant Scoping                        |
        |       - Zero Cross-Customer Data Leakage             |
        |       - AES-256 Storage Encryption                   |
        +──────────────────────────────────────────────────────+
                                   │
        +──────────────────────────┴───────────────────────────+
        |                  Specialist Engines                  |
        |    Requirement (PRD-0005)  •  Decision (PRD-0006)    |
        |    Strategy (PRD-0007)     •  PRD Spec (PRD-0008)    |
        |    Engineering (PRD-0009)  •  QA & Release (PRD-0010)|
        |    Analytics (PRD-0011)    •  Customer Intel (PRD-0012)
        +──────────────────────────────────────────────────────+
```

---

## 3. Commercial Tiers & Resource Limits

TPG provides tiered subscription plans tailored to different organizational scales:

| Tier | Target Persona | Entity Limit | Connectors Limit | Trial / Duration | Features Enabled |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`trial`** | New Evaluators | 500 nodes | 2 tools | 14 Days strict cutoff | Full memory, ADR decisions, 5 PRDs |
| **`starter`** | Solo Founders & PMs | 1,500 nodes | 3 tools | Monthly subscription | Complete graph, PRD engine, Sprint summaries |
| **`pro`** (Flagship) | Senior PMs & CPOs | 10,000 nodes | 10 tools | Annual subscription | Decision Tradeoff Engine, Lineage tracing, QA strategies |
| **`enterprise`**| Corporate Product Offices | 100,000+ nodes | 50 tools | Custom Enterprise | Multi-connector streaming, executive digests, dedicated SLA |

---

## 4. Key Management & Entropy

### License Key Format
All commercial license keys are generated using a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) with 128 bits of entropy:

- **Production Keys**: `tpg_live_<32 hex characters>` (e.g., `tpg_live_936d37664e9e3f9cfccedf6dcc333403`)
- **Evaluation / Trial Keys**: `tpg_trial_<32 hex characters>` (e.g., `tpg_trial_7f1a8c9b2e3d4f5a6b7c8d9e0f1a2b3c`)

Keys are unique, indexed in the database, and mapped directly to the customer's `Workspace`.

---

## 5. Paywall Gating & Status Codes

Every route across the entire backend depends on `get_workspace_id`. The gateway enforces the following HTTP error responses:

| HTTP Status | Condition | Gateway Message | Client Action |
| :--- | :--- | :--- | :--- |
| **`401 Unauthorized`** | Missing `Authorization` header | `"Authentication required. Please provide your TPG commercial license key via the Authorization header."` | Prompt customer to enter license key in ChatGPT Action. |
| **`401 Unauthorized`** | Unknown or forged key | `"Invalid API key. Unrecognized commercial license."` | Verify license key validity with support. |
| **`402 Payment Required`** | Expired license date | `"Commercial License Inactive: Commercial license expired on YYYY-MM-DD. Please renew your subscription at https://tpg.skynetorg.com/pricing to continue using TPG."` | TPG presents pricing portal URL to customer. |
| **`402 Payment Required`** | Canceled / Past-due | `"Commercial License Inactive: Commercial subscription has been canceled / payment is past due."` | Customer updates billing method. |
| **`402 Payment Required`** | Quota Limit Exceeded | `"Entity limit reached (10000/10000 entities for pro tier). Please upgrade your commercial subscription to store more knowledge."` | Customer upgrades subscription tier. |
| **`403 Forbidden`** | Suspended Account | `"Access Denied: Workspace account has been suspended. Please contact support@skynetorg.com."` | Contact SkynetOrg support. |

---

## 6. Commercial Management CLI (`scripts/manage_commercial.py`)

SkynetOrg operators use the CLI to provision, inspect, renew, and revoke customer licenses without manual SQL manipulation:

### 1. Provision a New Paying Customer
```powershell
python scripts/manage_commercial.py provision \
  --email "client@acmecorp.com" \
  --name "John Acme" \
  --org "Acme Inc" \
  --tier pro \
  --days 365
```
**Output:**
```text
[+] Provisioning commercial customer workspace for 'client@acmecorp.com'...
============================================================
[SUCCESS] CUSTOMER PROVISIONED SUCCESSFULLY
============================================================
Workspace ID       : 4b6a8af3-e431-433f-973c-45e6761080c3
Customer Name      : John Acme <client@acmecorp.com>
Organization       : Acme Inc
Subscription Tier  : PRO
Status             : ACTIVE
Valid Until        : 2027-10-01 12:23:50 UTC
Entities Limit     : 10,000
Connectors Limit   : 10
------------------------------------------------------------
COMMERCIAL KEY     : tpg_live_936d37664e9e3f9cfccedf6dcc333403
------------------------------------------------------------
```

### 2. List All Customer Licenses
```powershell
python scripts/manage_commercial.py list
```

### 3. Inspect Customer Diagnostics & Quota
```powershell
python scripts/manage_commercial.py inspect --email "client@acmecorp.com"
```

### 4. Renew Subscription
```powershell
python scripts/manage_commercial.py renew --email "client@acmecorp.com" --days 365
```

### 5. Revoke or Suspend Access
```powershell
python scripts/manage_commercial.py revoke --email "client@acmecorp.com" --reason canceled
```

---

## 7. Commercial REST Endpoints (`/commercial`)

| Method | Endpoint | Protection | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/commercial/licenses/provision` | Master Admin Key | Create workspace, generate key, set tier limits |
| `GET` | `/commercial/license/status` | Customer License Key | Check days remaining, usage counts, and validity |
| `POST` | `/commercial/licenses/{id}/renew` | Master Admin Key | Extend expiration date and restore active state |
| `POST` | `/commercial/licenses/{id}/revoke` | Master Admin Key | Suspend or cancel customer license |
| `POST` | `/commercial/webhook/stripe` | Stripe Signature | Handle automated recurring billing events |

---

## 8. Stripe Webhook Lifecycle

The webhook handler at `/commercial/webhook/stripe` processes automated Stripe billing events:

1. **`invoice.payment_succeeded`**:
   - Matches `customer.id` with `Workspace.stripe_customer_id`.
   - Extends `valid_until` by 30 days.
   - Sets `subscription_status = "active"`.
2. **`customer.subscription.deleted`**:
   - Sets `subscription_status = "canceled"`.
   - Future API requests are blocked with `402 Payment Required`.
3. **`customer.subscription.updated`**:
   - Updates `past_due` or `active` status immediately.

---

## 9. Customer Onboarding Guide for ChatGPT

When a customer subscribes:
1. They receive their unique license key: `tpg_live_<32-hex>`.
2. They open the **TPG Custom GPT** on OpenAI.
3. In Custom GPT configuration or first action prompt, click **Authenticate**.
4. Select **API Key** with Auth Type: **Bearer**.
5. Paste their key: `tpg_live_...`.
6. TPG immediately authenticates their dedicated Personal Workspace. All strategies, decisions, PRDs, and connected tools are recorded exclusively in their private Knowledge Graph.
