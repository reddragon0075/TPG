# PRD-0007 — Product Strategy, Roadmap Intelligence & Portfolio Management

**Product:** TPG 1.0 — The Product Guy  
**Organization:** SkynetOrg  
**Document ID:** PRD-0007  
**Status:** Design Specification  
**Priority:** P0 — Core Product Intelligence  
**Depends On:** PRD-0001 through PRD-0006  
**Primary Interface:** ChatGPT  
**Architecture:** Internal Specialist Agents + Unified TPG Identity  

---

# 1. Executive Summary

PRD-0006 gave TPG the ability to reason about individual product decisions.

PRD-0007 gives TPG the ability to understand and manage the **strategic system surrounding those decisions**.

A real senior Product Executive does not simply ask:

> "Should we build this feature?"

They continuously ask:

* Where is the company going?
* What are we trying to achieve?
* Which markets matter?
* Which customer problems matter most?
* Which product bets support the strategy?
* What should we invest in?
* What should we deliberately not invest in?
* What should happen now?
* What should happen later?
* Which initiatives depend on each other?
* Is the roadmap still aligned with strategy?
* Are we over-investing in one area?
* What has changed?
* What assumptions are becoming invalid?
* Are we building toward an outcome or merely filling a backlog?

TPG must therefore maintain a continuously evolving model of:

```text
Company Strategy
        ↓
Strategic Objectives
        ↓
Product Strategy
        ↓
Strategic Bets
        ↓
Product Outcomes
        ↓
Opportunities
        ↓
Initiatives
        ↓
Roadmap
        ↓
Execution
        ↓
Measured Outcomes
        ↓
Strategic Learning
```

The roadmap must become a **living strategic model**, not a list of dates and tickets.

---

# 2. Product Principle

> **A roadmap is a hypothesis about how the organization will achieve its strategic objectives.**

Therefore:

```text
Strategy → Outcomes → Bets → Roadmap
```

not:

```text
Backlog → Dates → Roadmap → Strategy
```

---

# 3. Core Objective

The Product Strategy & Roadmap Intelligence Engine must enable TPG to:

1. understand company strategy;
2. understand product strategy;
3. identify strategic themes;
4. maintain strategic objectives;
5. identify product bets;
6. connect bets to outcomes;
7. construct and analyze roadmaps;
8. sequence initiatives;
9. detect roadmap conflicts;
10. detect strategic drift;
11. identify gaps;
12. model scenarios;
13. analyze portfolio balance;
14. detect over-investment;
15. identify under-investment;
16. track strategic assumptions;
17. monitor strategy changes;
18. continuously reconcile strategy with execution.

---

# 4. Strategy Hierarchy

TPG must represent strategy hierarchically.

```text
Company Vision
      ↓
Company Mission
      ↓
Strategic Themes
      ↓
Strategic Objectives
      ↓
Product Strategy
      ↓
Product Outcomes
      ↓
Strategic Bets
      ↓
Initiatives
      ↓
Features / Requirements
      ↓
Execution
```

---

# 5. Strategic Theme

A Strategic Theme represents a major direction.

Examples:

* Enterprise Expansion
* Retention
* Automation
* Internationalization
* Platformization
* AI Transformation
* Operational Efficiency
* Product-Led Growth

A theme should not itself be a project.

---

# 6. Strategic Theme Schema

```json
{
  "theme_id": "THEME-001",
  "name": "Enterprise Expansion",
  "description": "...",
  "status": "ACTIVE",
  "priority": "HIGH",
  "time_horizon": "12_24_MONTHS",
  "objectives": [],
  "strategic_bets": [],
  "success_metrics": []
}
```

---

# 7. Strategic Objective

An objective defines what the organization intends to achieve.

Example:

> Increase enterprise retention.

It must not simply describe activity:

> Build customer dashboard.

---

# 8. Objective Schema

```json
{
  "objective_id": "OBJ-001",
  "theme_id": "THEME-001",
  "name": "Increase Enterprise Retention",
  "description": "...",
  "baseline": 92,
  "target": 97,
  "unit": "%",
  "deadline": "2027-03-31",
  "owner": "USER",
  "status": "ACTIVE",
  "confidence": 0.82
}
```

---

# 9. Objective Types

TPG must support:

| Type       | Example                        |
| ---------- | ------------------------------ |
| Revenue    | Increase ARR                   |
| Growth     | Increase new customers         |
| Retention  | Reduce churn                   |
| Engagement | Increase weekly active users   |
| Adoption   | Increase feature adoption      |
| Efficiency | Reduce operational cost        |
| Quality    | Reduce production incidents    |
| Customer   | Improve CSAT                   |
| Market     | Enter new segment              |
| Strategic  | Establish platform capability  |
| Technical  | Reduce critical technical debt |
| Compliance | Achieve regulatory requirement |

---

# 10. Product Strategy

TPG must understand the difference between:

### Company Strategy

Where the company wants to go.

### Product Strategy

How the product contributes to getting there.

### Roadmap

Which bets and initiatives will be pursued to execute the strategy.

---

# 11. Product Strategy Object

```json
{
  "strategy_id": "STRAT-001",
  "mission": "...",
  "target_market": [],
  "target_users": [],
  "strategic_themes": [],
  "competitive_position": [],
  "differentiators": [],
  "objectives": [],
  "strategic_bets": [],
  "constraints": [],
  "assumptions": [],
  "review_date": "..."
}
```

---

# 12. Strategy Questions TPG Must Answer

TPG should be able to answer:

> "What is our current product strategy?"

> "What are our strategic priorities?"

> "What are our biggest product bets?"

> "Why are we investing in this?"

> "Which roadmap items support retention?"

> "What percentage of engineering capacity supports growth?"

> "What strategic objectives have no roadmap support?"

> "Which roadmap items have weak strategic alignment?"

> "What has changed in our strategy?"

> "What are we not investing in?"

> "Where are we spreading ourselves too thin?"

---

# 13. Strategic Bet

A Strategic Bet is a meaningful investment made under uncertainty.

Examples:

* Enterprise AI automation
* International expansion
* New B2C product
* Platform transformation
* Self-service onboarding
* New distribution channel

A strategic bet is larger than an individual feature.

---

# 14. Strategic Bet Schema

```json
{
  "bet_id": "BET-001",
  "name": "AI-Powered Operations",
  "hypothesis": "...",
  "strategic_theme": "Automation",
  "expected_outcomes": [],
  "investment": {},
  "initiatives": [],
  "assumptions": [],
  "risks": [],
  "confidence": 0.61,
  "status": "ACTIVE"
}
```

---

# 15. Strategic Bet Lifecycle

```text
IDEA
 ↓
HYPOTHESIS
 ↓
EXPLORATION
 ↓
VALIDATION
 ↓
INVESTMENT
 ↓
EXECUTION
 ↓
MEASUREMENT
 ↓
SCALE / ADJUST / STOP
```

---

# 16. Bet Management

TPG must treat strategic bets as hypotheses.

For every bet:

```text
What do we believe?
Why do we believe it?
What evidence supports it?
What must be true?
How much are we investing?
What will prove us wrong?
When will we review it?
```

---

# 17. Strategy Assumption Register

TPG must maintain strategic assumptions.

Example:

```text
SA-001
Enterprise customers increasingly prefer automated workflows.

Confidence: Medium

SA-002
AI automation can reduce operational cost materially.

Confidence: Medium

SA-003
The company can acquire sufficient enterprise customers.

Confidence: Low
```

Strategic assumptions must be linked to the bets that depend on them.

---

# 18. Strategic Assumption Monitoring

TPG should continuously look for evidence that changes strategic assumptions.

Sources:

* customer conversations;
* sales pipeline;
* product analytics;
* market research;
* support data;
* competitive intelligence;
* financial results;
* operational metrics;
* engineering constraints.

When evidence changes:

> TPG should flag the affected strategy or bet.

---

# 19. Strategy Drift Detection

Strategy drift occurs when execution gradually moves away from strategy.

Example:

```text
Strategic Objective:
Enterprise retention

Current roadmap:
70% new feature development
20% internal tooling
10% retention initiatives
```

TPG should surface:

> "Current roadmap allocation appears materially different from the stated strategic emphasis."

It should show the underlying data rather than declaring the strategy wrong.

---

# 20. Roadmap Model

A roadmap item must contain more than:

```text
Feature
Date
Owner
```

It must contain:

```text
Outcome
Strategic Objective
Bet
Opportunity
Initiative
Dependencies
Expected Impact
Confidence
Investment
Timing
Success Metric
```

---

# 21. Roadmap Schema

