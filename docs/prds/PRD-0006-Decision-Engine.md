# PRD-0006 — Product Decision Engine, Strategic Reasoning & Prioritization Framework

**Product:** TPG 1.0 — The Product Guy  
**Organization:** SkynetOrg  
**Document ID:** PRD-0006  
**Status:** Design Specification  
**Priority:** P0 — Core Intelligence  
**Depends On:** PRD-0001, PRD-0002, PRD-0003, PRD-0004, PRD-0005  
**Primary Interface:** ChatGPT  
**Architecture:** Internal Specialist Agents + Unified TPG Identity  

---

# 1. Executive Summary

TPG must not merely collect requirements or generate PRDs.

It must be capable of answering the much harder product question:

> **"Given everything we know, what should we do?"**

PRD-0005 established the **Requirement Intelligence and Product Reasoning Engine**.

PRD-0006 introduces the **Product Decision Engine (PDE)**.

The Product Decision Engine converts validated requirements, evidence, business objectives, strategic context, constraints, product metrics, customer intelligence, engineering realities, and historical decisions into **structured product decisions**.

The engine must be capable of:

* determining whether something should be built;
* determining why it should be built;
* determining when it should be built;
* comparing alternative solutions;
* identifying strategic alignment;
* identifying opportunity cost;
* prioritizing competing initiatives;
* detecting conflicts between initiatives;
* identifying dependencies;
* recommending MVP scope;
* identifying risks;
* calculating confidence;
* explaining the reasoning behind decisions;
* preserving the decision and its rationale permanently;
* revisiting decisions when new evidence arrives.

TPG must therefore behave less like:

> "AI that generates product documents"

and more like:

> **"A permanent Product Executive that continuously evaluates what the organization should do next."**

---

# 2. Product Principle

## 2.1 Core Principle

> **TPG does not optimize for activity. TPG optimizes for product outcomes.**

A backlog containing 500 tickets does not mean the organization has 500 valuable things to build.

The PDE must continuously distinguish between:

**Requests → Problems → Opportunities → Strategic choices → Investments → Outcomes**

---

# 3. Decision Philosophy

TPG must follow:

> **Evidence → Context → Strategic Fit → Options → Trade-offs → Decision → Commitment → Measurement**

It must never blindly execute:

> Request → Feature → Jira Ticket

---

# 4. Decision Hierarchy

The engine must reason through the following hierarchy:

```text
Company Strategy
       ↓
Strategic Objectives
       ↓
Product Objectives
       ↓
Customer / User Problems
       ↓
Opportunities
       ↓
Initiatives
       ↓
Solution Options
       ↓
Requirements
       ↓
Execution
       ↓
Outcomes
```

Every major decision should be traceable upward and downward through this hierarchy.

---

# 5. Decision Object

Every material product decision must become a persistent `Decision` entity.

## 5.1 Decision Schema

```json
{
  "decision_id": "DEC-000123",
  "workspace_id": "WS-001",
  "title": "Build automated vendor reconciliation",
  "decision_type": "PRODUCT_INVESTMENT",
  "status": "APPROVED",
  "initiative_id": "INIT-0042",
  "problem_id": "PROB-0081",

  "decision_question": "...",

  "context": {},
  "evidence": [],
  "assumptions": [],
  "constraints": [],

  "options": [],

  "evaluation_framework": {},
  "tradeoffs": [],

  "recommendation": {},
  "confidence": 0.87,

  "strategic_alignment": {},
  "expected_outcomes": [],

  "risks": [],
  "dependencies": [],

  "decision_owner": "USER",
  "approval_required": true,

  "decision_date": "...",
  "review_date": "...",

  "supersedes": null,
  "superseded_by": null
}
```

---

# 6. Decision Types

The PDE must classify decisions.

| Type               | Example                               |
| ------------------ | ------------------------------------- |
| PRODUCT_INVESTMENT | Build a new product                   |
| FEATURE            | Add a capability                      |
| PRIORITIZATION     | Move initiative up/down               |
| MVP_SCOPE          | Define initial release                |
| ARCHITECTURE       | Choose technical approach             |
| UX                 | Select experience                     |
| PRICING            | Pricing decision                      |
| MARKET             | Enter a market                        |
| CUSTOMER           | Support customer-specific requirement |
| BUILD_VS_BUY       | Build internally or purchase          |
| RESOURCE           | Allocate engineering capacity         |
| TIMING             | Launch now/later                      |
| DEPRECATION        | Remove capability                     |
| EXPERIMENT         | Run experiment                        |
| STRATEGY           | Change product direction              |
| COMPLIANCE         | Respond to regulatory requirement     |
| OPERATIONAL        | Change operational process            |

---

# 7. Decision Lifecycle

```text
QUESTION
   ↓
CONTEXT COLLECTION
   ↓
EVIDENCE COLLECTION
   ↓
PROBLEM VALIDATION
   ↓
STRATEGIC ALIGNMENT
   ↓
OPTION GENERATION
   ↓
OPTION EVALUATION
   ↓
TRADE-OFF ANALYSIS
   ↓
RECOMMENDATION
   ↓
HUMAN REVIEW
   ↓
APPROVAL
   ↓
EXECUTION
   ↓
OUTCOME MEASUREMENT
   ↓
DECISION REVIEW
```

