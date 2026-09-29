# TPG GENESIS — PRD 0004

## Connector Intelligence Framework (CIF)

**Product:** TPG (The Product Guy)  
**Company:** SkynetOrg  
**Document ID:** TPG-PRD-0004  
**Version:** Genesis 1.1  
**Classification:** Internal / Confidential  
**Owner:** SkynetOrg Platform Architecture  
**Depends On:** PRD-0001, PRD-0002, PRD-0003  
**Status:** Engineering Specification  

---

# 1. Purpose

The Connector Intelligence Framework (CIF) enables TPG to observe the user's existing product ecosystem and transform fragmented information into structured product intelligence.

**TPG is not another workspace.** It lives inside ChatGPT while connecting securely to Gmail, Slack, Jira, GitHub and Calendar.

### Primary Responsibilities

* Read product-related information
* Extract requirements and decisions
* Build structured memory
* Generate insights
* Execute approved internal actions
* Never communicate directly with external clients

---

# 2. Product Philosophy

## Constitutional Principle

> **Read everywhere. Understand intelligently. Act internally.**

Connectors exist to enhance the user's Product Office—not replace existing tools.

Every connector follows three phases:

1. Observe
2. Understand
3. Execute (with permission)

Raw messages are **never** the source of truth.

The source of truth is TPG Memory.

---

# 3. System Architecture

```text
                    ChatGPT

                       │

                 Conversation Layer

                       │

                      TPG

                       │

        Connector Intelligence Framework

 ┌──────────┬─────────┬─────────┬─────────┬──────────┐
 │          │         │         │         │          │
 Gmail    Slack     Jira    GitHub   Calendar
 │          │         │         │          │
 └──────────┴─────────┴─────────┴──────────┘
                    │
            Knowledge Extractor
                    │
            Personal Memory Graph
```

**ChatGPT is always the only user interface.**

Users never interact directly with connector modules.

---

# 4. Connector Lifecycle

Every connector behaves identically.

## Phase 1 — Authentication

Supported authentication:

* Google OAuth
* Microsoft OAuth
* Atlassian OAuth
* GitHub OAuth

Rules:

* Passwords are never stored.
* Refresh tokens are encrypted.
* Users can revoke access anytime.
* Connector permissions are granular.

---

## Phase 2 — Observation

TPG retrieves only relevant product information.

Examples:

### Gmail

* Product discussions
* Client requests
* Feature feedback
* Meeting invitations

### Slack

* Product channels
* Threads
* Mentions
* Sprint discussions

### Jira

* Epics
* Stories
* Bugs
* Sprint data

### Calendar

* Product reviews
* Client meetings
* Sprint planning

---

## Phase 3 — Intelligence Extraction

Raw information becomes structured entities.

Example Slack message:

> We'll complete Vendor Wallet API by 5 October.

Generated entities:

* Commitment
* Initiative Link
* Due Date
* Owner
* Confidence Score

The original message is referenced but **not duplicated** into memory.

---

## Phase 4 — User Approved Execution

TPG performs actions only after explicit user intent.

Examples:

| User Request        | Action                |
| ------------------- | --------------------- |
| Create Jira stories | Create issues         |
| Draft email         | Generate draft        |
| Summarize sprint    | Read Jira only        |
| Prepare meeting     | Read Calendar + Gmail |

Automatic external execution is prohibited.

---

# 5. Gmail Connector

## Objective

Transform email into product intelligence.

### Read Capabilities

| Capability           | Supported |
| -------------------- | --------- |
| Read inbox           | ✓         |
| Read labels          | ✓         |
| Search emails        | ✓         |
| Extract requirements | ✓         |
| Detect commitments   | ✓         |
| Detect stakeholders  | ✓         |

---

## Write Capabilities

| Capability    | Supported           |
| ------------- | ------------------- |
| Draft email   | ✓                   |
| Suggest reply | ✓                   |
| Send email    | Human approval only |
| Delete email  | ✗                   |
| Archive email | ✗                   |

TPG never modifies mailbox state.

---

## Intelligence Extraction

Example email:

> We require bulk hotel allocation with policy enforcement before November.

TPG creates:

* Requirement
* Client
* Suggested Initiative
* Priority estimate
* Linked evidence

---

## Email Draft Workflow

User:

> Reply professionally.

TPG generates:

* Subject
* Body
* Attachments (suggested)
* Tone

The user reviews before sending.

---

# 6. Slack Connector

## Objective

Convert daily conversations into institutional knowledge.

### Read Scope

* Product channels
* Engineering channels
* Design channels
* Threads
* Mentions

Private channels require explicit authorization.

