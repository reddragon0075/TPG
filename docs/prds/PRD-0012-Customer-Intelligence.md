# PRD-0012 — Customer Intelligence, Voice of Customer, Feedback Mining & Opportunity Discovery

**Product:** TPG 1.0 — The Product Guy
**Organization:** SkynetOrg
**Document ID:** PRD-0012
**Status:** Design Specification
**Priority:** P0 — Core Product Intelligence
**Depends On:** PRD-0001 through PRD-0011
**Primary Interface:** ChatGPT
**Architecture:** Invisible Specialist Agents + Unified TPG Identity

---

# 1. Executive Summary

PRD-0011 gave TPG the ability to understand whether product work produced measurable outcomes.

PRD-0012 adds another critical dimension:

> **What are customers actually telling us?**

Organizations receive customer intelligence from many fragmented sources:

```text
Customer Emails
Support Tickets
Sales Calls
Customer Meetings
Slack / Internal Discussions
CRM Notes
Product Feedback
Feature Requests
Bug Reports
Reviews
Surveys
Usage Data
Renewal Discussions
Churn Conversations
```

The problem is that these signals are usually disconnected.

A product manager may know:

> Customer A requested feature X.

Sales may know:

> Customer B is concerned about the same workflow.

Support may know:

> 30 users complained about the workflow.

Analytics may show:

> The workflow has a 42% abandonment rate.

Engineering may know:

> The workflow has a technical limitation.

TPG must connect these signals.

The desired intelligence is:

```text
Customer Signal
      ↓
Observation
      ↓
Problem
      ↓
Pattern
      ↓
Evidence
      ↓
Opportunity
      ↓
Requirement
      ↓
Decision
      ↓
Product Change
      ↓
Outcome
```

The core principle:

> **TPG must listen to the organization’s customers without becoming the customer-facing organization.**

---

# 2. Core Principle

> **A customer request is evidence, not automatically a product requirement.**

A customer saying:

> “Build feature X.”

does not automatically mean:

> “The product should build feature X.”

TPG must investigate:

```text
What is the customer trying to accomplish?
        ↓
What problem are they experiencing?
        ↓
How frequently does it occur?
        ↓
Who else experiences it?
        ↓
What is the business impact?
        ↓
Is this strategically relevant?
        ↓
What solutions are possible?
```

---

# 3. Customer Intelligence Scope

TPG must understand:

1. Customer Signals
2. Voice of Customer
3. Feedback Mining
4. Complaint Intelligence
5. Feature Requests
6. Customer Problems
7. Customer Segmentation
8. Account Intelligence
9. Customer Journey Intelligence
10. Churn Signals
11. Opportunity Discovery
12. Customer Evidence
13. Customer-to-Product Traceability
14. Post-Release Feedback
15. Customer Learning

---

# 4. Customer Intelligence Pipeline

```text
Customer Interaction
        ↓
Signal Extraction
        ↓
Entity Resolution
        ↓
Intent Classification
        ↓
Problem Extraction
        ↓
Evidence Extraction
        ↓
Customer Impact
        ↓
Pattern Detection
        ↓
Cross-Customer Clustering
        ↓
Opportunity Detection
        ↓
Requirement Validation
        ↓
Product Decision
```

---

# 5. Customer Signal Model

TPG must distinguish different signal types.

```text
QUESTION
REQUEST
COMPLAINT
BUG_REPORT
PROBLEM_REPORT
PRAISE
SUGGESTION
REQUIREMENT
OBJECTION
CONFUSION
CHURN_SIGNAL
RENEWAL_SIGNAL
PRICING_CONCERN
COMPETITIVE_SIGNAL
USABILITY_ISSUE
PERFORMANCE_ISSUE
```

---

# 6. Customer Signal Object

```json
{
  "signal_id": "SIG-001",
  "workspace_id": "WS-001",
  "customer_id": "CUS-001",
  "source": "EMAIL",
  "source_reference": "EMAIL-9842",
  "signal_type": "PROBLEM_REPORT",
  "summary": "Customer cannot easily reconcile vendor invoices",
  "raw_claim": "...",
  "problem": "...",
  "impact": "...",
  "frequency": "UNKNOWN",
  "confidence": "HIGH",
  "status": "ANALYZED"
}
```

---

# 7. Customer Entity

TPG must maintain a structured customer model.

```text
Customer
├── Organization
├── Account
├── Contacts
├── Segment
├── Industry
├── Products
├── Plan
├── Usage
├── Revenue
├── Requests
├── Problems
├── Feedback
├── Support History
├── Meetings
├── Commitments
├── Risks
└── Outcomes
```

Only information available through authorized sources should be populated.

---

# 8. Customer vs Contact

TPG must distinguish:

```text
Customer Organization
```

from:

```text
Individual Contact
```

Example:

```text
Customer:
ABC Airlines

Contacts:
Procurement Head
Operations Manager
IT Manager
Product User
```

This prevents:

> One person's opinion

from being interpreted as:

> The customer's organizational position.

---

# 9. Stakeholder Role

Customer contacts may be:

```text
USER
BUYER
DECISION_MAKER
INFLUENCER
TECHNICAL_APPROVER
IMPLEMENTER
ADMIN
EXECUTIVE_SPONSOR
```

This connects to the stakeholder model from PRD-0005.

---

# 10. Customer Evidence Hierarchy

Not all customer signals have equal evidentiary value.