---

# 8. Decision States

```text
DRAFT
UNDERSTANDING
EVIDENCE_COLLECTION
READY_FOR_EVALUATION
EVALUATING
RECOMMENDATION_READY
AWAITING_APPROVAL
APPROVED
REJECTED
DEFERRED
SUPERSEDED
EXECUTING
MEASURING
REVIEW_REQUIRED
CLOSED
```

---

# 9. Decision Question Detection

TPG must detect implicit decision questions.

Example:

User says:

> "Engineering wants to build a separate reporting service."

TPG should internally identify:

```text
Decision Question:
Should the organization invest in a separate reporting service?
```

Then investigate:

* What problem does it solve?
* Who experiences it?
* Current workaround?
* Frequency?
* Business impact?
* Existing capabilities?
* Technical constraints?
* Strategic relevance?
* Alternative solutions?
* Build cost?
* Opportunity cost?
* Long-term implications?

---

# 10. Strategic Context Engine

A decision cannot be evaluated without understanding the organization's strategic direction.

TPG must maintain:

```text
Company Strategy
├── Mission
├── Vision
├── Strategic Themes
├── Annual Objectives
├── Product Objectives
├── Revenue Objectives
├── Customer Objectives
├── Operational Objectives
└── Technical Objectives
```

---

# 11. Strategic Objective Object

```json
{
  "objective_id": "OBJ-001",
  "name": "Increase enterprise retention",
  "description": "...",
  "time_horizon": "12_MONTHS",
  "target_metric": "NET_REVENUE_RETENTION",
  "target_value": 115,
  "priority": "HIGH",
  "status": "ACTIVE"
}
```

---

# 12. Strategic Alignment Analysis

For every significant initiative TPG should evaluate:

### 12.1 Alignment Dimensions

| Dimension       | Question                            |
| --------------- | ----------------------------------- |
| Strategic Fit   | Does it advance company strategy?   |
| Customer Value  | Does it solve a meaningful problem? |
| Business Value  | Does it affect business outcomes?   |
| Product Fit     | Does it strengthen the product?     |
| Market Fit      | Does it support market positioning? |
| Operational Fit | Can the organization support it?    |
| Technical Fit   | Does it fit architecture?           |
| Timing          | Is now the correct time?            |

---

# 13. Strategic Alignment Output

TPG must never simply say:

> "This aligns with strategy."

Instead:

```text
Strategic Alignment

Objective:
Increase enterprise retention

Relationship:
Strong

Reason:
The initiative addresses recurring operational failures
identified in 7 enterprise accounts.

Expected contribution:
Reduce customer-facing operational incidents.

Evidence:
- 7 customer incidents
- 19 support tickets
- 3 churn-risk accounts
- 14% increase in operational escalations
```

---

# 14. Evidence Weighting

Not all evidence is equal.

TPG must distinguish:

### Strong Evidence

* production analytics;
* repeated customer behavior;
* transaction data;
* validated experiments;
* production incidents;
* multiple independent customer reports.

### Medium Evidence

* customer interviews;
* sales feedback;
* support tickets;
* stakeholder observations;
* survey responses.

### Weak Evidence

* isolated requests;
* anecdotal comments;
* assumptions;
* executive opinions without supporting evidence.

---

# 15. Evidence Independence

TPG must detect correlated evidence.

Example:

10 customer requests all originate from one account.

TPG must not interpret:

> 10 requests = 10 independent signals.

Instead:

```text
Independent Customer Signals: 1
Reported Instances: 10
```

---

# 16. Confidence Model

Decision confidence must be calculated from:

```text
Evidence Quality
+
Evidence Diversity
+
Evidence Recency
+
Problem Validation
+
Strategic Clarity
+
Metric Availability
+
Solution Uncertainty
+
Assumption Load
```

Confidence categories:

|     Score | Level     |
| --------: | --------- |
| 0.90–1.00 | Very High |
| 0.75–0.89 | High      |
| 0.55–0.74 | Medium    |
| 0.30–0.54 | Low       |
|     <0.30 | Very Low  |

The confidence score must never be presented as mathematical certainty.

TPG must explain *why* confidence is high or low.

---

# 17. Assumption Register

Every important decision must maintain an assumption list.

Example:

```text
A-001:
Enterprise customers will continue using the workflow.

Confidence: Medium

A-002:
Engineering effort is approximately 4 weeks.

Confidence: Low

A-003:
Automation can reduce manual processing by >50%.

Confidence: Medium
```

---

# 18. Unknowns

TPG must explicitly distinguish:

```text
KNOWN
ASSUMED
UNKNOWN
CONTESTED
```

Example:

| Item                        | State             |
| --------------------------- | ----------------- |
| Current processing time     | KNOWN             |
| Engineering effort          | UNKNOWN           |
| Customer willingness to pay | UNKNOWN           |
| Problem frequency           | MEDIUM CONFIDENCE |
| Strategic importance        | KNOWN             |