```json
{
  "roadmap_item_id": "ROAD-001",
  "initiative_id": "INIT-001",
  "strategic_bet_id": "BET-001",
  "objective_ids": [],
  "target_outcome": "...",
  "time_horizon": "Q1",
  "status": "PLANNED",
  "confidence": 0.74,
  "dependencies": [],
  "capacity_required": {},
  "success_metrics": [],
  "risks": []
}
```

---

# 22. Roadmap Horizons

TPG should support:

## Now

0–3 months

## Next

3–6 months

## Later

6–12 months

## Future

12+ months

Exact dates should only be used where justified.

---

# 23. Avoid False Precision

TPG must not present speculative dates as commitments.

Bad:

> Launch Dashboard Builder on March 14.

when engineering has not estimated it.

Better:

> Target: Q2, contingent on platform API dependency and engineering sizing.

---

# 24. Roadmap Confidence

Each roadmap item should have confidence:

```text
HIGH
MEDIUM
LOW
UNKNOWN
```

Based on:

* validated problem;
* solution clarity;
* engineering estimate;
* dependencies;
* capacity;
* strategic stability;
* external constraints.

---

# 25. Roadmap Commitment Levels

TPG must distinguish:

### COMMITTED

Organization has explicitly approved it.

### TARGET

Intended timing but not guaranteed.

### PLANNED

Likely future work.

### EXPLORATORY

Under investigation.

### BACKLOG

Potential opportunity.

This prevents roadmap misinformation.

---

# 26. Roadmap Structure

Example:

```text
2027
│
├── Q1
│   ├── Enterprise Reliability
│   └── Automation Foundation
│
├── Q2
│   ├── Self-Service Platform
│   └── Enterprise Analytics
│
├── Q3
│   └── International Expansion
│
└── Q4
    └── Platform Scale
```

But TPG should also represent the outcome behind each item.

---

# 27. Outcome Roadmap

Instead of:

> Q1 — Dashboard

TPG should represent:

> **Q1 Outcome: Improve enterprise operational visibility**

Initiatives:

* Standard dashboards
* Alerting
* Reporting API

---

# 28. Outcome Mapping

Every significant roadmap initiative should map to:

```text
Initiative
 ↓
Outcome
 ↓
KPI
 ↓
Target
```

Example:

```text
Initiative:
Automated reconciliation

Outcome:
Reduce manual operations

KPI:
Processing hours / 1,000 transactions

Target:
-50%
```

---

# 29. Roadmap Dependencies

TPG must model:

```text
Identity Platform
      ↓
Permission Engine
      ↓
Corporate Workspace
      ↓
Enterprise Collaboration
```

The roadmap should automatically reflect dependency ordering.

---

# 30. Dependency Types

* Technical
* Data
* Product
* Design
* Operational
* Organizational
* Vendor
* Regulatory
* Customer
* Financial
* Market

---

# 31. Critical Path

TPG should identify the critical path.

Example:

```text
API modernization
      ↓
New data model
      ↓
Reporting service
      ↓
Enterprise dashboard
```

If API modernization slips:

> All downstream initiatives may be affected.

---

# 32. Roadmap Collision Detection

TPG must identify:

### Same Team Collision

Two initiatives require the same team.

### Same Dependency Collision

Two initiatives require the same unfinished capability.

### Same Customer Collision

Too many simultaneous changes for the same customer.

### Same Release Collision

Too many high-risk initiatives planned for one release.

---

# 33. Capacity-Aware Roadmapping

Where data exists:

```text
Available Capacity
-
Committed Work
=
Remaining Capacity
```

Then:

```text
Candidate Initiative Effort
≤
Remaining Capacity
```

If not:

> Capacity conflict.

TPG must not simply squeeze more work into the roadmap.

---

# 34. Portfolio Management

TPG must maintain a portfolio across strategic categories.

Example:

| Category   | Investment |
| ---------- | ---------: |
| Growth     |        35% |
| Retention  |        25% |
| Efficiency |        15% |
| Platform   |        15% |
| Compliance |        10% |

These percentages are descriptive measurements, not fixed recommendations.

---

# 35. Portfolio Dimensions

TPG should analyze:

* strategic theme;
* customer segment;
* product area;
* revenue impact;
* retention impact;
* technical investment;
* operational investment;
* innovation;
* compliance;
* geography;
* lifecycle stage.

---

# 36. Portfolio Concentration

TPG must detect concentration.

Example:

> 62% of planned product investment depends on one strategic bet.

