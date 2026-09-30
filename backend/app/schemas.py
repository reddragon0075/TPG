"""
Pydantic Schemas — API Request/Response Models

These define the contract between the ChatGPT Actions API
and the TPG backend. They are NOT the database models.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ─── Enums (mirror DB enums for API layer) ─────────────────────

class EntityTypeEnum(str, Enum):
    FACT = "fact"
    WORKSPACE_CONFIG = "workspace_config"
    STRATEGY = "strategy"
    STRATEGIC_THEME = "strategic_theme"
    OBJECTIVE = "objective"
    STRATEGIC_BET = "strategic_bet"
    ASSUMPTION = "assumption"
    INITIATIVE = "initiative"
    REQUIREMENT = "requirement"
    DECISION = "decision"
    PRD = "prd"
    CUSTOMER = "customer"
    CONTACT = "contact"
    SIGNAL = "signal"
    PROBLEM = "problem"
    OPPORTUNITY = "opportunity"
    COMMITMENT = "commitment"
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    PULL_REQUEST = "pull_request"
    ARCHITECTURE_DECISION = "adr"
    TECHNICAL_DEBT = "technical_debt"
    TECHNICAL_RISK = "technical_risk"
    TEST_STRATEGY = "test_strategy"
    TEST_CASE = "test_case"
    DEFECT = "defect"
    RELEASE = "release"
    METRIC = "metric"
    KPI = "kpi"
    EXPERIMENT = "experiment"
    OUTCOME = "outcome"
    LEARNING = "learning"


class ConfidenceEnum(str, Enum):
    CONFIRMED = "confirmed"
    INFERRED = "inferred"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"


class RelationshipTypeEnum(str, Enum):
    BELONGS_TO = "belongs_to"
    CONTAINS = "contains"
    PART_OF = "part_of"
    CREATED_FROM = "created_from"
    DEPENDS_ON = "depends_on"
    BLOCKS = "blocks"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    IMPLEMENTS = "implements"
    TESTS = "tests"
    TRACES_TO = "traces_to"
    MEASURED_BY = "measured_by"
    REQUESTED_BY = "requested_by"
    AFFECTS = "affects"
    RESOLVES = "resolves"
    CAUSED_BY = "caused_by"
    RELATES_TO = "relates_to"


# ─── Memory / Entity Schemas ──────────────────────────────────

class MemoryStoreRequest(BaseModel):
    """Store a piece of knowledge in TPG's memory."""
    entity_type: EntityTypeEnum = Field(
        default=EntityTypeEnum.FACT,
        description="The type of knowledge being stored",
    )
    name: str = Field(
        ...,
        max_length=500,
        description="Short name or title for this knowledge",
    )
    description: str | None = Field(
        default=None,
        description="Detailed description or content",
    )
    properties: dict = Field(
        default_factory=dict,
        description="Additional structured properties",
    )
    source: str | None = Field(
        default="user",
        description="Where this knowledge came from",
    )
    confidence: ConfidenceEnum = Field(
        default=ConfidenceEnum.CONFIRMED,
        description="How confident is this information",
    )


class MemoryStoreResponse(BaseModel):
    """Confirmation that knowledge was stored."""
    entity_id: str
    entity_type: str
    name: str
    message: str


class EntityResponse(BaseModel):
    """A single entity from the Knowledge Graph."""
    id: str
    entity_type: str
    name: str
    description: str | None = None
    properties: dict = {}
    source: str | None = None
    confidence: str = "confirmed"
    status: str = "active"
    version: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoryRecallRequest(BaseModel):
    """Query TPG's memory."""
    query: str = Field(
        ...,
        description="What are you looking for?",
    )
    entity_type: EntityTypeEnum | None = Field(
        default=None,
        description="Filter by entity type",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum results to return",
    )


class MemoryRecallResponse(BaseModel):
    """Results from a memory query."""
    query: str
    total_results: int
    entities: list[EntityResponse]


# ─── Relationship Schemas ──────────────────────────────────────

class RelationshipCreateRequest(BaseModel):
    """Create a relationship between two entities."""
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipTypeEnum
    properties: dict = Field(default_factory=dict)
    confidence: ConfidenceEnum = Field(default=ConfidenceEnum.CONFIRMED)


class RelationshipResponse(BaseModel):
    """A relationship between two entities."""
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: dict = {}
    confidence: str = "confirmed"
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Graph Query Schemas ───────────────────────────────────────

