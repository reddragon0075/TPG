# TPG GENESIS — PRD 0002

## Organizational Memory, Knowledge Graph & Workspace Architecture

**Product:** TPG (The Product Guy)  
**Company:** SkynetOrg  
**Document ID:** TPG-PRD-0002  
**Version:** Genesis 1.0  
**Classification:** Internal / Confidential  
**Owner:** SkynetOrg Architecture Team  
**Depends On:** PRD-0001 (Master Product Charter)  
**Status:** Engineering Specification  

---

# Document Objective

This document defines the **foundational data architecture** of TPG.

Everything TPG knows, remembers, retrieves and reasons upon originates from this specification.

This is **not** a database schema alone.

It defines:

* Organizational Memory
* Workspace isolation
* Knowledge Graph
* Entity relationships
* Versioning
* Retrieval rules
* Audit history
* Memory lifecycle

This document is considered the **constitution of memory**.

---

# 1. Design Philosophy

## Core Principle

> **TPG remembers knowledge, not conversations.**

Conversations are temporary.

Knowledge is permanent.

Example:

**Conversation**

> Sarah: We'll send the hotel policy on Monday.

Conversation disappears.

**Knowledge created**

* Commitment
* Owner
* Due date
* Client
* Initiative

Only structured knowledge enters Organizational Memory.

---

# 2. Workspace Architecture

## 2.1 Overview

TPG V1 supports **one Personal Workspace** and **one Corporate Workspace** per user.

Every authenticated user has one global identity.

Product knowledge always belongs to one workspace.

### Architecture

```text
Skynet Identity
      │
      ▼
+----------------------+
| User Authentication  |
+----------------------+
      │
      ▼
+----------------------+
| Workspace Resolver   |
+----------------------+
      │
 ┌────┴─────┐
 │          │
 ▼          ▼
Personal   Corporate
Workspace  Workspace
```

---

## 2.2 Workspace Types

### Personal Workspace

Purpose:

Private Product Office.

Contains:

* Startup ideas
* Personal PRDs
* Career planning
* Interview preparation
* Learning notes

Owner: Individual

Visibility: Private only

---

### Corporate Workspace

Purpose:

Shared Product Office.

Contains:

* Clients
* Stakeholders
* PRDs
* Initiatives
* Decisions
* Jira intelligence
* Slack intelligence
* Product KPIs

Owner: Organization

Visibility: Role-based

---

## 2.3 Workspace Limits (V1)

| Resource            | Limit |
| ------------------- | ----: |
| Personal Workspace  |     1 |
| Corporate Workspace |     1 |
| Active Workspace    |     1 |
| Workspace Owner     |     1 |

Multi-company membership is intentionally excluded from Version 1.

Future versions may extend this without changing entity IDs.

---

## 2.4 Active Workspace Resolution

TPG automatically determines context.

### Scenario A

User belongs only to taSki.

```text
User: Abhijith

Workspace:
taSki

Active → taSki
```

No selector shown.

---

### Scenario B

User has Personal + taSki.

```text
Available

Personal

taSki

Last Active → taSki
```

TPG opens taSki automatically.

---

### Scenario C

Switching

User says:

> Switch to Personal

Expected:

```text
Workspace changed.

Current:
Personal Workspace
```

No data migration occurs.

---

# 3. Global Object Standard

Every entity inherits the following structure.

## Base Object

| Field        | Type      | Required |
| ------------ | --------- | -------- |
| id           | UUID v7   | Yes      |
| workspace_id | UUID      | Yes      |
| entity_type  | Enum      | Yes      |
| created_at   | UTC       | Yes      |
| updated_at   | UTC       | Yes      |
| created_by   | User UUID | Yes      |
| version      | Integer   | Yes      |
| status       | Enum      | Yes      |
| visibility   | Enum      | Yes      |
| archived     | Boolean   | Yes      |

---

## 3.1 UUID Convention

Example

```text
cmp_******
cli_******
per_******
ini_******
req_******
prd_******
dec_******
kpi_******
com_******
```

Prefix indicates entity type.

Chronological UUID v7 ensures ordered retrieval.

---

# 4. Visibility Model

## Visibility Levels

| Level        | Description        |
| ------------ | ------------------ |
| PRIVATE      | Only creator       |
| TEAM         | Product team       |
| DEPARTMENT   | Department members |
| EXECUTIVE    | Leadership only    |
| ORGANIZATION | Entire company     |