TPG must never silently convert UNKNOWN into ASSUMED.

---

# 19. Option Generation Engine

Before recommending a solution, TPG should generate alternatives.

Minimum option categories:

```text
Option A — Do Nothing
Option B — Improve Existing Workflow
Option C — Build Minimal Solution
Option D — Build Full Solution
Option E — Buy / Integrate
Option F — Experiment First
Option G — Process / Operational Change
```

Not every decision requires every option.

---

# 20. Do-Nothing Analysis

The PDE must always consider the cost of inaction where relevant.

It should analyze:

* continued operational cost;
* customer impact;
* revenue risk;
* churn risk;
* technical debt;
* opportunity cost;
* regulatory exposure;
* strategic delay.

Example:

```text
Cost of Inaction

Current manual process:
~300 hours/month

Estimated annual operational burden:
~3,600 hours

Additional risk:
High

Confidence:
Medium
```

---

# 21. Opportunity Cost Engine

Every investment consumes finite resources.

TPG must evaluate:

```text
Initiative A
vs
Initiative B
vs
Initiative C
```

using:

* engineering capacity;
* design capacity;
* product capacity;
* operational capacity;
* capital;
* management attention;
* launch complexity;
* strategic timing.

---

# 22. Capacity Model

TPG must maintain available capacity when data is available.

Example:

```text
Engineering Capacity
--------------------
Team: Platform
Available: 320 hours
Committed: 240 hours
Available: 80 hours
```

If an initiative requires:

```text
Estimated effort: 120 hours
```

TPG must detect:

> Capacity conflict.

---

# 23. Prioritization Framework

TPG must support multiple prioritization models.

## Supported Models

1. RICE
2. MoSCoW
3. Value vs Effort
4. Opportunity Scoring
5. Cost of Delay
6. Strategic Alignment
7. Customer Impact
8. Revenue Impact
9. Risk Reduction
10. Technical Risk
11. Custom organizational framework

TPG must **not automatically use RICE for everything**.

---

# 24. RICE

When appropriate:

```text
RICE =
Reach × Impact × Confidence
---------------------------
Effort
```

TPG must show the inputs and assumptions.

Example:

```text
Reach: 1,000
Impact: 2
Confidence: 0.8
Effort: 4

RICE = 400
```

But TPG must explain:

> "RICE is being used because the initiatives have comparable measurable reach and effort."

---

# 25. Cost of Delay

For time-sensitive initiatives:

```text
Cost of Delay =
Lost Revenue
+
Customer Impact
+
Operational Cost
+
Risk Exposure
+
Strategic Delay
```

TPG must identify when timing matters.

---

# 26. Strategic Priority Model

TPG should maintain:

```text
Priority =
Customer Value
+
Business Value
+
Strategic Alignment
+
Urgency
+
Risk Reduction
+
Evidence Strength
-
Effort
-
Complexity
-
Opportunity Cost
```

This is **not necessarily a universal numeric formula**.

The engine may use qualitative reasoning when numeric data is insufficient.

---

# 27. Prioritization Anti-Patterns

TPG must detect:

### HiPPO

Highest Paid Person's Opinion.

### Loudest Customer

One large customer dominating roadmap decisions.

### Recency Bias

Recent request receives disproportionate priority.

### Sunk Cost

Continuing investment because resources have already been spent.

### Feature Factory

Optimizing ticket throughput instead of outcomes.

### Strategic Drift

Building useful things unrelated to strategy.

### Vanity Metrics

Prioritizing based on metrics that do not represent business value.

### Engineering Convenience Bias

Prioritizing easy engineering tasks over meaningful problems.

---

# 28. Opportunity Scoring

TPG may evaluate:

```text
Importance
+
Current Satisfaction Gap
```

to identify opportunities.

Example:

| Opportunity              | Importance | Satisfaction | Gap |
| ------------------------ | ---------: | -----------: | --: |
| Automated reconciliation |          9 |            3 |   6 |
| Custom dashboard         |          6 |            5 |   1 |

The engine should explain that a large gap may indicate opportunity, not automatically imply that the feature should be built.

---

# 29. Initiative Portfolio

TPG must maintain a portfolio view.

```text
PORTFOLIO

Growth
├── Initiative A
├── Initiative B

Retention
├── Initiative C

Operational Efficiency
├── Initiative D

Technical Foundation
├── Initiative E

Compliance
├── Initiative F
```

This enables strategic balance.

---

# 30. Portfolio Balance

TPG should detect excessive concentration.

Example:

```text
Current Portfolio

Growth: 70%
Retention: 10%
Operational: 5%
Platform: 15%
```

TPG may state:

> "The current portfolio is heavily concentrated in growth initiatives and has limited investment in operational reliability."

It must then show the evidence supporting the observation.

---

# 31. Initiative Dependencies

TPG must construct a dependency graph.

Example:

```text
Authentication
     ↓
Identity Service
     ↓
Permission Engine
     ↓
Corporate Workspace
     ↓
Team Collaboration
```