class GraphQueryRequest(BaseModel):
    """Query the Knowledge Graph for connected entities."""
    entity_id: str = Field(
        ..., description="Starting entity ID"
    )
    relationship_types: list[RelationshipTypeEnum] | None = Field(
        default=None,
        description="Filter by relationship type",
    )
    depth: int = Field(
        default=1, ge=1, le=3,
        description="How many hops to traverse",
    )


class GraphNeighbor(BaseModel):
    """An entity connected to the queried entity."""
    entity: EntityResponse
    relationship_type: str
    direction: str  # "outgoing" or "incoming"


class GraphQueryResponse(BaseModel):
    """Connected entities from a graph traversal."""
    center_entity: EntityResponse
    neighbors: list[GraphNeighbor]
    total_connections: int


# ─── Health ────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """System health check."""
    status: str = "healthy"
    version: str
    database: str = "connected"
    entity_count: int = 0


# ─── Intelligence & Reasoning Schemas (PRD-0005, PRD-0006) ───

class RequirementAnalyzeRequest(BaseModel):
    statement: str = Field(..., description="Raw requirement or problem statement")
    context: dict = Field(default_factory=dict, description="Optional surrounding context")


class DiscoveryQuestionSchema(BaseModel):
    priority: int
    dimension: str
    question: str
    rationale: str


class JTBDSchema(BaseModel):
    situation: str
    motivation: str
    expected_outcome: str


class RequirementAnalyzeResponse(BaseModel):
    is_product_requirement: bool
    detected_type: str
    ambiguity_score: float
    completeness_score: float
    missing_dimensions: list[str]
    prioritized_questions: list[DiscoveryQuestionSchema]
    suggested_jtbd: list[JTBDSchema]


class RequirementIngestRequest(BaseModel):
    raw_text: str = Field(..., description="Requirement details / user description")
    title: str = Field(..., description="Concise title for the requirement")
    initiative_id: str | None = Field(default=None, description="Optional parent Initiative ID")
    source: str = Field(default="chatgpt")
    source_reference: str | None = Field(default=None)


class RequirementIngestResponse(BaseModel):
    entity_id: str
    entity_type: str
    title: str
    ambiguity_score: float
    discovery_state: str
    next_questions: list[str]