TPG should flag:

> Concentration Risk.

It must not automatically conclude that concentration is bad; context matters.

---

# 37. Portfolio Gaps

TPG should detect:

### Objective with no initiative

```text
Objective:
Reduce churn

Initiatives:
None

Gap detected.
```

### Initiative with no objective

```text
Initiative:
Custom dashboard

Strategic alignment:
Unknown
```

### KPI with no owner

```text
Retention KPI
Owner:
Unknown
```

---

# 38. Strategic Orphans

A **Strategic Orphan** is an initiative with no meaningful connection to:

* strategy;
* objective;
* customer problem;
* measurable outcome.

Example:

```text
INIT-092
"UI modernization"

Strategic objective:
None

Problem:
Unknown

Outcome:
Unknown
```

TPG should surface this for review.

---

# 39. Strategic Debt

Strategic debt occurs when important strategic capabilities remain repeatedly deferred.

Example:

```text
Platform reliability
Deferred:
4 consecutive quarters
```

TPG should recognize:

> Strategic Debt Accumulation.

---

# 40. Technical Debt vs Strategic Debt

TPG must distinguish:

### Technical Debt

Architecture or code quality degradation.

### Strategic Debt

Repeated failure to invest in an important strategic capability.

Both can affect roadmap health.

---

# 41. Roadmap Health

TPG should maintain a roadmap health model.

Dimensions:

```text
Strategic Alignment
Outcome Clarity
Evidence Quality
Capacity Feasibility
Dependency Health
Risk
Confidence
Commitment Quality
Metric Coverage
```

---

# 42. Roadmap Health Output

Example:

```text
ROADMAP HEALTH

Strategic Alignment: Strong
Outcome Coverage: Medium
Capacity Feasibility: At Risk
Dependency Health: Medium
Evidence Quality: Strong
Metric Coverage: Weak

Primary concern:
3 initiatives have no measurable success criteria.
```

---

# 43. Roadmap Change Detection

TPG should track:

```text
Original Roadmap
       ↓
Current Roadmap
       ↓
Changes
```

Detect:

* added initiatives;
* removed initiatives;
* priority changes;
* timing changes;
* scope changes;
* ownership changes;
* dependency changes.

---

# 44. Roadmap Churn

TPG should measure:

> How frequently does the roadmap change?

Example:

```text
Quarterly Roadmap Churn:
38%

Major changes:
12
```

High churn may indicate uncertainty, but TPG must investigate context rather than automatically labeling it as unhealthy.

---

# 45. Strategy Versioning

Strategy must be immutable by version.

```text
Strategy v1
   ↓
Strategy v2
   ↓
Strategy v3
```

Each version contains:

* date;
* changes;
* rationale;
* affected objectives;
* affected bets;
* affected roadmap items.

---

# 46. Strategy Change Impact Analysis

When strategy changes, TPG must determine:

```text
Strategy Change
      ↓
Affected Objectives
      ↓
Affected Bets
      ↓
Affected Initiatives
      ↓
Affected PRDs
      ↓
Affected Jira Work
      ↓
Affected KPIs
```

Example:

> Company shifts from SMB acquisition to enterprise retention.

TPG should identify which current roadmap items are affected.

---

# 47. Strategy Simulation

TPG should support:

> "What happens if we prioritize enterprise retention for the next two quarters?"

The engine should model:

* roadmap changes;
* displaced initiatives;
* capacity;
* dependencies;
* expected outcomes;
* risks;
* assumptions.

It should clearly mark simulations as hypothetical.

---

# 48. Scenario Planning

Supported scenarios:

### Base Case

Current strategy continues.

### Growth Case

Higher investment in expansion.

### Efficiency Case

Higher investment in automation.

### Defensive Case

Focus on retention and reliability.

### Constraint Case

Engineering capacity reduced.

---

# 49. Scenario Comparison

TPG should compare:

| Dimension        | Scenario A | Scenario B      |
| ---------------- | ---------- | --------------- |
| Strategic Focus  | Growth     | Retention       |
| Investment       | High       | Medium          |
| Capacity         | High       | Medium          |
| Expected Outcome | Expansion  | Stability       |
| Key Risk         | Execution  | Growth slowdown |
| Major Dependency | Sales      | Platform        |

No scenario should be presented as automatically correct.

---

# 50. "What Are We Not Doing?"

TPG must explicitly maintain a **Not Doing / Deferred** area.