If a downstream initiative is proposed before its dependency exists:

> Dependency Risk Detected.

---

# 32. Dependency Types

* Technical
* Product
* Operational
* Regulatory
* Data
* Vendor
* Organizational
* Customer
* Financial
* Timing

---

# 33. Conflict Detection

TPG must identify:

### Strategy conflicts

Initiative conflicts with strategic objective.

### Resource conflicts

Two initiatives require the same team.

### Product conflicts

Features create contradictory experiences.

### Architecture conflicts

Solution contradicts technical direction.

### Customer conflicts

One customer-specific requirement harms broader product strategy.

### Metric conflicts

Optimizing one KPI harms another.

Example:

```text
Increasing trip acceptance rate
may increase driver cancellation rate.

Potential KPI conflict detected.
```

---

# 34. Customer-Specific Request Analysis

A customer request must pass through:

```text
Customer Request
       ↓
Customer Problem
       ↓
Problem Frequency
       ↓
Cross-Customer Occurrence
       ↓
Strategic Fit
       ↓
Commercial Value
       ↓
Productization Potential
       ↓
Decision
```

TPG must never automatically convert:

> "Client X wants this"

into:

> "Product must build this."

---

# 35. Productization Test

TPG should ask:

1. Does the problem occur across customers?
2. Is it central to the product?
3. Does solving it improve product differentiation?
4. Can it be generalized?
5. Will implementation create long-term product debt?
6. Is it contractual?
7. Is the customer willing to fund customization?
8. Can the capability become a reusable platform feature?

---

# 36. Build vs Buy Engine

For major capabilities:

```text
BUILD
BUY
PARTNER
INTEGRATE
ACQUIRE
DEFER
```

Evaluate:

| Dimension                 | Question                    |
| ------------------------- | --------------------------- |
| Strategic Differentiation | Is this core IP?            |
| Cost                      | Total cost?                 |
| Time                      | Time to production?         |
| Control                   | Required level of control?  |
| Vendor Risk               | Dependency risk?            |
| Scalability               | Can it scale?               |
| Security                  | Data/security implications? |
| Maintenance               | Long-term burden?           |

---

# 37. MVP Decision Engine

TPG must distinguish:

```text
MVP
V1
V1.1
V2
Future
```

MVP is not:

> "Everything we can build quickly."

MVP means:

> **Minimum product capability required to validate the core value proposition.**

---

# 38. MVP Scope Classification

Every requirement should receive:

```text
MUST_HAVE
SHOULD_HAVE
COULD_HAVE
NOT_NOW
```

And the reason must be recorded.

Example:

```text
Requirement:
Advanced analytics dashboard

Decision:
NOT_NOW

Reason:
Not required to validate the core workflow.
```

---

# 39. Experiment-First Decision

TPG should recommend experimentation when:

* problem exists but solution uncertainty is high;
* willingness to pay is uncertain;
* user behavior is uncertain;
* engineering investment is significant;
* market demand is uncertain.

Possible experiments:

* prototype;
* fake door;
* concierge MVP;
* manual workflow;
* A/B test;
* pilot;
* customer interview;
* landing page;
* shadow mode.

---

# 40. Decision Tree

TPG should use a decision tree similar to:

```text
Is the problem real?
        |
       NO → STOP / REJECT
        |
       YES
        ↓
Is it strategically relevant?
        |
       NO → DEFER / DECLINE
        |
       YES
        ↓
Is evidence sufficient?
        |
       NO → RESEARCH / EXPERIMENT
        |
       YES
        ↓
Are multiple solutions viable?
        |
       YES → COMPARE OPTIONS
        |
       NO
        ↓
Can MVP validate value?
        |
       YES → MVP
        |
       NO
        ↓
FULL INVESTMENT ANALYSIS
```

---

# 41. Decision Recommendation Format

TPG should provide:

```text
DECISION BRIEF

Question
Should we build X?

Context
...

Problem
...

Evidence
...

Strategic Alignment
...

Options
...

Trade-offs
...

Risks
...

Dependencies
...

Recommendation
...

Why
...

What would change the decision
...

Confidence
...

Next Action
...
```

---

# 42. "What Would Change My Mind?" Section

Every significant recommendation should include:

```text
Decision Sensitivity

This recommendation would change if:

1. Engineering effort exceeds 12 weeks.
2. Customer adoption is below 20%.
3. The strategic objective changes.
4. A cheaper third-party solution becomes available.
```

This makes decisions dynamic rather than permanent assumptions.

---

# 43. Decision Reversibility

TPG must classify decisions:

### Easily Reversible

Can be changed cheaply.

### Moderately Reversible

Requires moderate investment.

### Hard to Reverse

Creates significant technical, financial, contractual or organizational commitment.

High-reversibility decisions can be made faster.

Low-reversibility decisions require deeper analysis.

---

# 44. Decision Speed Framework

TPG should balance:

```text
Decision Importance
×
Decision Irreversibility
×
Uncertainty
```

High uncertainty + high irreversibility:

> Deep analysis required.

Low uncertainty + highly reversible:

> Move quickly.

---

# 45. Strategic Horizon

TPG should distinguish:

```text
NOW
0–3 months

NEAR
3–12 months

FUTURE
12+ months
```

An initiative may be strategically valuable but not appropriate **now**.

---

# 46. Roadmap Reasoning

TPG should construct roadmap recommendations based on:

```text
Strategic Objective
      ↓
Outcome
      ↓
Opportunity
      ↓
Initiative
      ↓
Dependency
      ↓
Sequence
      ↓
Execution
```

Roadmap should not simply be:

> Q1: Feature A
> Q2: Feature B

It should be:

> Q1: Remove operational bottleneck → improve processing reliability
> Q2: Automate workflow → reduce manual effort
> Q3: Expand capability → improve enterprise scalability

---

# 47. Outcome-Based Roadmap

Each roadmap item must contain:

```text
Initiative
Objective
Expected Outcome
Success Metric
Target
Dependencies
Estimated Effort
Confidence
Owner
Review Date
```

---

# 48. Outcome Hypothesis

Every significant investment should have:

```text
We believe that:
[solution]

For:
[target users]

Will:
[behavior change]

Resulting in:
[business/product outcome]

Measured by:
[metric]
```

---

# 49. KPI Selection

TPG must distinguish:

### Input Metrics

Engineering hours.

### Output Metrics

Features shipped.

### Behavioral Metrics

User adoption.

### Outcome Metrics

Revenue, retention, conversion, efficiency.

### Business Metrics

ARR, margin, churn, profitability.

TPG should prioritize outcome metrics where appropriate.

---

# 50. North Star Relationship

TPG should understand:

```text
North Star Metric
      ↓
Supporting Metrics
      ↓
Initiative Outcomes
      ↓
Feature Metrics
```

A feature should not be considered successful merely because it shipped.

---

# 51. Decision → KPI Linkage

Every major decision must be linked to one or more measurable outcomes.

Example:

```text
Decision:
Automate vendor reconciliation

Expected Outcome:
Reduce manual reconciliation effort

Primary KPI:
Hours spent per 100 transactions

Target:
-60%

Review:
90 days after launch
```

---

# 52. Post-Decision Review

TPG must revisit major decisions.

Review questions:

1. Was the decision correct?
2. Did assumptions hold?
3. Did expected outcomes occur?
4. What surprised us?
5. What evidence changed?
6. Should we continue?
7. Should we expand?
8. Should we stop?

---

# 53. Decision Learning

TPG must learn from previous decisions.

Example:

```text
Historical Decision Pattern

Previous 6 initiatives estimated at <4 weeks
actually averaged 7.2 weeks.

Planning adjustment:
Increase confidence penalty for similar estimates.
```

The system must distinguish:

> Historical pattern

from:

> Universal truth.

---

# 54. Decision Memory

TPG must preserve:

```text
Decision
+
Context
+
Evidence
+
Alternatives
+
Reasoning
+
Assumptions
+
Approval
+
Outcome
+
Lessons
```

Future TPG responses must be able to answer:

> "Why did we decide this six months ago?"

---

# 55. Decision Contradiction Detection

If a new proposal conflicts with an earlier decision:

```text
Previous Decision:
Do not build custom reporting for individual customers.

New Request:
Customer X requires custom reporting.

Conflict detected.
```

TPG should surface:

> "This appears to conflict with Decision DEC-0042."

Then explain the differences in context.

---

# 56. Decision Supersession

Decisions should not be silently overwritten.

Instead:

```text
DEC-001
   ↓
SUPERSEDED BY
   ↓
DEC-014
```

Both decisions remain historically accessible.

---

# 57. Decision Audit Trail

Record:

```text
Created
Evidence Added
Option Added
Recommendation Generated
User Reviewed
Approved
Rejected
Modified
Superseded
Outcome Measured
Closed
```

---

# 58. Human Approval Boundary

TPG can:

* analyze;
* recommend;
* prioritize;
* draft;
* model;
* simulate;
* create decision briefs;
* prepare roadmap proposals.

TPG cannot independently:

* commit company budget;
* approve major strategic investments;
* promise delivery dates externally;
* change corporate strategy;
* make contractual commitments;
* send client communications;
* represent the organization externally.

Human approval remains mandatory for material organizational decisions.

---

# 59. Internal Specialist Architecture

The PDE should internally use specialist reasoning modules.

```text
                    TPG
                     │
             Decision Orchestrator
                     │
 ┌───────────┬───────┼────────┬───────────┐
 │           │       │        │           │
Strategy   Evidence  Value   Risk      Portfolio
Agent      Agent     Agent   Agent      Agent
 │           │       │        │           │
 └───────────┴───────┼────────┴───────────┘
                     │
             Decision Synthesizer
                     │
                  TPG Output
```

These specialists remain invisible to the user.

The user sees only:

> **TPG**

---

# 60. Decision Orchestrator

The orchestrator determines:

1. What decision is being made?
2. Which evidence is required?
3. Which specialists should reason?
4. Which framework is appropriate?
5. What uncertainty exists?
6. Whether human clarification is required.
7. Whether a recommendation can be generated.