TPG should consider:

```text
Repeated independent customer problem
        ↓
Observed behavior
        ↓
Measured customer impact
        ↓
Multiple stakeholder confirmation
        ↓
Single customer request
        ↓
Individual preference
```

This is not a rigid ranking; context matters.

---

# 11. Evidence Independence

TPG must avoid false counting.

Example:

```text
Customer A:
10 emails about the same problem
```

does not equal:

```text
10 independent customers.
```

TPG should consolidate related signals.

---

# 12. Source Attribution

Every important customer insight should retain:

```text
Source
Customer
Contact
Date
Channel
Original Reference
Evidence
Confidence
```

Example:

> “Customer ABC reported invoice reconciliation difficulty during a September 12 meeting.”

The source must remain traceable.

---

# 13. Supported Customer Sources

Where authorized connectors exist, TPG may analyze:

### Gmail

* customer emails;
* threads;
* requests;
* complaints;
* commitments.

### Calendar

* customer meetings;
* meeting metadata;
* post-meeting notes.

### Slack

* internal discussion about customers;
* support escalations;
* sales/product discussions.

### CRM

* accounts;
* opportunities;
* customer notes;
* renewal information.

### Support

* tickets;
* conversations;
* categories;
* resolution.

### Product Analytics

* customer behavior;
* usage;
* adoption;
* abandonment.

---

# 14. Client Communication Boundary

This is a constitutional rule.

TPG is an **internal organizational teammate**.

Clients are not TPG users.

TPG may:

* read client emails;
* summarize customer conversations;
* extract requirements;
* analyze customer problems;
* prepare meeting briefs;
* draft responses;
* identify commitments;
* recommend internal actions.

TPG may **not**:

* autonomously email clients;
* negotiate;
* promise features;
* promise dates;
* promise roadmap scope;
* negotiate pricing;
* represent itself as an employee;
* join client WhatsApp conversations;
* send proposals autonomously.

Required workflow:

```text
Client Communication
       ↓
TPG Reads
       ↓
TPG Understands
       ↓
TPG Extracts
       ↓
TPG Analyzes
       ↓
TPG Drafts
       ↓
Employee Reviews
       ↓
Employee Sends
```

---

# 15. Customer Email Intelligence

TPG should identify:

* request;
* problem;
* complaint;
* urgency;
* affected workflow;
* customer impact;
* requested response;
* commitment;
* deadline;
* stakeholder.

---

# 16. Example Customer Email

Customer says:

> “We are spending too much time manually reconciling vendor invoices every week.”

TPG should extract:

```text
Signal:
Operational inefficiency

Problem:
Manual invoice reconciliation

User:
Operations team

Impact:
Time consumption

Frequency:
Weekly

Potential Opportunity:
Automated reconciliation

Confidence:
High
```

It should **not** immediately create:

> “Build invoice automation.”

---

# 17. Customer Problem Discovery

TPG should investigate:

```text
What exactly is manual?
Why is it manual?
How often does it happen?
How many users are affected?
What systems are involved?
What errors occur?
What does it cost?
What workaround exists?
```

---

# 18. Customer Request vs Problem

Example:

Customer:

> “Add bulk upload.”

TPG:

```text
Requested solution:
Bulk upload

Possible underlying problem:
Entering hundreds of records manually is inefficient.
```

The requirement engine should then determine whether bulk upload is actually the appropriate solution.

---

# 19. Customer Request Classification

TPG should classify requests:

```text
GENUINE_PROBLEM
SOLUTION_REQUEST
BUG
CONFIGURATION
TRAINING
DOCUMENTATION
WORKFLOW
INTEGRATION
COMPLIANCE
CUSTOMIZATION
PRODUCT_GAP
```

---

# 20. Customer Bug vs Product Gap

TPG must distinguish:

```text
Bug:
Existing promised behavior does not work.
```

from:

```text
Product Gap:
The product does not currently support the desired behavior.
```

---

# 21. Customer Configuration Problem

Some requests may be solvable without product development.

Example:

> “We need another approval level.”

TPG may discover:

> Existing configuration supports this but the customer's account is not configured.

Potential solution:

```text
Configuration
```

rather than:

```text
Engineering
```

---

# 22. Customer Training Problem

Example:

Customer:

> “We can't find the reporting feature.”

TPG should investigate:

```text
Feature exists
+
Low discoverability
```

Potential solution:

* UX improvement;
* documentation;
* onboarding;
* training.

Not automatically a new feature.

---

# 23. Customer Feedback Classification

Feedback should be categorized:

```text
PRODUCT
UX
PERFORMANCE
RELIABILITY
SUPPORT
PRICING
DOCUMENTATION
INTEGRATION
SECURITY
COMPLIANCE
OPERATIONS
TRAINING
```

---

# 24. Sentiment Intelligence

TPG may analyze sentiment as supporting context.

Possible states:

```text
POSITIVE
NEUTRAL
NEGATIVE
MIXED
UNKNOWN
```

But sentiment must not substitute for actual problem evidence.

---

# 25. Context Over Sentiment

Example:

> “This is frustrating, but the system eventually works.”

TPG should capture:

```text
Sentiment:
Negative

Actual issue:
Slow processing

Outcome:
Workflow eventually succeeds
```

The product issue is the measurable behavior, not merely the emotional tone.

---

# 26. Urgency

Customer signals may indicate:

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