class SolutionOptionSchema(BaseModel):
    name: str
    description: str
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    effort: float = Field(default=3.0, ge=1.0, le=5.0)
    impact: float = Field(default=3.0, ge=1.0, le=5.0)
    risk: float = Field(default=2.0, ge=1.0, le=5.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class DecisionEvaluateRequest(BaseModel):
    decision_question: str
    options: list[SolutionOptionSchema]


class RankedOptionResponse(BaseModel):
    name: str
    score: float
    analysis: str


class DecisionEvaluateResponse(BaseModel):
    decision_question: str
    top_recommendation: str
    ranked_options: list[RankedOptionResponse]
    tradeoffs: list[str]


class DecisionRecordRequest(BaseModel):
    title: str
    decision_type: str = "PRODUCT_INVESTMENT"
    outcome: str = "APPROVED"
    decision_question: str
    context: str
    rationale: str
    options: list[SolutionOptionSchema]
    evidence_citations: list[str] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    initiative_id: str | None = None
    problem_id: str | None = None
    requirement_id: str | None = None


class DecisionRecordResponse(BaseModel):
    decision_id: str
    title: str
    outcome: str
    confidence: float
    tradeoffs_count: int


# ─── Multi-Stage Graph Query Schemas (PRD-0002 §9) ─────────────

class MultiStageGraphQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question, e.g. 'Why was Vendor Wallet approved?'")
    entity_id: str | None = Field(default=None, description="Optional target entity ID")
    entity_type: str | None = Field(default=None, description="Optional entity type filter")


class EvidenceItemSchema(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    relationship: str
    source: str | None = None
    confidence: str = "confirmed"


class MultiStageGraphQueryResponse(BaseModel):
    query: str
    intent: str
    narrative_summary: str
    evidence: list[EvidenceItemSchema]
    total_nodes: int
    total_edges: int
    confidence: str


class LineageTraceResponse(BaseModel):
    entity_id: str
    root_name: str
    root_type: str
    upstream_count: int
    downstream_count: int
    provenance_chain: list[str]


class ShortestPathResponse(BaseModel):
    source_id: str
    target_id: str
    path_found: bool
    distance: int
    path_names: list[str]


# ─── PRD & Product Specification Schemas (PRD-0008) ───────────

class PRDAssessRequest(BaseModel):
    problem: str | None = Field(default=None, description="Validated problem statement")
    requirements: list[str] = Field(default_factory=list, description="List of functional capabilities")
    decision_rationale: str | None = Field(default=None, description="Executive decision justification")
    evidence: list[str] | None = Field(default=None, description="Customer or empirical data citations")
    success_metric: str | None = Field(default=None, description="Target success KPI")


class PRDAssessResponse(BaseModel):
    level: str
    overall_score: float
    dimension_scores: dict[str, str]
    missing_critical_items: list[str]
    readiness_notes: str


class PRDGenerateRequest(BaseModel):
    title: str = Field(..., description="Title of the PRD/Feature")
    problem: str = Field(..., description="Core customer/business problem")
    raw_requirements: list[str] = Field(..., description="Key functional requirements")
    decision_rationale: str | None = None
    evidence: list[str] | None = None
    target_personas: list[str] | None = None
    non_goals: list[str] | None = Field(default=None, description="Explicit out-of-scope non-goals")
    success_metric: str | None = None
    initiative_id: str | None = None
    decision_id: str | None = None


class PRDGenerateResponse(BaseModel):
    title: str
    version: int
    status: str
    executive_summary: dict[str, str]
    goals: list[str]
    non_goals: list[str]
    functional_requirements_count: int
    acceptance_criteria_count: int
    markdown: str


class PRDSaveResponse(BaseModel):
    prd_id: str
    title: str
    version: int
    status: str
    markdown_length: int


# ─── Engineering Intelligence Schemas (PRD-0009) ──────────────


class RequirementInput(BaseModel):
    """A single requirement for technical analysis."""
    id: str = Field(..., description="Requirement ID, e.g. FR-001")
    text: str = Field(..., description="Requirement description")


class EngineeringAnalyzeRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity in the Knowledge Graph")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="List of functional requirements")


class TechnicalImplicationSchema(BaseModel):
    requirement_ref: str
    requirement_text: str
    affected_components: list[str]
    new_components: list[str]
    data_model_changes: list[str]
    api_changes: list[str]
    dependencies: list[str]
    risks: list[str]
    confidence: str = "inferred"


class EngineeringAnalyzeResponse(BaseModel):
    prd_entity_id: str
    prd_title: str
    phase: str
    architecture_impact: str
    total_affected_components: list[str]
    total_new_components: list[str]
    total_dependencies: list[str]
    total_risks: list[str]
    implications: list[TechnicalImplicationSchema]
    recommendation: str


class TechnicalDesignRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    title: str = Field(..., description="Title for the technical design")
    requirements: list[RequirementInput] = Field(..., description="Requirements to analyze")
    architecture_context: str | None = Field(default=None, description="Optional existing architecture notes")


class ComponentSchema(BaseModel):
    name: str
    change_type: str
    confidence: str = "inferred"


class TechnicalDesignResponse(BaseModel):
    title: str
    architecture_context: str
    existing_system: list[str]
    proposed_changes: list[str]
    components: list[ComponentSchema]
    data_flow: list[str]
    api_changes: list[dict]
    data_model: list[dict]
    events: list[str]
    dependencies: list[str]
    security_considerations: list[str]
    scalability_notes: list[str]
    failure_modes: list[dict]
    observability: list[str]
    migration_strategy: str
    rollback_strategy: str
    open_questions: list[str]


class ADRAlternativeSchema(BaseModel):
    name: str = Field(..., description="Alternative option name")
    description: str = Field(..., description="Brief description of the alternative")
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class ADRCreateRequest(BaseModel):
    title: str = Field(..., description="ADR title")
    context: str = Field(..., description="Decision context")
    alternatives: list[ADRAlternativeSchema] = Field(..., description="Options considered")
    decision: str = Field(..., description="The decision made")
    consequences: list[str] = Field(..., description="Consequences of the decision")
    rationale: str = Field(..., description="Reasoning behind the decision")
    related_prd_id: str | None = None
    related_initiative_id: str | None = None


class ADRCreateResponse(BaseModel):
    adr_id: str
    title: str
    status: str
    alternatives_count: int
    consequences_count: int


class BreakdownRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="Requirements to decompose")


class StorySchema(BaseModel):
    story_id: str
    title: str
    context: str
    requirement_ref: str
    acceptance_criteria: list[str]
    dependencies: list[str] = Field(default_factory=list)
    estimated_hours: float | None = None
    estimate_confidence: str = "UNKNOWN"


class EpicSchema(BaseModel):
    epic_id: str
    title: str
    description: str
    stories: list[StorySchema]


class BreakdownResponse(BaseModel):
    prd_entity_id: str
    prd_title: str
    epics: list[EpicSchema]
    total_stories: int
    total_estimated_hours: float
    estimate_confidence: str


class DependencySchema(BaseModel):
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    dependency_type: str
    is_blocking: bool
    description: str = ""


class EffortEstimateRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="Requirements to estimate")
    testing_multiplier: float = Field(default=0.3, ge=0.0, le=1.0)
    integration_multiplier: float = Field(default=0.15, ge=0.0, le=1.0)
    contingency_multiplier: float = Field(default=0.2, ge=0.0, le=1.0)