---

# 61. Framework Selection Engine

TPG should select frameworks dynamically.

Example:

### Feature Prioritization

→ RICE / Value-Effort

### Regulatory Requirement

→ Compliance urgency / risk

### Build vs Buy

→ TCO / strategic differentiation

### Major Architecture

→ Reversibility / technical risk / long-term cost

### Customer Request

→ Productization / customer value / strategic fit

### Experiment

→ Hypothesis / uncertainty reduction

---

# 62. Never-Force-Framework Rule

TPG must not manufacture numeric scores when data quality is poor.

Instead:

```text
Quantitative evaluation unavailable.

Reason:
Reach and effort data are insufficient.

Using qualitative trade-off analysis instead.
```

This is mandatory.

---

# 63. Decision Quality Score

TPG may internally assess decision quality using:

```text
Evidence Completeness
Problem Clarity
Strategic Clarity
Option Coverage
Trade-off Quality
Risk Coverage
Assumption Transparency
Outcome Definition
```

This score is an internal diagnostic, not a statement that a decision is objectively correct.

---

# 64. Decision Readiness

A decision becomes:

### NOT READY

Critical unknowns remain.

### CONDITIONALLY READY

Decision can proceed with explicit assumptions.

### READY

Evidence and context are sufficient.

### EXECUTIVE REVIEW

High-impact / irreversible decision requiring human approval.

---

# 65. Decision Escalation

TPG should escalate when:

* financial impact is material;
* strategic direction changes;
* customer commitments are involved;
* legal/compliance implications exist;
* architecture becomes difficult to reverse;
* organizational structure changes;
* multiple strategic objectives conflict.

---

# 66. Decision Simulation

For major decisions TPG may simulate scenarios.

Example:

```text
Scenario A:
Build internally

Cost: ₹20L
Time: 5 months
Control: High

Scenario B:
Buy SaaS

Cost: ₹8L/year
Time: 1 month
Control: Medium

Scenario C:
Partner

Cost: ₹12L/year
Time: 2 months
Control: Medium
```

TPG should expose assumptions behind every scenario.

---

# 67. Sensitivity Analysis

TPG should identify variables that materially change the recommendation.

Example:

```text
Decision is highly sensitive to:

Engineering effort
Customer adoption
Annual contract value
Vendor pricing
```

This tells the user where additional research is valuable.

---

# 68. Opportunity Cost Statement

Every major recommendation should answer:

> "What are we not doing because we are doing this?"

Example:

```text
Choosing Initiative A consumes approximately
40% of Platform capacity for two months.

Likely displaced initiatives:
- Reporting improvements
- API modernization
```

---

# 69. Decision Communication

TPG should be able to generate:

### Executive Version

One-page decision brief.

### Product Version

Detailed product reasoning.

### Engineering Version

Technical trade-offs.

### Design Version

User/UX implications.

### Operations Version

Operational impact.

### Jira Version

Execution-ready work.

Same decision. Different communication layers.

---

# 70. Decision-to-Execution Bridge

Approved decision:

```text
Decision
   ↓
Initiative
   ↓
PRD
   ↓
Requirements
   ↓
Epics
   ↓
Stories
   ↓
Acceptance Criteria
   ↓
Execution
   ↓
Metrics
```

This creates end-to-end traceability.

---

# 71. Decision-to-PRD Gate

A PRD should not be generated automatically merely because someone asks:

> "Write a PRD."

TPG should determine:

```text
Problem validated?
Evidence sufficient?
Strategic alignment established?
Solution direction understood?
Scope defined?
Success metrics defined?
```

If not:

> Enter Discovery Mode.

---

# 72. Proactive Decision Intelligence

TPG should proactively identify decision opportunities.

Example:

Across Gmail + Slack + Jira:

```text
23 mentions
8 support tickets
4 engineering discussions
3 customer escalations

Common issue detected:
Vendor trip reconciliation.

Potential product decision required.
```

TPG can surface:

> "I found a recurring product issue that may warrant a decision review."

---

# 73. Decision Trigger Types

* repeated requirement;
* KPI deterioration;
* customer escalation;
* increasing operational cost;
* strategic change;
* competitor movement;
* engineering bottleneck;
* recurring incident;
* deadline;
* dependency change;
* regulatory change;
* resource constraint.

---

# 74. Silent Intelligence

TPG should not constantly interrupt the user.

Use:

### Silent

For low-impact observations.

### Suggested

For potentially useful decisions.

### Immediate

For urgent/high-impact decisions.

Example:

```text
Low:
"3 similar requests detected."

Medium:
"This appears to be becoming a recurring product problem."

High:
"Current production issue may create material customer impact."
```

---

# 75. Decision Notifications

Notifications should include:

```text
What happened
Why it matters
Evidence
Recommended next step
Urgency
```

Never:

> "You should definitely build this."

Prefer:

> "Evidence suggests this may warrant prioritization. Here is the supporting evidence and trade-off analysis."

---

# 76. Natural Language Queries

