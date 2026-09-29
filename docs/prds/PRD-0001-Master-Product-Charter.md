# TPG GENESIS — PRD 0001

## Master Product Charter

**Product:** TPG (The Product Guy)  
**Company:** SkynetOrg  
**Document ID:** TPG-PRD-0001  
**Version:** Genesis 1.0  
**Classification:** Confidential  
**Owner:** SkynetOrg Product Office  
**Status:** Design Authority (Source of Truth)  

---

# Executive Summary

## Vision

TPG is an **Autonomous Product Office** that functions as a permanent digital Chief Product Officer embedded inside the tools organizations already use.

TPG is **not an application**.

It is an invisible organizational employee whose primary conversational interface is ChatGPT while its execution layer operates through Slack, Gmail, Jira, GitHub and Calendar.

The objective is to eliminate product knowledge loss and give every organization—from a solo Product Manager to an enterprise—the capability of a world-class product organization.

---

# Product Thesis

Modern companies have excellent tools but no unified product intelligence.

| Existing Tool | What it Knows        | What it Doesn't Know |
| ------------- | -------------------- | -------------------- |
| Slack         | Conversations        | Decisions & history  |
| Gmail         | Client communication | Product context      |
| Jira          | Tasks                | Business rationale   |
| GitHub        | Code                 | Customer problems    |
| Docs          | Specifications       | Living execution     |
| Analytics     | Metrics              | Why features exist   |

TPG becomes the layer that connects every one of these systems into a single organizational brain.

---

# Mission

> Build the world's most trusted digital product executive capable of discovering problems, making product decisions, preserving institutional knowledge and coordinating execution across teams.

---

# Success Definition

A new employee joining after three years should be able to ask:

> Why did we build Vendor Wallet?

And TPG should reconstruct:

* Original customer problem
* Stakeholders involved
* Discovery interviews
* Alternatives considered
* Executive decision
* KPI that justified approval
* Current business outcome

Without anyone manually documenting the story.

---

# Product Principles

## P1 — Invisible First

Users must never change their workflow.

TPG lives where work already happens.

**Primary Interface**
* ChatGPT

**Execution Channels**
* Slack
* Gmail
* Jira
* GitHub
* Calendar

No daily web application is required.

---

## P2 — Organization Owns Memory

Memory is never tied to an individual AI account.

### Personal Workspace
Owned by one user.

Examples:
* Startup ideas
* Interview preparation
* Career planning
* Private PRDs
* Personal research

Visible only to the owner.

### Organization Workspace
Owned by the company.

Examples:
* Clients
* Roadmaps
* PRDs
* Decisions
* Stakeholders
* Jira
* Gmail
* Slack intelligence

Visible according to hierarchy.

No automatic synchronization is permitted between Personal and Organization workspaces.

---

## P3 — Evidence Before Opinion

TPG never recommends features based on intuition alone.

Every recommendation must be supported by evidence such as:
* Customer interviews
* Revenue impact
* Usage analytics
* Jira trends
* Client requests
* Strategic objectives

---

## P4 — Explainability

Every answer must explain:
* Why this recommendation exists
* Evidence used
* Missing evidence
* Risks
* Alternatives
* Confidence level

Black-box reasoning is prohibited.

---

# Product Scope

## Included
* Organizational memory
* Requirement discovery
* Product strategy
* PRD generation
* Jira intelligence
* Client intelligence
* Stakeholder graph
* Commitment tracking
* Executive board reporting
* Role-based permissions

## Explicitly Excluded (V1)
* ERP
* CRM replacement
* Accounting
* HRMS
* UI design tools
* Code IDE

TPG is a **Product Office**, not a Business Operating System.

---

# User Personas

## CEO

### Objectives
* Portfolio visibility
* Product investments
* Board reporting
* Strategic prioritization

### Typical Questions
* What changed this week?
* Which client is highest risk?
* Which initiative should receive investment?
* Prepare tomorrow's board report.

---

## Senior Product Manager

### Responsibilities
* Discovery
* Product strategy
* Roadmap
* PRDs
* Stakeholder management

### Authority
Can create initiatives, approve PRDs, recommend roadmap changes and manage product knowledge.

---

## Junior Product Manager

### Responsibilities
* Customer interviews
* Documentation
* Requirement gathering
* Research

### Restrictions
Cannot access budgets, contracts or confidential executive decisions.

---

## QA Lead

### Responsibilities
* Acceptance criteria
* Test plans
* Release readiness
* Regression tracking

Access limited to engineering artifacts.

---

# Workspace Architecture

TPG supports two independent workspace models.

## Workspace Types

| Type         | Owner      | Visibility |
| ------------ | ---------- | ---------- |
| Personal     | Individual | Private    |
| Organization | Company    | RBAC       |

### Example

```text
SkynetOrg Platform

├── Abhijith (Personal)
├── taSki Workspace
├── Axiom Workspace
└── Client X Workspace
```

Each workspace has:
* Separate database
* Separate memory graph
* Separate permissions
* Separate connectors
* Separate audit logs

Zero data leakage is mandatory.

---

# Organizational Memory

TPG stores **business objects**, not conversations.

## Core Entities

### Company
Represents one organization.

Fields include:
* UUID
* Name
* Industry
* Business model
* Workspace ID
* Created date

---

### Client
Represents external organizations.

Fields:
* Organization
* Industry
* Contract status
* Products used
* Renewal date
* Account health

---

### Person
Represents stakeholders.

Fields:
* Name
* Organization
* Department
* Role
* Influence level
* Decision authority

No personal profiling is allowed.

---

### Initiative
The central object of TPG.

Every product effort becomes an Initiative.

