"""
TPG Domain Intelligence Services

Implements:
- Requirement Intelligence Engine (PRD-0005)
- Product Decision Engine (PRD-0006)
- PRD & Product Specification Engine (PRD-0008)
- Engineering Intelligence Engine (PRD-0009)
"""

from app.services.requirement_engine import (
    RequirementIntelligenceEngine,
    RequirementType,
    DiscoveryState,
    ProblemStatement,
    JTBDStatement,
    AmbiguityAnalysis,
)
from app.services.decision_engine import (
    ProductDecisionEngine,
    DecisionType,
    DecisionOutcome,
    SolutionOption,
    DecisionRecord,
)
from app.services.prd_engine import (
    PRDSpecificationEngine,
    PRDReadinessLevel,
    PRDStatus,
    PRDDocument,
    PRDScope,
    FunctionalRequirement,
    AcceptanceCriterion,
    PRDReadinessAssessment,
)
from app.services.engineering_engine import (
    EngineeringIntelligenceEngine,
    EngineeringPhase,
    ADRStatus,
    TechDebtSeverity,
    EstimateConfidence,
    DependencyType,
    TechnicalAnalysis,
    TechnicalDesign,
    ArchitectureDecision,
    EngineeringBreakdown,
    EpicBreakdown,
    StorySpec,
    DependencyEdge,
    TechDebtItem,
    TechnicalRisk,
    EffortEstimate,
    CapacityAnalysis,
    HandoffDocument,
)

__all__ = [
    "RequirementIntelligenceEngine",
    "RequirementType",
    "DiscoveryState",
    "ProblemStatement",
    "JTBDStatement",
    "AmbiguityAnalysis",
    "ProductDecisionEngine",
    "DecisionType",
    "DecisionOutcome",
    "SolutionOption",
    "DecisionRecord",
    "PRDSpecificationEngine",
    "PRDReadinessLevel",
    "PRDStatus",
    "PRDDocument",
    "PRDScope",
    "FunctionalRequirement",
    "AcceptanceCriterion",
    "PRDReadinessAssessment",
    "EngineeringIntelligenceEngine",
    "EngineeringPhase",
    "ADRStatus",
    "TechDebtSeverity",
    "EstimateConfidence",
    "DependencyType",
    "TechnicalAnalysis",
    "TechnicalDesign",
    "ArchitectureDecision",
    "EngineeringBreakdown",
    "EpicBreakdown",
    "StorySpec",
    "DependencyEdge",
    "TechDebtItem",
    "TechnicalRisk",
    "EffortEstimate",
    "CapacityAnalysis",
    "HandoffDocument",
]