class EffortEstimateResponse(BaseModel):
    development_hours: float
    testing_hours: float
    integration_hours: float
    migration_hours: float
    deployment_hours: float
    contingency_hours: float
    total_hours: float
    confidence: str
    assumptions: list[str]


class CapacityRequest(BaseModel):
    available_hours: float = Field(..., description="Total available team hours")
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="Requirements")


class CapacityResponse(BaseModel):
    available_hours: float
    required_hours: float
    conflict_hours: float
    has_conflict: bool
    utilization_percent: float
    recommendations: list[str]


class TechDebtRequest(BaseModel):
    component: str = Field(..., description="Affected component or module")
    description: str = Field(..., description="Description of the technical debt")
    severity: str = Field(default="MEDIUM", description="CRITICAL, HIGH, MEDIUM, LOW")
    product_impact: str = Field(..., description="How this debt impacts the product")
    business_cost: str = Field(..., description="Business cost of not addressing")
    remediation: str = Field(..., description="Proposed remediation approach")
    estimated_effort_hours: float | None = None
    accumulated_since: str | None = None


class TechDebtResponse(BaseModel):
    tech_debt_id: str
    component: str
    severity: str
    product_impact: str


class TechRiskRequest(BaseModel):
    risk: str = Field(..., description="Description of the technical risk")
    likelihood: str = Field(default="MEDIUM", description="HIGH, MEDIUM, LOW")
    impact: str = Field(default="MEDIUM", description="HIGH, MEDIUM, LOW")
    mitigation: str = Field(..., description="Proposed mitigation")
    owner: str = Field(default="Engineering")
    related_component: str | None = None
    related_initiative_id: str | None = None


class TechRiskResponse(BaseModel):
    risk_id: str
    risk: str
    likelihood: str
    impact: str


class DriftItemSchema(BaseModel):
    requirement_ref: str
    requirement_text: str
    expected_status: str
    actual_status: str
    drift_type: str
    details: str


class DriftAnalysisResponse(BaseModel):
    prd_entity_id: str
    total_drift_items: int
    drift_items: list[DriftItemSchema]


class BlockerSchema(BaseModel):
    blocked_entity_id: str
    blocked_name: str
    blocking_entity_id: str
    blocking_name: str
    blocked_since: str | None
    age_days: int
    severity: str


class BlockerAnalysisResponse(BaseModel):
    epic_entity_id: str
    total_blockers: int
    blockers: list[BlockerSchema]


class HandoffRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="Requirements")
    objective: str | None = Field(default=None, description="Engineering objective")


class HandoffEpicSchema(BaseModel):
    epic_id: str
    title: str
    story_count: int
    stories: list[dict]


class HandoffResponse(BaseModel):
    initiative_name: str
    prd_reference: str
    objective: str
    architecture_impact: str
    affected_components: list[str]
    new_components: list[str]
    dependencies: list[str]
    data_model_changes: list[str]
    events: list[str]
    observability: list[str]
    rollback_strategy: str
    epics: list[dict]
    total_stories: int
    total_estimated_hours: float
    estimate_confidence: str
    risks: list[dict]
    open_questions: list[str]
# ─── QA & Release Intelligence Schemas (PRD-0010) ──────────────


class TestStrategyRequest(BaseModel):
    prd_entity_id: str = Field(..., description="ID of the PRD entity")
    prd_title: str = Field(..., description="Title of the PRD")
    requirements: list[RequirementInput] = Field(..., description="Requirements to base strategy on")


class TestStrategyResponse(BaseModel):
    prd_entity_id: str
    prd_title: str
    risk_level: str
    test_levels: list[str]
    automation_required: bool
    estimated_test_effort_hours: float
    key_risk_areas: list[str]
    testing_approach: str
    exit_criteria: list[str]
    assumptions: list[str]


class TestCaseRequest(BaseModel):
    requirement_ref: str = Field(..., description="Requirement reference")
    requirement_text: str = Field(..., description="Requirement description")
    acceptance_criteria: list[str] | None = Field(default=None)