```text
NOT NOW
├── Custom reporting
├── Mobile redesign
└── Secondary market expansion
```

Each item should have a reason:

* low strategic value;
* insufficient evidence;
* dependency;
* capacity;
* timing;
* deliberate strategic choice.

---

# 51. Strategic Exclusion

A deliberate exclusion is itself a strategic decision.

TPG must preserve:

```text
What we decided not to build
Why
When
What evidence supported the decision
What would cause reconsideration
```

---

# 52. Roadmap Review

TPG should support:

## Weekly

Execution alignment.

## Monthly

Initiative health.

## Quarterly

Roadmap and strategic alignment.

## Semiannual / Annual

Strategy review.

---

# 53. Weekly Product Strategy Brief

TPG may generate:

```text
THIS WEEK

Strategy Changes:
None

Roadmap Changes:
3

New Strategic Signals:
2

At-Risk Initiatives:
4

Blocked Initiatives:
2

Important Decisions:
3

Objective Performance:
2 objectives trending below target

Recommended Attention:
Enterprise retention initiative
```

---

# 54. Quarterly Product Review

TPG should generate:

```text
Quarterly Product Review

1. Strategy
2. Objectives
3. Portfolio
4. Roadmap
5. Outcomes
6. Wins
7. Misses
8. Strategic Assumptions
9. Bets
10. Risks
11. Capacity
12. Next Quarter
```

---

# 55. Strategy-to-Execution Traceability

TPG must support full traceability:

```text
Strategy
 ↓
Objective
 ↓
Bet
 ↓
Opportunity
 ↓
Decision
 ↓
Initiative
 ↓
PRD
 ↓
Requirement
 ↓
Epic
 ↓
Story
 ↓
Release
 ↓
KPI
 ↓
Outcome
```

This is one of the most important capabilities of the system.

---

# 56. Reverse Traceability

TPG must also work backwards.

Given a Jira ticket:

> "Add export button."

TPG should answer:

```text
Story
 ↓
Epic
 ↓
Initiative
 ↓
Decision
 ↓
Opportunity
 ↓
Objective
 ↓
Strategy
```

If the chain breaks:

> Strategic Traceability Gap.

---

# 57. Strategic Traceability Score

For internal diagnostics:

```text
Strategic Traceability =
Items linked to valid strategic context
----------------------------------------
Total material roadmap items
```

The system should identify missing links rather than inventing them.

---

# 58. Roadmap Evidence Model

Each roadmap item should identify:

```text
Why is this on the roadmap?

Customer Evidence
Business Evidence
Product Evidence
Technical Evidence
Strategic Evidence
```

---

# 59. Roadmap Evidence Freshness

Evidence becomes stale.

TPG should track:

```text
Fresh
Aging
Stale
Unknown
```

Example:

> Initiative priority is based on customer research conducted 18 months ago.

TPG should flag evidence freshness.

---

# 60. Market and Competitive Signals

When external research is available, TPG may incorporate:

* competitor launches;
* pricing changes;
* market movements;
* regulatory changes;
* customer trends;
* technology changes.

But external signals must remain separate from internal facts.

```text
Internal Evidence
External Evidence
Assumption
```

---

# 61. Strategy Signal Detection

TPG should identify signals such as:

```text
Competitor launches capability X
+
Customers request capability X
+
Sales loses deals due to capability X
```

Potential strategic signal:

> Market positioning may require review.

TPG should escalate for analysis rather than automatically changing strategy.

---

# 62. Product Lifecycle Management

TPG must understand:

```text
IDEA
 ↓
EXPERIMENT
 ↓
MVP
 ↓
GROWTH
 ↓
SCALE
 ↓
MATURE
 ↓
DECLINE
 ↓
SUNSET
```

Roadmap allocation should be analyzable by lifecycle stage.

---

# 63. Product Sunset Intelligence

TPG should identify products/features showing:

* declining usage;
* increasing maintenance cost;
* declining customer value;
* obsolete technology;
* strategic irrelevance.

It should produce a sunset analysis:

```text
Usage
Revenue
Customers
Maintenance
Dependencies
Migration Cost
Replacement
Risk
```

---

# 64. Sunset Decision

TPG must not automatically delete or deprecate.

It should create:

> Sunset Decision Proposal.

Human approval required.

---

# 65. Strategic Risk Register

TPG must maintain:

```text
Risk
Probability
Impact
Affected Strategy
Affected Bet
Mitigation
Owner
Status
```

Example:

```text
Risk:
Dependency on third-party API.

Probability:
Medium

Impact:
High

Affected Bet:
Automation Platform
```

---

# 66. Strategic Risk Triggers

TPG should monitor:

* objective deterioration;
* dependency delays;
* budget changes;
* capacity changes;
* market shifts;
* customer churn;
* vendor changes;
* technical incidents;
* regulatory developments.

---

# 67. Strategic Decision Queue

TPG should maintain:

```text
DECISION QUEUE

1. Enterprise pricing model
2. Dashboard investment
3. API modernization
4. International expansion
5. Mobile strategy
```

Each decision contains:

* urgency;
* impact;
* uncertainty;
* owner;
* required evidence;
* deadline.

---

# 68. Roadmap Query Examples

The user can ask:

> "Show me our roadmap."

> "Why is this on the roadmap?"

> "What are our strategic bets?"

> "What are we over-investing in?"

> "What are we under-investing in?"

> "Which objectives have no roadmap support?"

> "Which roadmap items have no measurable outcome?"

> "What changed this quarter?"

> "What should move out if we prioritize retention?"

> "What happens if engineering capacity drops 20%?"

> "Which initiatives are dependent on the platform migration?"

> "Which initiatives are at risk?"

> "What strategic assumptions are weakening?"

---

# 69. Internal Specialist Architecture

The Strategy Engine should use invisible specialist modules.

```text
                         TPG
                          │
                 Strategy Orchestrator
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   Strategy Agent    Roadmap Agent    Portfolio Agent
        │                 │                 │
   Objective Agent   Dependency Agent   Risk Agent
        │                 │                 │
   Market Agent      Capacity Agent    Outcome Agent
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                  Strategy Synthesizer
                          │
                         TPG
```

The user must never be required to select these agents.

---

# 70. Strategy Orchestrator

The orchestrator determines:

1. what strategic question exists;
2. which memory is relevant;
3. which initiatives are affected;
4. which metrics matter;
5. which specialists are needed;
6. what evidence is missing;
7. whether simulation is appropriate;
8. whether human review is required.

---

# 71. Proactive Strategic Intelligence

TPG should continuously inspect available intelligence.

Example:

```text
Sales:
Repeated enterprise objection

Gmail:
Customer escalation

Slack:
Engineering discussion

Jira:
Multiple bugs

Analytics:
Adoption decline
```

TPG may infer:

> Multiple independent signals may indicate a strategic product issue.

This becomes a strategic investigation, not an automatic roadmap change.

---

# 72. Strategy Alerts

Alert levels:

### INFO

Interesting signal.

### ATTENTION

Potential strategic issue.

### IMPORTANT

Decision/review likely required.

### CRITICAL

Material strategic risk or objective failure.

---

# 73. Strategy Memory

TPG must remember:

* strategy versions;
* objectives;
* strategic bets;
* roadmap decisions;
* exclusions;
* assumptions;
* outcomes;
* lessons;
* failed bets.

This prevents organizational amnesia.

---

# 74. Strategy Learning

After each strategic bet:

```text
Hypothesis
↓
Investment
↓
Execution
↓
Outcome
↓
Learning
```

TPG should record:

> What did we learn about the market, customers, product, technology, and strategy?

---

# 75. Failed Bet Intelligence

A failed strategic bet must not disappear.

TPG should record:

```text
BET-007

Hypothesis:
...

Expected:
...

Actual:
...

Why:
...

Learning:
...

Future implication:
...
```

The lesson becomes part of organizational memory.

---

# 76. Strategy Anti-Patterns

TPG must detect:

### Roadmap-as-Strategy

Treating a list of features as strategy.

### Date Theater

Adding dates without evidence.

### Everything Is Priority

No meaningful prioritization.

### Strategy by Customer Request

Allowing individual customers to dictate direction.

### Strategy by Competitor

Copying competitors without strategic rationale.

### Strategy by Executive Preference

Unvalidated opinion becoming product direction.

### Infinite Roadmap

Planning too far into uncertain future.

### Output Optimization

Measuring shipped features rather than outcomes.

### Zombie Initiatives

Projects continuing despite loss of strategic relevance.

### Strategic Whiplash

Frequent strategy changes without explicit rationale.

---

# 77. Strategic Whiplash Detection

TPG should detect repeated major directional changes.