Visibility is evaluated **after** workspace validation.

---

# 5. Core Entities

## 5.1 Company

Represents one organization.

### Fields

| Field             | Type   |
| ----------------- | ------ |
| company_id        | UUID   |
| company_name      | String |
| industry          | Enum   |
| business_model    | String |
| headquarters      | String |
| north_star_metric | String |
| timezone          | String |

Example

```yaml
company_name: taSki
industry: Corporate Mobility
north_star_metric: Successful Trips
```

---

## 5.2 Person

Represents employees and stakeholders.

### Fields

| Field              | Type        |
| ------------------ | ----------- |
| person_id          | UUID        |
| full_name          | String      |
| department         | String      |
| designation        | String      |
| hierarchy_level    | Integer     |
| reports_to         | Person UUID |
| decision_authority | Enum        |
| active             | Boolean     |

### Decision Authority

* NONE
* RECOMMENDER
* APPROVER
* EXECUTIVE

Sensitive personal information is prohibited.

---

## 5.3 Client

Represents customer organizations.

### Fields

| Field           | Type        |
| --------------- | ----------- |
| client_id       | UUID        |
| company_name    | String      |
| account_owner   | Person UUID |
| contract_status | Enum        |
| products        | Array       |
| renewal_date    | Date        |
| health_score    | Integer     |
| strategic_tier  | Enum        |

Strategic Tier:

* Tier 1
* Tier 2
* Tier 3

---

## 5.4 Initiative

The primary object of TPG.

Everything revolves around Initiatives.

### Fields

| Field             | Type        |
| ----------------- | ----------- |
| initiative_id     | UUID        |
| title             | String      |
| objective         | Text        |
| problem_statement | Text        |
| owner             | Person UUID |
| priority          | Enum        |
| status            | Enum        |
| linked_clients    | Array       |
| linked_prds       | Array       |
| linked_kpis       | Array       |

### Status

* Discovery
* Validation
* Planned
* Development
* QA
* Released
* Archived

---

## 5.5 Requirement

Validated customer needs.

### Fields

| Field           | Type   |
| --------------- | ------ |
| requirement_id  | UUID   |
| initiative      | UUID   |
| persona         | String |
| pain_point      | Text   |
| desired_outcome | Text   |
| constraints     | Array  |
| confidence      | Float  |
| source          | Enum   |

Sources:

* ChatGPT
* Slack
* Gmail
* Meeting
* Support Ticket

---

## 5.6 PRD

Living specification.

### Fields

| Field          | Type    |
| -------------- | ------- |
| prd_id         | UUID    |
| initiative     | UUID    |
| version        | Integer |
| author         | UUID    |
| status         | Enum    |
| approval_state | Enum    |

Approval States:

* Draft
* Review
* Approved
* Superseded

PRDs are immutable.

New versions are created instead of editing.

---

## 5.7 Decision

Executive record.

### Fields

| Field        | Type      |
| ------------ | --------- |
| decision_id  | UUID      |
| initiative   | UUID      |
| outcome      | Enum      |
| rationale    | Text      |
| evidence     | Array     |
| alternatives | Array     |
| approver     | UUID      |
| approved_at  | Timestamp |

Outcomes:

* Approved
* Rejected
* Deferred
* Research Required

---

## 5.8 KPI

Success measurement.

### Fields

| Field    | Type   |
| -------- | ------ |
| kpi_id   | UUID   |
| name     | String |
| baseline | Number |
| target   | Number |
| current  | Number |
| unit     | String |

Example

```yaml
name: Feature Adoption
baseline: 18
target: 40
current: 26
unit: "%"
```

---

## 5.9 Commitment

Natural-language promises.

### Fields

| Field            | Type |
| ---------------- | ---- |
| commitment_id    | UUID |
| owner            | UUID |
| deliverable      | Text |
| due_date         | Date |
| status           | Enum |
| reminder_state   | Enum |
| source_reference | UUID |

Lifecycle:

* Upcoming
* Today
* Overdue
* Completed

---

# 6. Knowledge Graph

TPG uses relationship-based retrieval.

## Relationship Matrix

| From        | To         | Relation  |
| ----------- | ---------- | --------- |
| Client      | Initiative | Requested |
| Person      | Initiative | Owns      |
| Requirement | Initiative | Defines   |
| Initiative  | PRD        | Specifies |
| Initiative  | KPI        | Measures  |
| Decision    | Initiative | Governs   |
| Commitment  | Person     | Assigned  |