Urgency should be based on actual business consequences, not emotional language alone.

---

# 27. Customer Impact

TPG should identify:

```text
TIME
COST
REVENUE
ERRORS
PRODUCTIVITY
COMPLIANCE
RISK
CUSTOMER EXPERIENCE
REPUTATION
```

---

# 28. Customer Impact Model

Example:

```text
Problem:
Manual reconciliation

Frequency:
20 hours/week

Users:
5

Potential impact:
100 staff-hours/week
```

TPG should clearly label calculated estimates vs observed facts.

---

# 29. Customer Journey Intelligence

TPG should model customer journeys.

Example:

```text
Discover
 ↓
Evaluate
 ↓
Purchase
 ↓
Onboard
 ↓
Configure
 ↓
Use
 ↓
Expand
 ↓
Renew
```

---

# 30. Journey Problem Mapping

TPG should associate customer signals with journey stages.

Example:

```text
Onboarding
  ├── Configuration confusion
  ├── Integration delay
  └── Training request

Usage
  ├── Performance complaint
  └── Missing feature
```

---

# 31. Customer Journey + Analytics

Customer intelligence should connect with PRD-0011.

Example:

```text
Customer Feedback:
“Checkout is confusing.”

Analytics:
Checkout abandonment increased.

Support:
Checkout questions increased.
```

TPG identifies:

> **Converging evidence of checkout friction.**

---

# 32. Cross-Customer Pattern Detection

This is one of the most important capabilities.

Example:

```text
Customer A:
Manual reconciliation problem

Customer B:
Manual reconciliation problem

Customer C:
Manual reconciliation problem

Customer D:
Requested automation
```

TPG should detect:

> Potential cross-customer product opportunity.

---

# 33. Pattern Object

```text
Pattern
├── Pattern ID
├── Signals
├── Customers
├── Problem
├── Frequency
├── Segments
├── Evidence
├── Confidence
├── Impact
└── Status
```

---

# 34. Pattern Lifecycle

```text
DETECTED
 ↓
CLUSTERING
 ↓
VALIDATING
 ↓
CONFIRMED
 ↓
OPPORTUNITY
 ↓
REQUIREMENT
```

Alternative:

```text
REJECTED
DUPLICATE
CUSTOMER_SPECIFIC
INSUFFICIENT_EVIDENCE
```

---

# 35. Customer-Specific vs Productizable

TPG must determine whether an issue is:

```text
CUSTOMER_SPECIFIC
```

or:

```text
PRODUCTIZABLE
```

Example:

Customer A requests:

> “Support our internal approval process.”

TPG should investigate whether:

* many customers need it;
* it aligns with the product;
* configurable workflow is valuable;
* it is merely a custom requirement.

---

# 36. Productization Test

TPG should evaluate:

```text
Frequency
+
Customer Impact
+
Market Breadth
+
Strategic Fit
+
Revenue Potential
+
Implementation Cost
+
Long-Term Value
```

No single dimension should automatically decide the outcome.

---

# 37. Feature Request Aggregation

TPG should cluster semantically similar requests.

Example:

```text
“Bulk upload users”
“Upload 500 employees at once”
“Mass employee import”
“CSV employee upload”
```

Potential common problem:

> Efficient bulk employee onboarding.

---

# 38. Request Deduplication

Duplicate requests should be connected rather than creating separate requirements.

```text
REQ-102
REQ-187
REQ-244
```

may all connect to:

```text
OPP-041
Bulk Employee Onboarding
```

---

# 39. Contradictory Feedback

Customers may disagree.

Example:

```text
Customer A:
“Need more automation.”

Customer B:
“Automation removes our control.”
```

TPG should preserve both signals.

It should identify:

```text
Segment Difference
```

rather than selecting one automatically.

---

# 40. Segment-Specific Needs

Example:

```text
Enterprise:
Needs control + approvals

SMB:
Needs speed + simplicity
```

TPG should determine whether the product should support differentiated workflows.

---

# 41. Customer Segment Intelligence

TPG should understand relevant segments:

* enterprise;
* SMB;
* geography;
* industry;
* plan;
* usage maturity;
* customer size;
* lifecycle stage.

Segments should come from available workspace data.

---

# 42. Account-Level Intelligence

For a specific customer, TPG should be able to summarize:

```text
Customer Health
Usage
Adoption
Open Issues
Requests
Complaints
Commitments
Product Gaps
Business Impact
Renewal Risks
Expansion Signals
```

---

# 43. Customer Health

Where sufficient evidence exists:

```text
HEALTHY
STABLE
AT_RISK
CRITICAL
UNKNOWN
```

This is an analytical state, not a claim about customer sentiment.

TPG should show the evidence supporting it.

---

# 44. Churn Signal Intelligence

Potential signals:

* declining usage;
* unresolved critical problems;
* repeated complaints;
* reduced stakeholder engagement;
* renewal objections;
* competitor mentions;
* reduced feature adoption.

TPG should treat these as signals, not guaranteed churn.

---

# 45. Churn Signal Example

```text
Usage:
↓ 32%

Support complaints:
↑ 4x

Renewal discussion:
Pricing concern

Customer:
Evaluating alternatives
```

TPG should surface:

> **Elevated retention risk signals detected.**

---

# 46. Competitive Mentions

Customer conversations may contain:

> “Competitor X provides this.”

TPG should extract:

```text
Competitor:
X

Capability:
Bulk reconciliation

Customer perception:
Required capability

Source:
Customer conversation
```

This becomes market/customer evidence.

---

# 47. Competitor Claim Handling

TPG must distinguish:

```text
Customer says competitor supports X
```

from:

```text
Verified competitor supports X
```

The first is customer intelligence.

The second requires independent evidence.

---

# 48. Customer Pricing Intelligence

TPG may detect:

* pricing objections;
* willingness to pay signals;
* discount requests;
* packaging confusion;
* perceived value issues.

It must distinguish:

```text
Customer Request
```

from:

```text
Validated Pricing Insight
```

---

# 49. Customer Commitment Intelligence

Customer discussions may create commitments.

TPG should identify:

```text
Commitment
Owner
Customer
Deadline
Status
Source
```

Example:

> “We will investigate SSO support by Friday.”

This becomes an internal commitment.

It does **not** automatically become:

> “SSO will ship by Friday.”

---

# 50. Customer Meeting Intelligence

For authorized meeting data:

Before meeting:

```text
Customer profile
Open issues
Previous commitments
Current usage
Recent requests
Known risks
Relevant metrics
```

After meeting:

```text
Problems
Requests
Decisions
Commitments
Questions
Risks
Next actions
```

---

# 51. Meeting-to-Product Intelligence

A meeting may contain:

```text
Customer Problem
+
Requested Feature
+
Business Impact
+
Deadline
```

TPG should convert this into structured evidence.

---

# 52. Customer Feedback Timeline

Each customer should have a temporal history.

```text
Jan:
Requested SSO

Mar:
SSO became blocker

Apr:
Pilot discussed

Jun:
SSO launched

Jul:
Adoption 82%
```

This enables longitudinal reasoning.

---

# 53. Feedback Evolution

TPG should detect:

```text
Request
 ↓
Repeated Request
 ↓
Business Blocker
 ↓
Escalation
 ↓
Product Change
 ↓
Outcome
```

---

# 54. Customer Problem Memory

TPG should remember:

* original problem;
* when discovered;
* affected customer;
* evidence;
* decisions;
* solution;
* outcome.

This prevents repeated rediscovery.

---

# 55. Opportunity Discovery

TPG should identify opportunities from:

```text
Repeated Requests
+
Repeated Problems
+
Usage Friction
+
Support Volume
+
Customer Impact
+
Strategic Alignment
```

---

# 56. Opportunity Object

```json
{
  "opportunity_id": "OPP-001",
  "problem": "Manual reconciliation",
  "customers_affected": 12,
  "segments": ["Enterprise"],
  "evidence_count": 37,
  "impact": "HIGH",
  "strategic_fit": "HIGH",
  "confidence": "HIGH",
  "status": "VALIDATING"
}
```

---

# 57. Opportunity Lifecycle

```text
DETECTED
 ↓
EVIDENCE_COLLECTION
 ↓
PROBLEM_VALIDATION
 ↓
OPPORTUNITY_DEFINED
 ↓
PRIORITIZATION
 ↓
DECISION
```

Terminal:

```text
REJECTED
DEFERRED
CUSTOMER_SPECIFIC
DUPLICATE
INSUFFICIENT_EVIDENCE
```

---

# 58. Opportunity Scoring

TPG may evaluate:

```text
Customer Impact
+
Frequency
+
Strategic Fit
+
Market Breadth
+
Revenue Potential
+
Risk Reduction
+
Evidence Quality
-
Effort
```

The scoring framework must remain configurable.

---

# 59. Evidence Quality

TPG should consider:

* number of independent customers;
* stakeholder diversity;
* recency;
* behavioral evidence;
* support evidence;
* analytics;
* revenue impact;
* repeated occurrence;
* direct observation.

---

# 60. Opportunity Confidence

```text
HIGH
MEDIUM
LOW
UNKNOWN
```

High frequency alone does not automatically mean high confidence.

---

# 61. Opportunity vs Feature

Example:

```text
Opportunity:
Customers need faster invoice reconciliation.

Possible solutions:
1. Bulk upload
2. Automation
3. API integration
4. Improved matching
5. Workflow redesign
```

TPG should preserve the opportunity before prematurely locking into a solution.

---

# 62. Opportunity → Requirement

Once validated:

```text
Customer Evidence
 ↓
Problem
 ↓
Opportunity
 ↓
Requirement
```

This feeds PRD-0005.

---

# 63. Opportunity → Decision

Opportunity evidence feeds PRD-0006.

```text
Opportunity
 ↓
Evidence
 ↓
Options
 ↓
Trade-offs
 ↓
Decision
```

---

# 64. Opportunity → Roadmap

If strategically relevant:

```text
Opportunity
 ↓
Strategic Objective
 ↓
Strategic Bet
 ↓
Roadmap Initiative
```

This feeds PRD-0007.

---

# 65. Opportunity → PRD

Validated opportunity becomes input to PRD-0008.

```text
Opportunity
 ↓
Validated Problem
 ↓
Approved Decision
 ↓
PRD
```

---

# 66. Opportunity → Engineering

Eventually:

```text
Opportunity
 ↓
PRD
 ↓
Technical Design
 ↓
Engineering
```

This preserves full traceability.

---

# 67. Opportunity → Outcome

After release:

```text
Opportunity
 ↓
Product Change
 ↓
Customer Adoption
 ↓
Customer Outcome
```