class TestCaseSchema(BaseModel):
    test_case_id: str
    requirement_ref: str
    title: str
    test_level: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    scenario_type: str
    priority: str
    is_automatable: bool


class TestCaseResponse(BaseModel):
    requirement_ref: str
    test_cases: list[TestCaseSchema]
    total_cases: int


class QualityRiskRequest(BaseModel):
    requirement_ref: str = Field(..., description="Requirement reference")
    requirement_text: str = Field(..., description="Requirement description")


class QualityRiskResponse(BaseModel):
    requirement_ref: str
    requirement_text: str
    impact: str
    likelihood: str
    uncertainty: str
    risk_level: str
    reasoning: str
    recommended_test_depth: str


class DefectRequest(BaseModel):
    title: str = Field(..., description="Defect title")
    description: str = Field(..., description="Defect description")
    requirement_ref: str | None = Field(default=None)
    severity: str = Field(default="MEDIUM", description="CRITICAL, HIGH, MEDIUM, LOW")
    priority: str = Field(default="P2", description="P0, P1, P2, P3, P4")
    steps_to_reproduce: list[str] = Field(..., description="Steps to reproduce")
    expected_behavior: str = Field(..., description="Expected behavior")
    actual_behavior: str = Field(..., description="Actual behavior")
    environment: str = Field(default="staging")
    is_regression: bool = Field(default=False)
    root_cause_category: str | None = Field(default=None)


class DefectResponse(BaseModel):
    defect_id: str
    title: str
    severity: str
    priority: str
    is_regression: bool


class DefectClassifyRequest(BaseModel):
    description: str = Field(..., description="Defect description to classify")


class DefectClassifyResponse(BaseModel):
    severity: str
    priority: str
    is_regression: bool
    root_cause_category: str
    affected_component: str
    similar_defects: list[str]


class RegressionSetRequest(BaseModel):
    change_scope: str = Field(..., description="Description of the change scope")
    total_test_count: int = Field(default=100)


class RegressionSetResponse(BaseModel):
    change_scope: str
    selected_test_count: int
    test_categories: list[str]
    rationale: str
    estimated_execution_hours: float
    risk_areas: list[str]


class ReleaseReadinessRequest(BaseModel):
    release_name: str = Field(..., description="Name of the release")
    total_tests: int = Field(..., description="Total tests executed")
    passed_tests: int = Field(..., description="Number of passed tests")
    failed_tests: int = Field(..., description="Number of failed tests")
    blocked_tests: int = Field(..., description="Number of blocked tests")
    critical_defects: int = Field(..., description="Open critical defects")
    high_defects: int = Field(..., description="Open high defects")
    total_requirements: int = Field(..., description="Total requirements in scope")
    covered_requirements: int = Field(..., description="Requirements with test coverage")


class QualityGateSchema(BaseModel):
    gate_name: str
    criteria: str
    status: str
    evidence: str
    override_reason: str | None
    override_approver: str | None


class ReleaseReadinessResponse(BaseModel):
    release_name: str
    overall_status: str
    test_pass_rate: float
    open_critical_defects: int
    open_high_defects: int
    coverage_percent: float
    quality_gates: list[QualityGateSchema]
    passed_gates: int
    failed_gates: int
    risks: list[str]
    recommendation: str


class CoverageRequest(BaseModel):
    requirements: list[RequirementInput] = Field(..., description="Requirements in scope")
    tested_requirements: list[str] = Field(..., description="List of requirement IDs that have test coverage")


class CoverageResponse(BaseModel):
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: list[str]
    coverage_percent: float
    coverage_by_level: dict[str, int]
    recommendation: str


class TraceabilityResponse(BaseModel):
    requirement_ref: str
    requirement_text: str
    linked_test_cases: list[str]
    test_results: list[dict[str, str]]
    is_fully_covered: bool


class IncidentTraceRequest(BaseModel):
    incident_description: str = Field(..., description="Description of the production incident")


class IncidentTraceResponse(BaseModel):
    incident_description: str
    probable_root_cause: str
    related_requirements: list[str]
    test_gaps: list[str]
    existing_tests: list[str]
    recommended_new_tests: list[str]
    quality_learning: str


# ─── Analytics & Outcome Intelligence Schemas (PRD-0011) ──────────────