Example:

```text
Q1:
SMB Growth

Q2:
Enterprise

Q3:
B2C

Q4:
Platform

Q1:
Enterprise again
```

TPG should surface:

> "The strategic direction has changed materially four times within 12 months."

It should then identify the associated decisions and evidence.

---

# 78. Roadmap Commitment Integrity

TPG must differentiate:

> Internal target

from:

> Customer commitment

from:

> Contractual commitment.

A roadmap item must never automatically become a customer promise.

---

# 79. Client Communication Boundary

TPG can:

* prepare roadmap analysis;
* analyze client requirements;
* identify roadmap implications;
* draft employee communications.

TPG cannot:

* promise roadmap dates to clients;
* communicate roadmap commitments directly;
* negotiate roadmap scope;
* independently send roadmap updates externally.

---

# 80. Human Governance

Human approval is required for:

* strategic direction changes;
* major strategic bets;
* material budget allocation;
* major roadmap changes;
* product sunset;
* significant customer commitments;
* market entry;
* major architecture investment.

---

# 81. V1 Scope

TPG 1.0 must support strategy intelligence for the **individual user's Personal Workspace**.

The user may manually provide:

* company strategy;
* objectives;
* roadmap;
* product documents;
* metrics;
* business context.

Connected tools may enrich the model.

No shared corporate strategy workspace is required in V1.

---

# 82. Future Corporate Edition

Later:

```text
Personal Workspace
        +
Corporate Workspace
```

Corporate Edition may support:

* shared strategy;
* shared roadmap;
* organizational objectives;
* team ownership;
* permissions;
* executive dashboards;
* corporate governance;
* multi-user approvals.

Personal strategy and memory remain isolated unless explicitly shared.

---

# 83. Non-Functional Requirements

## Performance

Normal roadmap query:

**<10 seconds** where indexed data is available.

Deep strategy analysis:

**<60 seconds** target.

---

## Explainability

All material strategic observations must identify:

* evidence;
* assumptions;
* affected objects;
* confidence.

---

## Auditability

Strategy and roadmap changes must be versioned.

---

## Privacy

Zero cross-workspace strategy leakage.

---

## Integrity

No roadmap item may silently become a commitment.

---

# 84. Acceptance Criteria

### STRAT-AC-001

TPG can represent strategic themes.

### STRAT-AC-002

TPG can represent measurable strategic objectives.

### STRAT-AC-003

TPG can represent strategic bets.

### STRAT-AC-004

TPG can link strategic bets to initiatives.

### STRAT-AC-005

TPG can identify roadmap items without strategic alignment.

### STRAT-AC-006

TPG can identify objectives without roadmap support.

### STRAT-AC-007

TPG can detect strategic drift.

### STRAT-AC-008

TPG can identify roadmap dependencies.

### STRAT-AC-009

TPG can perform capacity-aware roadmap analysis where data exists.

### STRAT-AC-010

TPG can distinguish committed, target, planned and exploratory roadmap items.

### STRAT-AC-011

TPG can version strategy.

### STRAT-AC-012

TPG can perform strategy-change impact analysis.

### STRAT-AC-013

TPG can model hypothetical scenarios.

### STRAT-AC-014

TPG can identify strategic assumptions.

### STRAT-AC-015

TPG can identify weakening strategic assumptions.

### STRAT-AC-016

TPG can maintain a "not now / not doing" portfolio.

### STRAT-AC-017

TPG can connect strategy → roadmap → execution → outcomes.

### STRAT-AC-018

TPG can perform reverse traceability from execution back to strategy.

### STRAT-AC-019

TPG can detect strategic debt.

### STRAT-AC-020

TPG never independently communicates roadmap commitments to clients.

---

# 85. End-to-End Example

User asks:

> "We want to focus on enterprise customers next year. What should our roadmap look like?"

TPG should reason:

### Step 1 — Understand Strategy

```text
Strategic Direction:
Enterprise Expansion
```

### Step 2 — Define Objectives

Potential objectives:

* increase enterprise acquisition;
* improve enterprise retention;
* reduce enterprise implementation time.

### Step 3 — Analyze Current State

Read:

* CRM/sales data where available;
* customer emails;
* support;
* Jira;
* analytics;
* existing roadmap.

### Step 4 — Identify Gaps

Example:

```text
Enterprise onboarding:
Weak

Enterprise reporting:
Medium

Enterprise permissions:
Weak

Operational reliability:
Strong
```