This connects PRD-0012 back to PRD-0011.

---

# 68. Closed-Loop Customer Intelligence

The complete chain:

```text
Customer
 ↓
Feedback
 ↓
Problem
 ↓
Opportunity
 ↓
Decision
 ↓
Product
 ↓
Release
 ↓
Customer Usage
 ↓
Outcome
 ↓
Feedback
```

TPG continuously learns from the loop.

---

# 69. Customer Feedback After Release

TPG should ask:

> Did the customer problem actually improve?

Example:

Before:

```text
Manual reconciliation:
20 hrs/week
```

After:

```text
Manual reconciliation:
11 hrs/week
```

TPG can report:

> “Observed manual effort decreased by approximately 45% for the measured customer cohort.”

---

# 70. Customer Outcome vs Product Outcome

A feature can improve product metrics without improving customer outcomes.

Example:

```text
Feature adoption:
+40%

Customer time saved:
0%
```

TPG should flag:

> High adoption did not translate into the intended customer outcome.

---

# 71. Customer Outcome Evidence

Potential measures:

```text
Time Saved
Cost Saved
Errors Reduced
Processing Time
Manual Work Reduced
Revenue Impact
Operational Efficiency
User Satisfaction
Retention
Adoption
```

---

# 72. Customer Feedback + Support

Support data should be mined for:

* recurring problems;
* product gaps;
* documentation gaps;
* training gaps;
* usability issues;
* reliability issues.

---

# 73. Support Volume Intelligence

Example:

```text
Issue:
“Driver ETA mismatch”

Support tickets:
Jan: 12
Feb: 17
Mar: 41
```

TPG should identify an increasing support pattern.

---

# 74. Support vs Product Requirement

High ticket volume does not automatically mean:

> Build a new feature.

Potential causes:

```text
Product Bug
UX Problem
Documentation
Training
Configuration
Operational Issue
```

TPG should investigate.

---

# 75. Customer Evidence Convergence

Strong product evidence may come from multiple independent channels:

```text
Customer Emails
       +
Support Tickets
       +
Usage Analytics
       +
Sales Feedback
       +
Meeting Notes
```

If they point toward the same problem, TPG should increase confidence.

---

# 76. Evidence Divergence

If sources disagree:

```text
Customers say:
Workflow is slow.

Analytics:
Median latency normal.

Support:
Few complaints.
```

TPG should not force a conclusion.

It should investigate:

* segment differences;
* perception vs measured latency;
* specific workflows;
* outliers.

---

# 77. Customer Evidence Graph

TPG should construct:

```text
Customer
   ↓
Signal
   ↓
Problem
   ↓
Evidence
   ↓
Opportunity
   ↓
Requirement
   ↓
Decision
   ↓
Initiative
```

This becomes part of the organizational knowledge graph.

---

# 78. Customer Intelligence Queries

TPG should support:

> “What are customers complaining about?”

> “What feature requests are increasing?”

> “Which problems affect multiple customers?”

> “What are our enterprise customers asking for?”

> “Why are customers churning?”

> “What are the biggest customer pain points?”

> “Which requests are actually product opportunities?”

> “Which customer problems have no roadmap coverage?”

> “What did customers say about the latest release?”

> “Which customer problems are supported by analytics?”

> “Which requests are customer-specific?”

---

# 79. Executive Customer Brief

TPG should generate:

```text
CUSTOMER INTELLIGENCE

Top Problems
1. Reconciliation
2. Reporting
3. Integration reliability

Emerging Signal
SSO becoming a recurring enterprise requirement.

Positive Signal
New dashboard receiving strong adoption.

Risk
Three enterprise accounts report workflow performance concerns.

Opportunity
Standardized approval workflow.
```

Every major claim must be traceable to evidence.

---

# 80. Product Manager Brief

For a PM:

```text
Problem:
Manual reconciliation

Evidence:
12 customers
37 signals
3 segments

Behavior:
High manual activity

Impact:
Significant operational effort

Existing Solution:
Partial automation

Gap:
Exception handling

Opportunity:
Automated exception workflow

Confidence:
High
```

---

# 81. Customer Portfolio View

TPG should be able to summarize:

```text
Customers
 ↓
Problems
 ↓
Requests
 ↓
Opportunities
 ↓
Roadmap Coverage
```

Example:

| Opportunity      | Customers | Roadmap     | Evidence |
| ---------------- | --------: | ----------- | -------- |
| SSO              |         8 | Planned     | High     |
| Bulk upload      |        14 | Not covered | High     |
| Advanced reports |         6 | Exploratory | Medium   |
| Custom workflow  |         1 | Not planned | Low      |

This is descriptive portfolio intelligence, not automatic prioritization.

---

# 82. Roadmap Coverage Gap

TPG should identify:

> “A recurring customer problem has no corresponding roadmap initiative.”

This becomes a decision signal.

---

# 83. Customer Promise Tracking

TPG must track what the organization has actually promised.

Distinguish:

```text
Customer Asked
Customer Suggested
TPG Recommended
Employee Promised
Company Committed
Roadmap Target
```

These are not equivalent.

---

# 84. Promise Integrity

Example:

Customer:

> “Can you deliver this by December?”

Employee:

> “We will try.”

TPG must not convert this into:

> “Committed for December.”

Only explicit commitments should become commitments.

---

# 85. Customer Commitment Object

