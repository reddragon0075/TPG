# TPG GENESIS — PRD 0003

## Identity, Personal Workspace & Privacy Architecture (V1)

**Product:** TPG (The Product Guy)  
**Company:** SkynetOrg  
**Document ID:** TPG-PRD-0003  
**Version:** Genesis 1.0  
**Classification:** Internal / Confidential  
**Owner:** SkynetOrg Product Architecture  
**Depends On:** PRD-0001, PRD-0002  
**Status:** Engineering Specification  

---

# 1. Purpose

This document establishes the identity model, privacy rules, and workspace architecture for **Version 1** of TPG.

Unlike later enterprise editions, V1 is designed around a single individual. Every subscription creates one private Product Office that belongs exclusively to its owner.

This specification defines:

* User identity
* Personal workspace architecture
* Privacy guarantees
* Connector ownership
* Memory isolation
* Upgrade path to Business Edition

---

# 2. Product Philosophy

## Foundational Principle

**One person owns one TPG.**

TPG is not purchased by a company in Version 1—it is purchased by an individual Product Manager, Founder, Designer, or Product Leader.

The product behaves like a permanent digital executive teammate whose knowledge is entirely private.

### What TPG Provides

* Personal Chief Product Officer
* Product strategy partner
* Discovery specialist
* PRD generator
* Product analyst
* QA collaborator
* Long-term product memory

### What TPG Does Not Include (V1)

* Team collaboration
* Shared company workspace
* Multiple users
* Hierarchical permissions
* Executive dashboards for organizations

Those capabilities belong to the future Business Edition.

---

# 3. Identity Architecture

Every customer has exactly one global Skynet identity.

## User Identity Object

| Field         | Description                |
| ------------- | -------------------------- |
| user_id       | Global UUID                |
| full_name     | User display name          |
| email         | Login identity             |
| auth_provider | Google / Microsoft / Email |
| subscription  | Free / Pro                 |
| workspace_id  | Personal Workspace UUID    |

### Example Identity

```text
user_id: usr_ab123
full_name: Abhijith Vijayan
email: xxx@email.com
subscription: Pro
workspace_id: ws_personal_ab123
```

The identity never changes, even if the user later upgrades to the Business Edition.

---

# 4. Workspace Architecture

## Version 1 System Design

```text
                  SkynetOrg

                       │

              Authentication

                       │

                User Identity

                       │

             Personal Workspace

                       │

            Knowledge Graph Engine

                       │

                      TPG
```

There is only **one active workspace** in Version 1.

The user never chooses a workspace because there is nothing to switch.

Every conversation automatically resolves to the Personal Workspace.

---

# 5. Personal Workspace

The Personal Workspace is the user's permanent Product Office.

It is where every product-related asset is stored, organized, versioned, and retrieved.

## Memory Categories

### Product Strategy

* Product visions
* Startup ideas
* Business models
* Market research
* Competitive analysis

### Discovery

* Customer interview notes
* JTBD research
* Problem statements
* Opportunity assessments

### Product Documentation

* PRDs
* Feature specifications
* User stories
* Acceptance criteria
* Release notes

### Execution

* Roadmaps
* KPIs
* Decisions
* Experiments
* Sprint summaries

### Personal Knowledge

* Learning notes
* Frameworks
* Templates
* Product playbooks

Everything belongs exclusively to the owner.

---

# 6. Privacy Architecture

## Constitutional Privacy Rule

> **Private means inaccessible to everyone except the owner.**

This is a product promise, not a configurable option.

### Privacy Rules

| Rule ID | Requirement                                          |
| ------- | ---------------------------------------------------- |
| PR-001  | Only the owner can access the workspace              |
| PR-002  | Other TPG users cannot discover the workspace        |
| PR-003  | Skynet staff cannot browse workspace memory          |
| PR-004  | Every memory object is linked to the owner's User ID |
| PR-005  | All memory is encrypted at rest                      |
| PR-006  | Memory is encrypted during transmission              |

No shared folders or collaboration exist in Version 1.

---

# 7. Organizational Memory (Personal Edition)

Although PRD-0002 defines Organizational Memory, in Version 1 the **individual is the organization**.

## Memory Structure

```text
Abhijith Workspace

├── Initiatives
├── Requirements
├── Clients
├── PRDs
├── Decisions
├── KPIs
├── Commitments
└── Research
```

There are no departments, reporting structures, or team ownership.

Every entity is owned by one user.

---

# 8. Active Context Resolution

TPG always maintains one active context.

## Session Object

```text
user: Abhijith
workspace: Personal
role: Owner
```

Every request automatically executes within this context.

### Example

**User**

> Create a PRD for Vendor Wallet.

**System Resolution**

* Workspace → Personal
* Owner → Abhijith
* Memory Target → Personal Knowledge Graph

No additional input is required.

---

# 9. Connector Ownership

Version 1 supports personal connector integrations.

