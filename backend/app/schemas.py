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
    OBJECTIVE = "objective"
    STRATEGIC_BET = "strategic_bet"
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