```text
Commitment
├── Customer
├── Owner
├── Statement
├── Date
├── Source
├── Commitment Level
├── Status
└── Related Initiative
```

---

# 86. Customer Escalation Intelligence

TPG should detect:

```text
Repeated issue
 ↓
No resolution
 ↓
Escalation
 ↓
Executive involvement
```

It should surface internal urgency.

---

# 87. Escalation Risk

Potential signals:

* repeated unresolved complaints;
* executive escalation;
* renewal risk;
* contractual impact;
* critical operational impact.

TPG should identify evidence rather than speculate.

---

# 88. Customer Success Integration

Where customer-success data is available, TPG should connect:

```text
Customer Health
+
Product Usage
+
Open Issues
+
Requests
+
Outcomes
```

This creates a product/customer feedback loop.

---

# 89. Sales Intelligence

Sales conversations may contain:

* requested capabilities;
* competitive objections;
* buying blockers;
* pricing objections;
* integration requirements.

TPG should distinguish:

```text
Sales Deal Requirement
```

from:

```text
Validated Product Requirement
```

---

# 90. Revenue vs Product Fit

A high-value customer request may still be strategically wrong for the core product.

TPG should surface:

```text
Revenue Importance
+
Product Fit
+
Market Breadth
+
Long-Term Consequence
```

without blindly optimizing for a single deal.

---

# 91. Customer Customization Risk

TPG should detect when multiple customizations are accumulating.

Example:

```text
Customer A:
Custom workflow

Customer B:
Custom approval

Customer C:
Custom reporting

Customer D:
Custom integration
```

Potential result:

> Product fragmentation risk.

---

# 92. Product Fragmentation

TPG should track:

```text
Standard Capability
vs
Customer-Specific Capability
```

This can reveal:

* maintenance burden;
* roadmap complexity;
* inconsistent user experience;
* technical debt.

---

# 93. Customer-Specific Feature Flag Intelligence

Where available, TPG should know:

```text
Feature
 ↓
Customer
 ↓
Flag
 ↓
Usage
 ↓
Outcome
```

This helps distinguish:

> Product capability

from:

> Customer-specific customization.

---

# 94. Voice of Customer Dashboard

TPG should support a structured summary:

```text
VOC HEALTH

Top Problem:
Reconciliation

Fastest Growing Problem:
Reporting latency

Most Requested Capability:
Bulk operations

Most Severe Issue:
Integration reliability

Emerging Opportunity:
Approval automation

At-Risk Segment:
Enterprise operations

Evidence Confidence:
Medium
```

---

# 95. Customer Intelligence Alerts

TPG may proactively surface:

```text
New recurring customer problem
Rapid complaint increase
New churn signal
Repeated enterprise request
Competitor mention
Customer commitment approaching
Unexpected post-release feedback
```

Alerts must be configurable.

---

# 96. Silent vs Active Intelligence

As established in earlier PRDs:

### Silent

Store and connect the signal.

### Active

Tell the user because the signal may require attention.

TPG should avoid overwhelming users with low-value alerts.

---

# 97. Alert Priority

```text
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL
```

Priority should consider:

```text
Customer Impact
+
Frequency
+
Urgency
+
Revenue / Contract Impact
+
Strategic Importance
+
Evidence
```

---

# 98. Customer Intelligence Memory

TPG should remember:

* customer problems;
* requests;
* patterns;
* outcomes;
* commitments;
* feedback;
* customer-specific constraints;
* product gaps.

It should not preserve entire communications unnecessarily.

---

# 99. Memory Principle

> **TPG remembers customer intelligence, not customer noise.**

The system should extract durable knowledge rather than treating every email sentence as permanent memory.

---

# 100. Customer Knowledge Graph

Example:

```text
Customer ABC
      │
      ├── Reported → Problem P1
      │
      ├── Requested → Feature R1
      │
      ├── Blocked By → Issue B1
      │
      ├── Uses → Product X
      │
      ├── Adopted → Feature F1
      │
      └── Outcome → Reduced manual effort
```

---

# 101. Cross-Customer Knowledge Graph

```text
Problem P1
 ├── Customer A
 ├── Customer B
 ├── Customer C
 └── Customer D

Opportunity O1
 └── Problem P1

Initiative I1
 └── Opportunity O1

Outcome O1
 └── Initiative I1
```

This is the foundation for opportunity discovery.

---

# 102. Customer Intelligence Specialist Architecture

All specialists remain invisible behind TPG.

```text
                           TPG
                            │
                  Customer Intelligence
                      Orchestrator
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   Email Agent         Support Agent        Meeting Agent
       │                    │                    │
   Feedback Agent      Account Agent        CRM Agent
       │                    │                    │
 Pattern Agent       Opportunity Agent    Churn Agent
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                  Customer Intelligence
                       Synthesizer
                            │
                           TPG
```

---

# 103. Customer Intelligence Orchestrator

Responsibilities:

1. ingest customer signals;
2. identify customer;
3. identify stakeholder;
4. classify signal;
5. extract problem;
6. extract impact;
7. identify evidence;
8. cluster related signals;
9. detect patterns;
10. identify opportunities;
11. feed requirements;
12. monitor outcomes.

---

# 104. Email Intelligence Agent

Responsible for:

* customer request extraction;
* problem extraction;
* commitment extraction;
* stakeholder identification;
* urgency;
* customer impact.

---

# 105. Support Intelligence Agent

Responsible for:

