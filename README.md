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

---

## 🏛️ Architecture Overview

```text
               +-------------------------------------------------+
               |              ChatGPT (Primary UI)               |
               +-------------------------------------------------+
                                       │
                                       ▼
                     +───────────────────────────────────+
                     |  TPG Constitutional Prompt System |
                     |             (PRD-0009)            |
                     +───────────────────────────────────+
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
         +──────────────────────+              +──────────────────────+
         | Personal Workspace   |              | Org Workspace (RBAC) |
         | (Private isolation)  |              | (Multi-tenant graph) |
         +──────────────────────+              +──────────────────────+
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                     +───────────────────────────────────+
                     |    Requirement & Decision Engine   |
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