---

## Intelligence Types

### Decisions

Message:

> Let's postpone Wallet until Q4.

Creates:

Decision Draft

---

### Commitments

Message:

> I'll finish API tomorrow.

Creates:

Commitment

---

### Requirements

Message:

> Client wants offline rostering.

Creates:

Requirement

---

## Daily Product Brief

User:

> What happened today?

TPG summarizes:

* New decisions
* New requirements
* Risks
* Blockers
* Pending commitments

Never returns raw chronological chat logs unless requested.

---

# 7. Jira Connector

## Objective

Convert execution into product intelligence.

### Read

| Object   | Supported |
| -------- | --------- |
| Projects | ✓         |
| Epics    | ✓         |
| Stories  | ✓         |
| Bugs     | ✓         |
| Sprints  | ✓         |
| Comments | ✓         |

---

### Write

| Action        | Supported |
| ------------- | --------- |
| Create Epic   | ✓         |
| Create Story  | ✓         |
| Update Status | ✓         |
| Add Labels    | ✓         |
| Delete Issues | ✗         |

Deletion is permanently disabled.

---

## Sprint Intelligence

User:

> Review Sprint 18.

TPG analyzes:

* Velocity
* Spillover
* Blockers
* Bug trends
* Delivery risks
* KPI impact

It explains **what happened**, not just statistics.

---

## PRD → Jira

Input:

Approved PRD

Output:

* Epic
* Stories
* Tasks
* Acceptance Criteria
* Labels
* Priority

This becomes a core flagship workflow.

---

# 8. GitHub Connector

## Objective

Give product managers engineering awareness.

### Read

* Pull Requests
* Reviews
* Commits
* Releases
* Tags

### Intelligence

TPG identifies:

* Release readiness
* Review bottlenecks
* Linked initiatives
* Engineering blockers

Example:

> Why is Wallet delayed?

TPG correlates:

* Jira
* GitHub
* Slack
* Decisions

To produce one explanation.

---

# 9. Calendar Connector

## Objective

Convert meetings into structured knowledge.

### Detect

* Client meetings
* Sprint planning
* Product reviews
* Retrospectives
* Leadership meetings

---

## Pre-Meeting Brief

User:

> Prepare me for tomorrow's IndiGo meeting.

TPG provides:

* Client summary
* Previous decisions
* Open requests
* Stakeholders
* Risks
* Recommended agenda
* Suggested questions

---

## Post-Meeting Intelligence

Input:

Transcript or notes

Output:

* Requirements
* Decisions
* Commitments
* Action Items
* Linked Initiative

Meeting notes become structured memory.

---

# 10. Connector Intelligence Engine

All connectors pass through one extraction engine.

## Processing Pipeline

```text
External Data

↓

Cleaner

↓

Intent Detection

↓

Entity Recognition

↓

Confidence Scoring

↓

Validation

↓

Memory Graph
```

No connector writes directly into memory.

Validation is mandatory.

---

# 11. Confidence Scoring

Every extracted entity receives confidence.

|      Score | Action               |
| ---------: | -------------------- |
|  0.95–1.00 | Auto-create Draft    |
|  0.80–0.94 | Ask for confirmation |
| Below 0.80 | Ignore               |

Example:

Slack:

> Maybe we should redesign Wallet.

Confidence:

0.41

Result:

Ignored.

---

# 12. Synchronization Rules

## Incremental Sync

TPG synchronizes only changes.

Rules:

* Preserve timestamps
* Preserve source
* Detect duplicates
* Never overwrite edited memory
* Never duplicate initiatives

Example:

Vendor Wallet appears in Gmail and Slack.

Result:

One Initiative

Two evidence sources

Higher confidence

---

# 13. User Command Library

## Gmail

* Summarize today's product emails
* Find every email about Wallet
* Draft reply to IndiGo
* Extract feature requests

---

## Slack

* What happened today?
* Show unresolved blockers
* Find Wallet discussions
* Summarize sprint channel

---

## Jira

* Review current sprint
* Create stories from PRD
* Which bugs block release?
* Show overdue epics

---

## Calendar

* Prepare tomorrow's meeting
* Summarize today's meetings
* List action items
* Show pending commitments

---

## Universal

> What changed this week?

TPG combines every connector into one executive briefing.

---

# 14. Client Interaction Policy

## Constitutional Rule

> **TPG is an internal organizational teammate. It never communicates directly with clients.**

Clients are external stakeholders.

Employees are TPG's users.

This distinction is mandatory.

---

## Allowed Actions