* ticket clustering;
* recurring issue detection;
* defect identification;
* support volume;
* resolution patterns.

---

# 106. Meeting Intelligence Agent

Responsible for:

* meeting context;
* customer problems;
* requests;
* commitments;
* decisions;
* follow-ups.

---

# 107. Pattern Agent

Responsible for:

* semantic clustering;
* duplicate detection;
* recurring problem detection;
* cross-customer patterns.

---

# 108. Opportunity Agent

Responsible for:

* opportunity discovery;
* problem validation;
* customer breadth;
* strategic fit;
* evidence quality.

---

# 109. Churn Intelligence Agent

Responsible for:

* usage decline;
* unresolved issues;
* renewal signals;
* customer risk patterns.

It must not claim that a customer will churn without evidence.

---

# 110. Customer Intelligence → Requirement Engine

The integration is:

```text
Customer Signal
      ↓
Problem
      ↓
Evidence
      ↓
Opportunity
      ↓
PRD-0005
```

PRD-0005 remains the authority for requirement reasoning.

---

# 111. Customer Intelligence → Decision Engine

```text
Opportunity
      ↓
Evidence
      ↓
Options
      ↓
Trade-offs
      ↓
PRD-0006
```

---

# 112. Customer Intelligence → Strategy

```text
Cross-Customer Pattern
      ↓
Market Signal
      ↓
Strategic Implication
      ↓
PRD-0007
```

---

# 113. Customer Intelligence → Analytics

```text
Customer Feedback
      +
Product Behavior
      ↓
Converging Evidence
      ↓
Outcome Analysis
```

---

# 114. Customer Intelligence → Quality

```text
Customer Complaint
      ↓
Defect Investigation
      ↓
QA Test Gap
      ↓
Regression Test
```

---

# 115. Customer Intelligence → Engineering

```text
Customer Problem
      ↓
Validated Requirement
      ↓
Technical Implication
      ↓
Engineering
```

---

# 116. Full TPG Loop

After PRD-0012:

```text
                    CUSTOMER
                       ↓
                    SIGNALS
                       ↓
                    PROBLEMS
                       ↓
                   OPPORTUNITIES
                       ↓
                    DECISIONS
                       ↓
                     PRD
                       ↓
                 ENGINEERING
                       ↓
                      QA
                       ↓
                    RELEASE
                       ↓
                  ADOPTION
                       ↓
                    OUTCOME
                       ↓
                  CUSTOMER
                       ↓
                  NEW SIGNAL
```

This is a genuine closed-loop Product Office.

---

# 117. Non-Functional Requirements

## Performance

Standard customer-intelligence query:

**<10 seconds target**

Deep multi-source customer analysis:

**<90 seconds target**

---

## Traceability

Every material customer insight should retain source references.

---

## Privacy

Customer data must remain isolated within the authorized Personal Workspace.

---

## Security

Sensitive customer information must not become uncontrolled organizational memory.

---

## Accuracy

TPG must distinguish:

```text
Observed
Inferred
Reported
Assumed
Unknown
```

---

# 118. Acceptance Criteria

### CUST-AC-001

TPG can extract customer signals from authorized sources.

### CUST-AC-002

TPG can identify customer organizations.

### CUST-AC-003

TPG can identify customer stakeholders.

### CUST-AC-004

TPG can classify customer signals.

### CUST-AC-005

TPG can distinguish requests from problems.

### CUST-AC-006

TPG can distinguish bugs from product gaps.

### CUST-AC-007

TPG can identify configuration/training issues.

### CUST-AC-008

TPG can identify customer impact.

### CUST-AC-009

TPG can cluster related customer requests.

### CUST-AC-010

TPG can detect recurring problems.

### CUST-AC-011

TPG can detect cross-customer patterns.

### CUST-AC-012

TPG can identify customer-specific requirements.

### CUST-AC-013

TPG can identify potentially productizable opportunities.

### CUST-AC-014

TPG can maintain customer evidence.

### CUST-AC-015

TPG can preserve source attribution.

### CUST-AC-016

TPG can identify contradictory customer feedback.

### CUST-AC-017

TPG can analyze customer journey problems.

### CUST-AC-018

TPG can identify customer risk signals.

### CUST-AC-019

TPG can connect customer signals to analytics.

### CUST-AC-020

TPG can connect customer problems to requirements.

### CUST-AC-021

TPG can connect opportunities to product decisions.

### CUST-AC-022

TPG can connect customer problems to roadmap coverage.

### CUST-AC-023

TPG can identify roadmap gaps against recurring customer problems.

### CUST-AC-024

TPG can track customer commitments.

### CUST-AC-025

TPG can track customer feedback after product releases.

### CUST-AC-026

TPG can convert production/customer problems into product learning.

### CUST-AC-027

TPG does not treat a single customer request as automatically representative.

### CUST-AC-028

TPG does not fabricate customer sentiment or intent.

### CUST-AC-029

TPG does not claim customer churn without evidence.

### CUST-AC-030

TPG does not autonomously communicate with clients.

---

# 119. Failure Scenarios

## F-001 — Single Customer Request

TPG must state:

> “This is currently a single-customer signal.”

It must not present it as a market-wide requirement.

---

## F-002 — Repeated Emails From Same Customer

TPG must consolidate them rather than counting each email as independent evidence.

---

## F-003 — Customer Requests Specific Solution

TPG must separate:

```text
Requested Solution
```