## Graph Rules

Every Initiative must have:

* One owner
* One objective
* One status

Every Decision must reference exactly one Initiative.

Every Requirement belongs to one Initiative.

Orphan entities are invalid.

---

# 7. Versioning Strategy

Nothing is overwritten.

Example

```text
PRD v1

↓

PRD v2

↓

PRD v3

↓

PRD v4 (Current)
```

Rules:

* Previous versions remain readable.
* Current version marked by metadata.
* Audit trail preserved forever.

---

# 8. Audit Architecture

Every modification becomes an immutable event.

## Event Types

| Event    | Description        |
| -------- | ------------------ |
| CREATED  | Object created     |
| UPDATED  | Metadata changed   |
| LINKED   | Relationship added |
| APPROVED | Executive approval |
| ARCHIVED | Soft archive       |
| RESTORED | Recovery           |

Example

```text
09:10 Initiative Created

09:42 Requirement Linked

11:20 PRD Approved

14:15 KPI Updated
```

Audit logs cannot be deleted.

---

# 9. Retrieval Engine

TPG does not perform keyword search.

It performs graph retrieval.

## Stage 1 — Authorization

Validate:

* User
* Workspace
* Role

Failure immediately terminates retrieval.

---

## Stage 2 — Intent Classification

Example

User:

> Why was Vendor Wallet approved?

Intent:

Decision Retrieval

---

## Stage 3 — Graph Traversal

```text
Initiative

↓

Decision

↓

Evidence

↓

Client

↓

KPI
```

---

## Stage 4 — Response Assembly

Final response includes:

* Direct answer
* Supporting evidence
* Related initiatives
* Confidence
* Decision rationale

---

# 10. Memory Lifecycle

## Capture

Sources:

* ChatGPT
* Slack
* Gmail
* Jira
* Meetings

---

## Extraction

TPG identifies:

* Requirements
* Decisions
* Commitments
* Stakeholders
* KPIs

Each receives a confidence score.

---

## Validation

Objects remain in Draft until confirmed by an authorized user.

Example:

Meeting creates five Requirements.

Senior PM approves.

Only then do they become Active Memory.

---

## Archive

Completed initiatives become archived.

Archived entities remain searchable.

Deletion is prohibited.

---

# 11. Duplicate Resolution

Problem:

Three employees independently create:

* Vendor Wallet
* Wallet Feature
* Driver Wallet

TPG performs semantic similarity.

If confidence exceeds threshold:

Suggest merge.

Never merge automatically.

Human approval required.

---

# 12. Integrity Constraints

### IC-001

Every object requires `workspace_id`.

### IC-002

Every Initiative requires an owner.

### IC-003

Every Decision requires an approver.

### IC-004

Every PRD requires one Initiative.

### IC-005

Every Requirement must originate from Discovery.

### IC-006

Cross-workspace relationships are forbidden.

---

# 13. Failure Scenarios

## Unauthorized Access

Junior PM asks:

> Show IndiGo contract value.

Expected:

Access denied.

Commercial values remain hidden.

---

## Duplicate Initiative

Existing:

Vendor Wallet

User creates:

Corporate Wallet

Expected:

Suggest merge.

Do not duplicate.

---

## Workspace Isolation

User switches to Personal.

Expected:

Corporate Slack

Corporate Jira

Corporate PRDs

Become inaccessible immediately.

---

# 14. Engineering Acceptance Criteria

| ID     | Requirement                      |
| ------ | -------------------------------- |
| FR-021 | One Personal Workspace           |
| FR-022 | One Corporate Workspace          |
| FR-023 | Automatic workspace resolution   |
| FR-024 | Manual workspace switching       |
| FR-025 | UUID v7 entities                 |
| FR-026 | Immutable version history        |
| FR-027 | Graph-based retrieval            |
| FR-028 | Zero cross-workspace leakage     |
| FR-029 | Soft archive only                |
| FR-030 | Audit log for every modification |

---

# 15. Design Freeze

This document defines the canonical memory architecture of TPG.

No module—including Discovery, PRD Generation, Decision Engine, Client Intelligence, Jira Intelligence or Board Reporting—may introduce entities outside this schema without a formal PRD revision.

**Next Document:** PRD-0003 — Role-Based Access Control & Enterprise Security.