### Step 5 — Identify Strategic Bets

```text
Bet A:
Enterprise Self-Service

Bet B:
Enterprise Governance

Bet C:
Enterprise Analytics
```

### Step 6 — Generate Initiatives

```text
SSO
RBAC
Audit Logs
Enterprise Reporting
Bulk Onboarding
API Improvements
Admin Controls
```

### Step 7 — Sequence Dependencies

```text
Identity
 ↓
Permissions
 ↓
Admin Controls
 ↓
Enterprise Self-Service
```

### Step 8 — Capacity Check

Identify what can realistically fit.

### Step 9 — Build Roadmap

```text
Q1:
Identity + Permissions Foundation

Q2:
Enterprise Admin + Onboarding

Q3:
Analytics + Automation

Q4:
Scale / Optimization
```

### Step 10 — Define Outcomes

Each quarter has measurable outcomes.

### Step 11 — Define Review Points

Strategy is reviewed against evidence.

This produces a **strategy-backed roadmap**, not simply a feature calendar.

---

# 86. Core Strategy Intelligence Loop

```text
                 STRATEGY
                    ↓
                OBJECTIVES
                    ↓
              STRATEGIC BETS
                    ↓
               OPPORTUNITIES
                    ↓
                DECISIONS
                    ↓
                ROADMAP
                    ↓
                EXECUTION
                    ↓
                 OUTCOMES
                    ↓
                 LEARNING
                    ↓
              STRATEGY UPDATE
                    │
                    └──────────────→
```

This loop allows TPG to continuously connect strategic intent with actual organizational behavior.

---

# 87. Design Freeze

The following are **non-negotiable decisions** for TPG 1.0:

1. Strategy is distinct from roadmap.
2. Roadmap is distinct from backlog.
3. Strategic objectives must be outcome-oriented.
4. Strategic bets must be treated as hypotheses.
5. Strategic assumptions must be explicitly stored.
6. Roadmap items must have strategic context where applicable.
7. TPG must identify strategic orphans.
8. TPG must identify strategic gaps.
9. TPG must identify strategic debt.
10. TPG must detect strategy drift.
11. Roadmaps must be capacity-aware when data exists.
12. Roadmaps must be dependency-aware.
13. Roadmaps must distinguish commitment levels.
14. Speculative dates must never be presented as guaranteed.
15. Strategy must be versioned.
16. Strategy changes must support impact analysis.
17. TPG must support scenario planning.
18. TPG must support portfolio analysis.
19. TPG must preserve deliberate "not doing" decisions.
20. TPG must learn from failed strategic bets.
21. Strategy, roadmap and execution must be traceable.
22. Reverse traceability must be supported.
23. TPG must not automatically change strategy based on a single signal.
24. External/client communication remains outside TPG's autonomous authority.
25. V1 operates inside the user's private Personal Workspace.
26. Internal strategy specialists remain invisible behind the single TPG identity.

---

# 88. Relationship to the TPG Architecture

The first seven PRDs now form a coherent intelligence stack:

```text
PRD-0001
MASTER PRODUCT CHARTER
        │
        ▼
PRD-0002
MEMORY + KNOWLEDGE GRAPH
        │
        ▼
PRD-0003
IDENTITY + PERSONAL WORKSPACE
        │
        ▼
PRD-0004
CONNECTOR INTELLIGENCE
        │
        ▼
PRD-0005
REQUIREMENT INTELLIGENCE
        │
        ▼
PRD-0006
DECISION ENGINE
        │
        ▼
PRD-0007
STRATEGY + ROADMAP + PORTFOLIO
```

The resulting TPG capability is now:

> **Observe the organization → understand its problems → reason about decisions → understand strategic direction → determine how investments should be sequenced → monitor whether execution remains aligned.**

---

# 89. Final Product Definition

With PRD-0007, TPG is no longer merely a:

**Product Decision Assistant.**

It becomes a:

> **Persistent Strategic Product Executive.**

Its job is to continuously maintain the relationship between:

**What the organization says it wants to achieve**

and

**What the organization is actually building.**

The central TPG question evolves from:

> **"Should we build this?"**

to:

> **"Does this investment belong in the strategy, and if so, where, when, why, and at what opportunity cost?"**

That is the foundation for the next layer:

**PRD-0008 — Product Specification, PRD Generation & Requirements-to-Execution Engine.**