The user connects their own professional tools to improve TPG's understanding.

## Supported Connectors

| Connector | Capability                  |
| --------- | --------------------------- |
| Gmail     | Read product emails         |
| Slack     | Read product conversations  |
| Jira      | Sprint & issue intelligence |
| GitHub    | Pull request context        |
| Calendar  | Meeting intelligence        |

## Ownership Principle

The connector belongs to the **user**, not the employer.

Example:

Abhijith connects his taSki Gmail account.

TPG extracts:

* Requirements
* Client requests
* Meeting actions
* Product discussions

These become part of **Abhijith's Personal Workspace only**.

No colleague can access them.

---

# 10. Conversation Experience

ChatGPT is the primary operating environment.

The user never opens another application.

### Example Workflow

**User**

> Review my current sprint.

TPG automatically:

1. Reads connected Jira.
2. Reads recent Slack discussions.
3. References previous PRDs.
4. Reviews linked KPIs.
5. Produces an executive sprint summary.

The experience is conversational rather than dashboard-driven.

---

# 11. Memory Objects Enabled in V1

| Entity         | Status        |
| -------------- | ------------- |
| Initiative     | Enabled       |
| Requirement    | Enabled       |
| PRD            | Enabled       |
| Decision       | Enabled       |
| KPI            | Enabled       |
| Commitment     | Enabled       |
| Client         | Enabled       |
| Research       | Enabled       |
| Team           | Not Available |
| Department     | Not Available |
| Employee Roles | Not Available |

This keeps the MVP intentionally focused.

---

# 12. Functional Requirements

## Identity

| ID     | Requirement                                        |
| ------ | -------------------------------------------------- |
| FR-031 | One user owns one Personal Workspace               |
| FR-032 | Support Google, Microsoft and Email authentication |
| FR-033 | Automatically resolve Personal Workspace on login  |

## Privacy

| ID     | Requirement                           |
| ------ | ------------------------------------- |
| FR-034 | All memories private by default       |
| FR-035 | No shared visibility                  |
| FR-036 | User can export complete workspace    |
| FR-037 | User can permanently delete workspace |

## Connectors

| ID     | Requirement      |
| ------ | ---------------- |
| FR-038 | Connect Gmail    |
| FR-039 | Connect Slack    |
| FR-040 | Connect Jira     |
| FR-041 | Connect GitHub   |
| FR-042 | Connect Calendar |

---

# 13. Non-Functional Requirements

| Requirement         | Target          |
| ------------------- | --------------- |
| Workspace Isolation | 100%            |
| Cross-user Leakage  | 0               |
| Retrieval Latency   | Less than 3 sec |
| Encryption          | AES-256         |
| Availability        | 99.9%           |
| Export Capability   | One-click       |

---

# 14. Failure Scenarios

## Scenario A — Unauthorized Access

A different user attempts to access Abhijith's workspace.

**Expected Behavior**

* Access denied
* Workspace remains undiscoverable
* No metadata exposed

---

## Scenario B — Connector Removed

User asks:

> Summarize today's client emails.

Gmail has been disconnected.

**Expected Behavior**

TPG informs the user that Gmail is unavailable and requests reconnection instead of generating fabricated results.

---

## Scenario C — Permanent Deletion

User chooses to delete the workspace.

**Expected Behavior**

* Personal memories removed
* Connectors revoked
* Knowledge graph deleted
* Recovery unavailable after retention window

---

# 15. Upgrade Path — Business Edition

Version 1 is intentionally individual-first.

The Business Edition introduces a Corporate Workspace without affecting Personal Memory.

## Evolution Path

```text
V1

User
 │
Personal Workspace
 │
TPG


V2

User
 ├── Personal Workspace
 └── Corporate Workspace
         │
    Shared Company Memory
         │
         TPG
```

The Personal Workspace always remains independent.

Upgrading never merges personal knowledge into company memory automatically.

Explicit user consent will be required in the Business Edition.

---

# 16. Engineering Acceptance Criteria

| ID     | Acceptance Criteria                           |
| ------ | --------------------------------------------- |
| AC-031 | One Personal Workspace created per subscriber |
| AC-032 | Automatic workspace resolution on login       |
| AC-033 | Private memory enforced across all entities   |
| AC-034 | Connectors scoped to the individual user      |
| AC-035 | Complete workspace export supported           |
| AC-036 | Permanent workspace deletion supported        |
| AC-037 | Zero shared visibility between users          |
| AC-038 | ChatGPT serves as the primary interface       |

---

# Design Freeze

This document defines the complete identity and privacy contract for **TPG Individual Edition (V1)**.

No collaboration, RBAC, company hierarchy, or shared organizational memory shall be implemented in Version 1. Those capabilities are reserved for the future Business Edition while maintaining full backward compatibility with every Personal Workspace.

**Next Document:** PRD-0004 — Connector Intelligence Framework (Gmail, Slack, Jira, GitHub & Calendar).