class KPIRequest(BaseModel):
    name: str = Field(..., description="KPI name")
    description: str = Field(..., description="KPI description")
    formula: str = Field(..., description="Calculation formula")
    unit: str = Field(..., description="Unit of measurement")
    baseline: float | None = None
    target: float | None = None
    measurement_period: str = "weekly"

class KPIResponse(BaseModel):
    name: str
    description: str
    formula: str
    unit: str
    baseline: float | None
    target: float | None
    measurement_period: str
    status: str

class EventRequest(BaseModel):
    name: str = Field(..., description="Event name")
    description: str = Field(..., description="Event description")
    trigger: str = Field(..., description="Trigger condition")
    properties: list[str] = Field(default_factory=list)
    required_properties: list[str] = Field(default_factory=list)
    source: str = "frontend"

class EventResponse(BaseModel):
    name: str
    description: str
    trigger: str
    properties: list[str]
    required_properties: list[str]
    source: str

class InstrumentationRequest(BaseModel):
    prd_entity_id: str
    requirements: list[RequirementInput]

class InstrumentationResponse(BaseModel):
    prd_entity_id: str
    events: list[EventResponse]
    identity_rules: list[str]
    deduplication_rules: list[str]
    acceptance_criteria: list[str]

class OutcomeHypothesisRequest(BaseModel):
    initiative_name: str
    action: str
    target_segment: str
    expected_behavior_change: str
    expected_outcome: str
    primary_metric: str
    guardrails: list[str]

class OutcomeHypothesisResponse(BaseModel):
    initiative_name: str
    hypothesis_if: str
    hypothesis_for_segment: str
    hypothesis_then_behavior: str
    hypothesis_which_improves: str
    measured_by_metric: str
    guardrails: list[str]

class ExperimentRequest(BaseModel):
    hypothesis: OutcomeHypothesisResponse
    min_sample_size: int = 1000
    duration_days: int = 14

class ExperimentResponse(BaseModel):
    hypothesis: OutcomeHypothesisResponse
    target_population: str
    control_variant: str
    treatment_variant: str
    primary_metric: str
    secondary_metrics: list[str]
    guardrails: list[str]
    min_sample_size: int
    duration_days: int
    success_criteria: list[str]

class ExperimentEvalRequest(BaseModel):
    experiment_id: str
    control_value: float
    treatment_value: float
    is_statistically_significant: bool
    guardrails_passed: bool

class ExperimentEvalResponse(BaseModel):
    experiment_id: str
    observed_effect: str
    statistical_significance: bool
    confidence_level: str
    guardrails_ok: bool
    decision: str
    reasoning: str
    learning: str

class FunnelRequest(BaseModel):
    steps: list[str]
    users_at_steps: list[int]

class FunnelResponse(BaseModel):
    steps: list[str]
    conversion_rates: list[float]
    overall_conversion: float
    largest_dropoff_step: str
    anomaly_detected: bool
    insights: list[str]

class RetentionRequest(BaseModel):
    cohort_name: str
    d1_rate: float
    d7_rate: float
    d30_rate: float

class RetentionResponse(BaseModel):
    cohort_name: str
    retention_d1: float
    retention_d7: float
    retention_d30: float
    trend: str
    insights: list[str]

class FeatureAdoptionRequest(BaseModel):
    feature_name: str
    eligible_users: int
    exposed_users: int
    tried_users: int
    retained_users: int

class FeatureAdoptionResponse(BaseModel):
    feature_name: str
    eligible_users: int
    exposed_users: int
    tried_users: int
    retained_users: int
    adoption_rate: float
    primary_state: str
    recommendation: str

class AnomalyRequest(BaseModel):
    metric_name: str
    baseline_value: float
    observed_value: float

class AnomalyResponse(BaseModel):
    metric_name: str
    baseline_value: float
    observed_value: float
    magnitude_pct: float
    is_anomaly: bool
    potential_causes: list[str]

class CorrelationRequest(BaseModel):
    anomaly: AnomalyResponse
    recent_releases: list[str]

class CorrelationResponse(BaseModel):
    anomaly: AnomalyResponse
    recent_releases: list[str]
    correlation_strength: str
    investigation_steps: list[str]

class ScorecardRequest(BaseModel):
    initiative_name: str
    baseline: float
    target: float
    current: float
    guardrail_violations: int = 0

class ScorecardResponse(BaseModel):
    initiative_name: str
    baseline: float
    target: float
    current: float
    progress_pct: float
    status: str
    guardrail_status: str
    recommendation: str

class StrategicLearningResponse(BaseModel):
    source: str
    learning: str
    confidence: str
    affected_decisions: list[str]