TPG must support:

> "What should we build next?"

> "What are our highest-value opportunities?"

> "Why isn't this feature prioritized?"

> "Should we build this?"

> "Should we buy this?"

> "What are we currently over-investing in?"

> "What are we ignoring?"

> "What decisions are blocked?"

> "Which decisions are based on weak evidence?"

> "What changed our product strategy?"

> "What did we decide about this six months ago?"

> "What assumptions are most dangerous?"

> "What would happen if we don't build this?"

---

# 77. Explainability

Every recommendation must be explainable.

TPG should be able to answer:

> "Why?"

> "Based on what?"

> "What alternatives did you consider?"

> "What assumptions are you making?"

> "What would change your recommendation?"

> "Who requested this?"

> "What customer evidence exists?"

> "What does engineering think?"

> "What is the opportunity cost?"

---

# 78. Source Traceability

Every factual claim should map to evidence.

Example:

```text
Claim:
This issue affects enterprise customers.

Evidence:
- Client A — 4 incidents
- Client B — 2 incidents
- Client C — 3 support tickets
```

Sources should link back to connector-origin records where available.

---

# 79. Privacy

All decision reasoning must obey workspace boundaries.

```text
User A Workspace
      X
User B Workspace
```

No cross-workspace decision intelligence in V1.

---

# 80. Client Boundary

The PDE must obey the constitutional client rule.

TPG may:

* analyze client requests;
* prioritize client problems;
* prepare internal recommendations;
* draft employee responses;
* create internal PRDs;
* create internal Jira work.

TPG must never:

* independently communicate decisions to clients;
* promise roadmap commitments;
* negotiate scope;
* send proposals;
* make contractual commitments.

---

# 81. Failure Scenarios

## F-001 — Insufficient Evidence

**Scenario:** User asks whether to build a feature.

**Expected behavior:**

TPG identifies insufficient evidence and asks targeted questions or proposes research.

---

## F-002 — Conflicting Evidence

**Scenario:** Customers report opposite preferences.

**Expected behavior:**

TPG exposes the conflict rather than averaging it away.

---

## F-003 — Strategic Conflict

**Scenario:** High-value customer request conflicts with product strategy.

**Expected behavior:**

Surface the conflict and evaluate alternatives.

---

## F-004 — Single-Customer Bias

**Scenario:** One customer represents most evidence.

**Expected behavior:**

Flag evidence concentration.

---

## F-005 — Weak Quantitative Data

**Scenario:** RICE cannot be calculated reliably.

**Expected behavior:**

Switch to qualitative analysis.

---

## F-006 — Unknown Engineering Effort

**Scenario:** Engineering estimate unavailable.

**Expected behavior:**

Mark effort UNKNOWN rather than inventing it.

---

## F-007 — Historical Decision Conflict

**Scenario:** New requirement contradicts an earlier decision.

**Expected behavior:**

Surface historical decision and ask whether context has changed.

---

## F-008 — High-Irreversibility Decision

**Scenario:** Major architecture change.

**Expected behavior:**

Increase analysis depth and require human approval.

---

## F-009 — Outcome Failure

**Scenario:** Initiative launched but KPI does not improve.

**Expected behavior:**

Trigger decision review.

---

## F-010 — Client Commitment Risk

**Scenario:** User asks TPG to promise a feature to a client.

**Expected behavior:**

TPG may draft the response but must not send or independently commit.

---

# 82. Non-Functional Requirements

## Performance

Normal decision query:

**Target:** <10 seconds where cached evidence exists.

Deep decision analysis:

**Target:** <60 seconds.

---

## Reliability

Decision records must never be silently lost.

---

## Explainability

100% of material recommendations must have:

* evidence;
* assumptions;
* rationale;
* confidence;
* alternatives.

---

## Auditability

100% of approved decisions must have immutable history.

---

## Privacy

0 cross-workspace leakage.

---

## Client Autonomy

0 autonomous external client communication.

---

# 83. Acceptance Criteria

## PDE-AC-001

Given a validated requirement, TPG can determine whether a product decision is required.

## PDE-AC-002

TPG can generate multiple solution alternatives.

## PDE-AC-003

TPG can evaluate strategic alignment.

## PDE-AC-004

TPG can detect opportunity cost.

## PDE-AC-005

TPG can detect initiative dependencies.

## PDE-AC-006

TPG can detect conflicting decisions.

## PDE-AC-007

TPG can select an appropriate prioritization framework.

## PDE-AC-008

TPG refuses to fabricate missing quantitative inputs.

## PDE-AC-009

TPG preserves assumptions separately from facts.

## PDE-AC-010

TPG can generate a decision brief.

## PDE-AC-011

TPG can link decisions to initiatives, requirements, PRDs and KPIs.

## PDE-AC-012

TPG can revisit historical decisions.

## PDE-AC-013

TPG can identify decisions requiring human approval.

## PDE-AC-014

TPG cannot autonomously communicate material decisions to clients.

## PDE-AC-015

TPG can explain what evidence would change a recommendation.

---

# 84. Example End-to-End Scenario

User says:

> "Sales says every enterprise customer wants custom dashboards. Should we build a dashboard builder?"

TPG should not immediately produce:

> "Yes, build dashboard builder."

Instead:

### Step 1 — Detect Decision

```text
Should we build a generalized dashboard builder?
```

### Step 2 — Search Memory

Find:

* customer requests;
* support tickets;
* existing dashboards;
* product strategy;
* analytics usage;
* sales pipeline;
* churn information.

### Step 3 — Validate Problem

Determine:

* who needs dashboards;
* what decisions dashboards support;
* what information is missing;
* whether customers need customization or simply better reporting.

### Step 4 — Generate Options

```text
A. Build dashboard builder
B. Improve existing standard dashboards
C. Add configurable widgets
D. Provide export/API
E. Offer managed reporting
F. Pilot with 3 customers
```

### Step 5 — Evaluate

Assess:

* customer value;
* revenue;
* retention;
* engineering effort;
* maintenance;
* strategic fit;
* product complexity.

### Step 6 — Recommendation

Produce structured decision brief.

### Step 7 — Human Decision

User approves/rejects.

### Step 8 — Execution

If approved:

```text
Decision
→ Initiative
→ PRD
→ Requirements
→ Jira
```

### Step 9 — Measurement

Track:

* dashboard adoption;
* customer usage;
* retention;
* support reduction;
* time saved.

### Step 10 — Learning

Compare actual outcome with original hypothesis.

---

# 85. TPG Behavioral Standard

TPG must behave like a senior product executive.

It should:

* challenge weak assumptions;
* ask uncomfortable questions;
* identify hidden trade-offs;
* distinguish signal from noise;
* protect strategic coherence;
* recognize uncertainty;
* resist customer-driven roadmap distortion;
* resist executive opinion without evidence;
* challenge feature requests;
* prioritize outcomes;
* preserve institutional reasoning.

But TPG must remain:

> **Analytical, evidence-driven and explainable — not authoritarian.**

The final decision belongs to the human decision-maker.

---

# 86. Product Intelligence Loop

The PDE establishes the core loop:

```text
                ┌───────────────┐
                │   Signals     │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Requirements  │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Problems    │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Opportunities │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Decisions   │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Initiatives │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Execution   │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Outcomes    │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │   Learning    │
                └───────┬───────┘
                        │
                        └──────────────→ Signals
```

This loop is the foundation of TPG's continuous product intelligence.

---

# 87. Design Freeze

The following are **non-negotiable architecture decisions** for TPG 1.0:

1. TPG must reason about decisions, not merely generate documents.
2. Every major product decision must be represented as a persistent Decision object.
3. Decisions must preserve context, evidence, assumptions, alternatives, rationale and outcomes.
4. TPG must support multiple prioritization frameworks.
5. Framework selection must depend on decision context.
6. TPG must never fabricate missing data.
7. Unknown information must remain explicitly unknown.
8. Customer requests must not automatically become product requirements.
9. Opportunity cost must be considered for major investments.
10. Dependencies and conflicts must be detectable.
11. Decisions must be revisitable.
12. Historical decisions must remain immutable.
13. New decisions may supersede old decisions but must not erase them.
14. Major decisions must link to measurable outcomes.
15. TPG must learn from decision outcomes.
16. TPG must expose reasoning and evidence.
17. TPG must distinguish facts, assumptions and opinions.
18. Human approval remains mandatory for material organizational decisions.
19. TPG must never independently communicate material product decisions to clients.
20. Internal specialist agents remain invisible behind the single TPG identity.
21. V1 remains a private Personal Workspace.
22. No cross-user decision intelligence is permitted in V1.

---

# 88. Relationship to Previous PRDs

```text
PRD-0001
Master Product Charter
        ↓
PRD-0002
Memory & Knowledge Graph
        ↓
PRD-0003
Identity & Personal Workspace
        ↓
PRD-0004
Connector Intelligence
        ↓
PRD-0005
Requirement Intelligence
        ↓
PRD-0006
Product Decision Engine
        ↓
PRD-0007
Product Strategy / Roadmap Intelligence
        ↓
PRD-0008
PRD & Product Specification Engine
        ↓
PRD-0009
Execution & Engineering Intelligence
        ↓
PRD-0010
Quality / QA / Release Intelligence
        ↓
PRD-0011
Product Analytics & Outcome Intelligence
        ↓
PRD-0012
Autonomous Product Office Orchestration
```

---

# 89. Final Product Definition

With PRD-0006, TPG evolves from:

> **"An AI that understands product requirements."**

into:

> **"An AI Product Executive that can reason about what the organization should do, why it should do it, what it should not do, what trade-offs exist, and how the decision should be measured."**

The fundamental TPG loop becomes:

> **Understand → Challenge → Evaluate → Decide → Execute → Measure → Learn.**

That is the core behavior expected from the **Product Decision Engine**.

This sets up **PRD-0007 — Product Strategy, Roadmap Intelligence & Portfolio Management**, where TPG moves from deciding individual initiatives to understanding the **entire product/company direction over time**.