from:

```text
Underlying Problem
```

---

## F-004 — Contradictory Customers

TPG must preserve the disagreement and investigate segmentation.

---

## F-005 — Customer Sentiment Without Specific Problem

TPG should record sentiment as context but should not manufacture a product problem.

---

## F-006 — Competitor Claim

TPG must identify:

> “Customer-reported competitor capability.”

It must not present the claim as independently verified.

---

## F-007 — Customer Health Unknown

TPG must say:

> “Insufficient evidence to assess customer health.”

---

## F-008 — Churn Signal

TPG should report:

> “Potential churn-risk signals detected.”

Not:

> “Customer will churn.”

---

## F-009 — Customer Commitment Ambiguity

TPG must distinguish:

```text
Customer Asked
```

from:

```text
Employee Promised
```

---

## F-010 — Client Communication

TPG prepares internal analysis/drafts only.

No autonomous client communication.

---

# 120. Design Freeze

The following are **non-negotiable** for TPG 1.0:

1. Customer requests are evidence, not automatic requirements.
2. Customer signals must be classified.
3. Customer organizations must be distinguished from individual contacts.
4. Stakeholder roles must be preserved.
5. Customer evidence must retain source attribution.
6. Repeated signals from the same customer must not be counted as independent customers.
7. Problems must be separated from requested solutions.
8. Bugs must be distinguished from product gaps.
9. Configuration and training issues must be considered.
10. Customer-specific needs must be distinguished from productizable opportunities.
11. Cross-customer pattern detection must exist.
12. Contradictory feedback must be preserved.
13. Segment differences must be considered.
14. Customer journey problems must be traceable.
15. Customer impact must be explicit.
16. Customer evidence must have confidence.
17. Sentiment must not substitute for evidence.
18. Customer churn must not be predicted as fact.
19. Competitor claims from customers must remain attributed.
20. Customer commitments must be distinguished from requests.
21. Customer feedback must connect to requirements.
22. Opportunities must connect to decisions.
23. Opportunities must connect to roadmap intelligence.
24. Customer outcomes must connect to analytics.
25. Customer complaints must connect to quality intelligence.
26. Customer intelligence must remain traceable to source.
27. TPG must remember durable customer intelligence rather than raw communication noise.
28. Customer data must remain within authorized workspace boundaries.
29. TPG must never autonomously communicate with clients.
30. TPG must never promise scope, dates, pricing or roadmap commitments.
31. V1 remains within the user's Personal Workspace.
32. Customer Intelligence specialists remain invisible behind TPG.
33. Human approval remains required for material product decisions.

---

# 121. TPG Architecture After PRD-0012

```text
                           TPG
                            │
                      MEMORY CORE
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
     STRATEGY          REQUIREMENTS         CUSTOMERS
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                         DECISIONS
                            │
                         ROADMAP
                            │
                           PRD
                            │
                      ENGINEERING
                            │
                           QA
                            │
                        RELEASE
                            │
                        ANALYTICS
                            │
                         OUTCOME
                            │
                       CUSTOMER
                            │
                         FEEDBACK
                            │
                      OPPORTUNITY
                            │
                       NEXT DECISION
```

---

# 122. The Digital Product Office Loop

At this point TPG has a much more complete intelligence cycle:

```text
              ┌───────────────────┐
              │     STRATEGY      │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │     DECISION      │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │       PRD         │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │   ENGINEERING     │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │       QA          │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │     RELEASE       │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │     ANALYTICS     │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │     OUTCOME       │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │     CUSTOMER      │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │    FEEDBACK       │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │   OPPORTUNITY     │
              └─────────┬─────────┘
                        │
                        └────────────→ DECISION
```

---

# 123. Final Product Definition

After PRD-0012, TPG can understand both sides of the product equation.

### Internal side

```text
Strategy
→ Decisions
→ Roadmap
→ PRD
→ Engineering
→ QA
→ Release
→ Analytics
```

### External side

```text
Customers
→ Problems
→ Feedback
→ Behavior
→ Outcomes
→ Opportunities
```

TPG connects them:

```text
                    TPG
                     │
       ┌─────────────┴─────────────┐
       │                           │
 INTERNAL PRODUCT SYSTEM      CUSTOMER SYSTEM
       │                           │
 Strategy                    Customer Signals
 Decisions                   Problems
 Roadmap                     Feedback
 PRD                         Usage
 Engineering                 Outcomes
 QA                          Opportunities
 Release
 Analytics
       │                           │
       └─────────────┬─────────────┘
                     ↓
              PRODUCT LEARNING
                     ↓
                NEXT DECISION
```

That is a major architectural milestone.

TPG is no longer merely:

> **“AI that helps a Product Manager.”**

It is becoming:

> **“An invisible Product Executive that continuously connects company strategy, product execution, engineering reality, customer reality, and measurable outcomes.”**

---

# 124. Next PRD

**PRD-0013 — Competitive Intelligence, Market Intelligence & External Signal Intelligence**

The next layer will answer:

```text
What is happening outside the company?

Customers
+
Competitors
+
Market
+
Technology
+
Regulation
+
Industry Trends
+
Pricing
+
New Entrants
+
External Events
        ↓
External Intelligence
        ↓
Strategic Implications
        ↓
Product Decisions
```

This will give TPG the **external market intelligence layer**, complementing the internal organizational intelligence built through PRD-0001 to PRD-0012.