# ─── Customer Intelligence Schemas (PRD-0012) ─────────────────

class SignalIngestRequest(BaseModel):
    customer_id: str = Field(..., description="Customer or Organization ID")
    source: str = Field(..., description="Source system (e.g. Zendesk, Salesforce)")
    source_reference: str = Field(..., description="Source ticket or email ID")
    raw_text: str = Field(..., description="Raw text of the customer signal")

class SignalIngestResponse(BaseModel):
    workspace_id: str
    customer_id: str
    source: str
    source_reference: str
    signal_type: str
    summary: str
    urgency: str
    sentiment: str

class ProblemExtractRequest(BaseModel):
    signal: SignalIngestResponse

class ProblemExtractResponse(BaseModel):
    signal_id: str
    problem_statement: str
    affected_workflow: str
    frequency: str
    workaround_exists: bool

class ImpactEstimateRequest(BaseModel):
    problem: ProblemExtractResponse

class ImpactEstimateResponse(BaseModel):
    problem_statement: str
    time_impact: str
    cost_impact: str
    revenue_impact: str
    user_frustration: str
    severity: str

class OpportunityExtractRequest(BaseModel):
    problem: ProblemExtractResponse

class OpportunityExtractResponse(BaseModel):
    problem_statement: str
    potential_opportunity: str
    strategic_alignment: str
    confidence: str

class ChurnRiskRequest(BaseModel):
    signals: list[SignalIngestResponse]

class ChurnRiskResponse(BaseModel):
    customer_id: str
    risk_level: str
    primary_reason: str
    contributing_factors: list[str]
    recommended_action: str

class FeatureEvalRequest(BaseModel):
    raw_request: str

class FeatureEvalResponse(BaseModel):
    requested_feature: str
    underlying_problem: str
    is_genuine_problem: bool
    alternative_solutions: list[str]

class AccountSummaryRequest(BaseModel):
    account_id: str
    signals: list[SignalIngestResponse]

class AccountSummaryResponse(BaseModel):
    account_id: str
    total_signals: int
    primary_problems: list[str]
    overall_sentiment: str
    churn_risk: str

class TraceRequest(BaseModel):
    customer_id: str

class TraceResponse(BaseModel):
    customer_id: str
    signals: list[str]
    influenced_requirements: list[str]
    shipped_features: list[str]


# ─── Strategy & Roadmap Schemas (PRD-0007) ───────────────────────

class ThemeCreateRequest(BaseModel):
    name: str = Field(..., description="Theme title, e.g. Enterprise Expansion")
    description: str = Field(..., description="Theme rationale and focus")
    priority: str = Field(default="HIGH")
    time_horizon: str = Field(default="6_12_MONTHS")
    success_metrics: list[str] = Field(default_factory=list)

class ThemeResponse(BaseModel):
    theme_id: str
    name: str
    description: str
    priority: str
    time_horizon: str
    success_metrics: list[str]

class ObjectiveCreateRequest(BaseModel):
    name: str
    theme_id: str | None = None
    objective_type: str = "growth"
    description: str = ""
    baseline: float = 0.0
    target: float = 0.0
    unit: str = "%"
    deadline: str | None = None
    owner: str = "Product Office"

class ObjectiveResponse(BaseModel):
    objective_id: str
    name: str
    theme_id: str | None
    objective_type: str
    baseline: float
    target: float
    unit: str
    deadline: str | None
    owner: str

class StrategicBetCreateRequest(BaseModel):
    name: str
    hypothesis: str
    strategic_theme_id: str | None = None
    expected_outcomes: list[str] = Field(default_factory=list)
    investment_size: str = "MEDIUM"
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = 0.70
    status: str = "HYPOTHESIS"

class StrategicBetResponse(BaseModel):
    bet_id: str
    name: str
    hypothesis: str
    strategic_theme_id: str | None
    investment_size: str
    confidence: float
    status: str
    expected_outcomes: list[str]

class BetEvaluateRequest(BaseModel):
    name: str
    hypothesis: str
    evidence_strength: float = 0.7
    investment_size: str = "MEDIUM"
    market_uncertainty: float = 0.5

class BetEvaluateResponse(BaseModel):
    bet_name: str
    viability_score: float
    recommendation: str
    evidence_strength: float
    market_uncertainty: float
    validation_milestones: list[str]

class AssumptionCreateRequest(BaseModel):
    statement: str
    category: str = "MARKET"
    confidence: str = "MEDIUM"
    validation_criteria: str = ""