| Action                       | Allowed |
| ---------------------------- | ------- |
| Read client emails           | ✓       |
| Analyze client requirements  | ✓       |
| Prepare meeting briefings    | ✓       |
| Draft email for review       | ✓       |
| Generate PRDs                | ✓       |
| Create Jira stories          | ✓       |
| Track commitments internally | ✓       |

---

## Prohibited Actions

| Action                             | Status |
| ---------------------------------- | ------ |
| Send emails directly to clients    | ❌      |
| Reply automatically to customers   | ❌      |
| Join client WhatsApp conversations | ❌      |
| Negotiate with clients             | ❌      |
| Send proposals autonomously        | ❌      |
| Represent itself as the company    | ❌      |

TPG always operates **behind the employee**, never in front of the client.

---

## Client Workflow

```text
Client Email

↓

TPG Reads

↓

Requirement Extraction

↓

Initiative Suggestion

↓

Draft Reply

↓

Employee Reviews

↓

Employee Sends
```

TPG never becomes the sender.

---

# 15. Internal Communication Policy

TPG may communicate freely with authenticated organization members.

Examples:

* PM ↔ TPG
* QA ↔ TPG
* Engineering ↔ TPG
* Founder ↔ TPG

TPG behaves like an internal senior product executive.

It does not participate in customer conversations.

---

# 16. Privacy & Security

## Connector Ownership

All connectors belong to the individual subscriber in Version 1.

Example:

Abhijith connects:

* Gmail
* Slack
* Jira

Only Abhijith can access those integrations.

---

## Security Rules

| Rule    | Requirement                                        |
| ------- | -------------------------------------------------- |
| CIF-001 | OAuth authentication only                          |
| CIF-002 | Encrypt all access tokens                          |
| CIF-003 | Never store passwords                              |
| CIF-004 | Store structured entities only                     |
| CIF-005 | Preserve source references                         |
| CIF-006 | User may revoke anytime                            |
| CIF-007 | Never expose raw client data outside user requests |

---

# 17. Failure Scenarios

## Gmail Disconnected

User:

> Summarize today's emails.

Expected:

Inform user Gmail is disconnected.

Offer reconnection.

Never fabricate.

---

## Jira Permission Lost

User:

> Create stories.

Expected:

Explain authorization failure.

Do not lose PRD context.

---

## Duplicate Requirement

Requirement appears in Slack and Gmail.

Expected:

* Merge evidence
* Increase confidence
* Preserve both sources

---

## Client Email Reply

User has not approved the draft.

Expected:

Draft only.

No email sent.

---

# 18. Functional Requirements

| ID      | Requirement                           |
| ------- | ------------------------------------- |
| CIF-101 | Connect Gmail                         |
| CIF-102 | Connect Slack                         |
| CIF-103 | Connect Jira                          |
| CIF-104 | Connect GitHub                        |
| CIF-105 | Connect Calendar                      |
| CIF-106 | Extract structured entities           |
| CIF-107 | Generate email drafts                 |
| CIF-108 | Create Jira stories from PRDs         |
| CIF-109 | Produce executive summaries           |
| CIF-110 | Preserve evidence references          |
| CIF-111 | Never initiate client communication   |
| CIF-112 | Require approval for outbound emails  |
| CIF-113 | Client messages are read-only sources |
| CIF-114 | Operate only with authenticated users |

---

# 19. Non-Functional Requirements

| Requirement                |     Target |
| -------------------------- | ---------: |
| Sync latency               | <2 minutes |
| Entity extraction accuracy |       >90% |
| Duplicate detection        |       >95% |
| Connector uptime           |      99.5% |
| OAuth security             |  Mandatory |
| Outbound client autonomy   |         0% |

---

# 20. Future Connectors (Excluded from V1)

| Connector         | Future Purpose              |
| ----------------- | --------------------------- |
| Notion            | Knowledge import            |
| Linear            | Engineering projects        |
| ClickUp           | Task management             |
| HubSpot           | Sales intelligence          |
| Figma             | Design reviews              |
| Teams             | Enterprise communication    |
| WhatsApp Business | Requirement extraction only |

Personal WhatsApp is intentionally unsupported.

---

# Design Freeze

The Connector Intelligence Framework defines how TPG observes external systems while remaining an **internal Product Office**.

**Key Constitutional Rules**

1. ChatGPT is the primary interface.
2. Connectors are intelligence sources, not memory.
3. Memory stores structured knowledge only.
4. Every outbound action requires user intent.
5. TPG never communicates directly with clients.
6. Employees remain the official representatives of the organization.

**Next Document:** PRD-0005 — Requirement Intelligence Engine (Discovery, JTBD, Product Thinking & Autonomous PRD Generation).