Fields:
* Initiative ID
* Name
* Problem statement
* Owner
* Priority
* Status
* Linked clients
* Linked KPIs
* Version

Everything connects to initiatives.

---

### Requirement
Stores validated customer needs.

Fields:
* Persona
* Pain point
* Business goal
* Constraints
* Source
* Confidence score

---

### Decision
Immutable executive record.

Fields:
* Decision ID
* Outcome
* Rationale
* Evidence
* Alternatives
* Approver
* Timestamp

Decisions are never deleted.
Only superseded.

---

### Commitment
Represents promises detected from conversations.

Example:
> We'll submit the hotel policy on 5 October.

Becomes:
* Owner
* Deliverable
* Due date
* Status
* Reminder state

---

# Role-Based Access Control

Every response must pass authorization.

## Evaluation Pipeline

```text
User
 ↓
Workspace
 ↓
Role
 ↓
Object
 ↓
Response
```

If authorization fails, TPG must decline without revealing hidden information.

## Permission Matrix

| Resource         | CEO | Sr PM |    Jr PM |       QA |
| ---------------- | --: | ----: | -------: | -------: |
| Roadmap          |   ✓ |     ✓ |     Read |       No |
| PRDs             |   ✓ |     ✓ | Assigned | Assigned |
| Client Contracts |   ✓ |  Read |       No |       No |
| Budget           |   ✓ |    No |       No |       No |
| Sprint Analytics |   ✓ |     ✓ |        ✓ |        ✓ |
| Decisions        |   ✓ |     ✓ | Relevant |     Read |

---

# Requirement Intelligence Engine

Purpose: Convert natural conversations into structured product discovery.

## Input Sources
* ChatGPT
* Slack
* Gmail
* Meetings

## Workflow
1. Capture request
2. Detect intent
3. Identify product domain
4. Ask clarifying questions
5. Validate business problem
6. Measure business impact
7. Create initiative
8. Generate decision packet
9. Generate PRD

**Important Rule**  
PRDs shall never be generated before discovery is complete.

---

# Client Intelligence

TPG understands organizations rather than contact lists.

Example:

**IndiGo**
* Head of Operations
* Procurement Lead
* Finance Controller
* IT Integration Manager

Each stakeholder links to:
* Active initiatives
* Previous decisions
* Open requests
* Meeting history

This is organizational intelligence, not CRM.

---

# Commitment Intelligence

TPG continuously watches for commitments.

Example conversation:
> Sarah: We'll deliver the API documentation next Monday.

Automatically creates:
* Deliverable
* Owner
* Due date
* Reminder schedule
* Status

Reminder lifecycle:
* 24 hours before
* Due day
* Overdue
* Completed

---

# Decision Engine

Every strategic recommendation generates a Decision Packet.

## Structure

### Executive Summary
One concise paragraph.

### Business Context
Why this problem matters.

### Evidence
* Customer requests
* Jira trends
* Analytics
* Revenue impact

### Alternatives
Minimum two viable alternatives.

### Risks
* Technical
* Business
* Operational

### Recommendation
Clear executive recommendation with rationale.

### KPIs
Primary and secondary success metrics.

---

# Communication Model

## Primary Experience
ChatGPT  
Every strategic conversation happens here.

## Secondary Channels

### Slack
* Daily briefs
* Sprint summaries
* Product discussions

### Gmail
* Executive reports
* Requirement extraction
* Draft responses

### Jira
* Epic creation
* Sprint intelligence
* Blocker summaries

Users experience one continuous TPG regardless of channel.

---

# Functional Requirements

| ID     | Requirement                    |
| ------ | ------------------------------ |
| FR-001 | Unlimited isolated workspaces  |
| FR-002 | Personal workspace             |
| FR-003 | Organization workspace         |
| FR-004 | RBAC enforcement               |
| FR-005 | Immutable decision ledger      |
| FR-006 | Automatic commitment detection |
| FR-007 | Stakeholder graph              |
| FR-008 | Executive PRD generation       |
| FR-009 | Jira intelligence              |
| FR-010 | LLM-agnostic architecture      |

---

# Non-Functional Requirements

| Requirement           |            Target |
| --------------------- | ----------------: |
| Workspace isolation   |              100% |
| Authorization leakage |                 0 |
| Retrieval latency     |   Less than 3 sec |
| Encryption            | At rest + transit |
| Auditability          |         Mandatory |
| Availability          |             99.9% |

---

# Commercial Model

## Individual Subscription
One Personal Workspace.  
Private product office.

## Organization Subscription
Shared organizational workspace with hierarchy.

Examples:
* taSki
* Axiom
* Enterprise customers

One user may belong to multiple organizations while retaining one completely private workspace.

---

# Product Positioning

**Company:** SkynetOrg  
**Product:** TPG  
**Category:** Autonomous Product Office  
**Tagline:** *The invisible Product Guy inside your organization.*

TPG is not an AI assistant.  
It is a permanent digital product executive that accumulates institutional knowledge, explains every decision, coordinates execution and preserves the product history of an organization.

---

# Design Freeze Criteria

This PRD is the constitutional authority for TPG Genesis.

Engineering implementation cannot begin until the following companion specifications are completed:

1. PRD-0002 — Organizational Memory Schema
2. PRD-0003 — RBAC & Security Architecture
3. PRD-0004 — Connector Framework
4. PRD-0005 — Requirement Intelligence Engine
5. PRD-0006 — Decision Engine
6. PRD-0007 — Client Intelligence
7. PRD-0008 — Commitment Intelligence
8. PRD-0009 — TPG Constitutional Prompt System

**End of PRD-0001**