class AssumptionResponse(BaseModel):
    assumption_id: str
    statement: str
    category: str
    confidence: str
    status: str

class StrategicAlignRequest(BaseModel):
    initiative_name: str
    problem_statement: str
    linked_theme: str | None = None
    linked_objective: str | None = None
    has_validated_evidence: bool = False

class StrategicAlignResponse(BaseModel):
    initiative_name: str
    alignment_score: float
    alignment_level: str
    dimension_scores: dict[str, float]
    gap_analysis: list[str]
    is_constitutionally_sound: bool

class RoadmapInitiativeItem(BaseModel):
    id: str | None = None
    name: str
    theme: str | None = None
    objective: str | None = None
    status: str = "active"
    confidence: str = "confirmed"
    dependencies: list[str] = Field(default_factory=list)

class RoadmapGenerateRequest(BaseModel):
    initiatives: list[RoadmapInitiativeItem] | None = None

class RoadmapResponse(BaseModel):
    summary: str
    horizons: dict[str, list[dict]]
    total_initiatives: int
    now_count: int
    next_count: int
    later_count: int

class StrategicDriftRequest(BaseModel):
    initiatives: list[RoadmapInitiativeItem]
    active_themes: list[str]

class StrategicDriftResponse(BaseModel):
    total_initiatives: int
    aligned_count: int
    unaligned_count: int
    drift_percentage: float
    drift_level: str
    aligned_initiatives: list[str]
    unaligned_initiatives: list[str]
    recommendations: list[str]

class PortfolioBalanceRequest(BaseModel):
    allocations: dict[str, float]

class PortfolioBalanceResponse(BaseModel):
    status: str
    distribution: dict[str, float]
    warnings: list[str]
    is_sustainable: bool


# ─── Connector Schemas (PRD-0004) ────────────────────────────────

class ConnectorRegisterRequest(BaseModel):
    connector_type: str = Field(..., description="gmail, slack, jira, github, calendar")
    display_name: str
    config: dict = Field(default_factory=dict)

class ConnectorResponse(BaseModel):
    connector_id: str
    connector_type: str
    display_name: str
    status: str
    config: dict

class ConnectorSyncItem(BaseModel):
    channel: str
    sender: str
    content: str
    timestamp: str | None = None
    thread_id: str | None = None
    metadata: dict = Field(default_factory=dict)

class ConnectorSyncRequest(BaseModel):
    items: list[ConnectorSyncItem]

class DetectedCommitmentSchema(BaseModel):
    deliverable: str
    owner: str
    due_date: str | None
    statement: str

class ConnectorSyncResponse(BaseModel):
    processed_count: int
    signals_ingested: int
    commitments_detected: int
    detected_commitments: list[DetectedCommitmentSchema]

class CommitmentDetectRequest(BaseModel):
    text: str
    default_owner: str = "Unknown"

class CommitmentDetectResponse(BaseModel):
    commitments_found: int
    commitments: list[DetectedCommitmentSchema]

class InternalActionDraftRequest(BaseModel):
    action_type: str = Field(..., description="EMAIL_DRAFT, SLACK_DRAFT, JIRA_ISSUE_DRAFT, GITHUB_PR_COMMENT_DRAFT")
    target: str
    context: str
    user_intent: str

class InternalActionDraftResponse(BaseModel):
    action_type: str
    target: str
    subject: str | None = None
    summary: str | None = None
    issue_type: str | None = None
    draft_body: str
    requires_human_approval: bool
    dispatched: bool


# ─── Workspace & RBAC Schemas (PRD-0003) ─────────────────────────

class WorkspaceInfoResponse(BaseModel):
    workspace_id: str
    name: str
    owner_email: str
    owner_name: str
    workspace_type: str
    created_at: str | None

class WorkspaceStatsResponse(BaseModel):
    workspace_id: str
    total_entities: int
    total_relationships: int
    total_connectors: int
    entities_by_type: dict[str, int]

class WorkspaceExportResponse(BaseModel):
    exported_at: str
    workspace_id: str
    entities: list[dict]
    relationships: list[dict]

class WorkspaceResetResponse(BaseModel):
    workspace_id: str
    deleted_entities_count: int
    status: str

class RBACCheckRequest(BaseModel):
    role: str = Field(..., description="CEO, SR_PM, JR_PM, QA_LEAD, VIEWER")
    resource: str = Field(..., description="roadmap, prd, client_contracts, budget, sprint_analytics, decisions")

class RBACCheckResponse(BaseModel):
    role: str
    resource: str
    permission_level: str
    is_authorized: bool

