"""
Connector Intelligence Framework API — PRD-0004

Endpoints:
- POST /connectors: Register external connector
- GET /connectors: List connectors in workspace
- POST /connectors/sync: Ingest multi-channel raw stream into signals & commitments
- POST /connectors/commitments/detect: Detect commitments in text
- POST /connectors/actions/draft: Generate internal drafts for PM review (Email, Slack, Jira)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_workspace_id
from app.models.connector import ConnectorType
from app.services.connector_engine import (
    ConnectorIntelligenceEngine,
    IngestionBatchItem,
    InternalActionType,
)
from app.schemas import (
    ConnectorRegisterRequest,
    ConnectorResponse,
    ConnectorSyncRequest,
    ConnectorSyncResponse,
    CommitmentDetectRequest,
    CommitmentDetectResponse,
    DetectedCommitmentSchema,
    InternalActionDraftRequest,
    InternalActionDraftResponse,
)

router = APIRouter(prefix="/connectors", tags=["Connectors"])


@router.post("", response_model=ConnectorResponse)
async def register_connector(
    request: ConnectorRegisterRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Registers an authorized connector for the current workspace."""
    engine = ConnectorIntelligenceEngine(db=db, workspace_id=workspace_id)
    try:
        c_type = ConnectorType(request.connector_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid connector type '{request.connector_type}'. Must be one of: {[e.value for e in ConnectorType]}",
        )

    res = await engine.register_connector(
        connector_type=c_type,
        display_name=request.display_name,
        config=request.config,
    )
    return ConnectorResponse(**res)


@router.get("", response_model=list[dict])
async def list_connectors(
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """Lists all connectors active in the workspace."""
    engine = ConnectorIntelligenceEngine(db=db, workspace_id=workspace_id)
    return await engine.list_connectors()


@router.post("/sync", response_model=ConnectorSyncResponse)
async def sync_connector_items(
    request: ConnectorSyncRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingests raw communication items from Gmail, Slack, Jira, GitHub, or Calendar.
    Extracts signals and automatically detects commitments.
    """
    engine = ConnectorIntelligenceEngine(db=db, workspace_id=workspace_id)
    items = [
        IngestionBatchItem(
            channel=i.channel,
            sender=i.sender,
            content=i.content,
            timestamp=i.timestamp,
            thread_id=i.thread_id,
            metadata=i.metadata,
        )
        for i in request.items
    ]
    res = await engine.ingest_batch(items)
    return ConnectorSyncResponse(
        processed_count=res["processed_count"],
        signals_ingested=res["signals_ingested"],
        commitments_detected=res["commitments_detected"],
        detected_commitments=[
            DetectedCommitmentSchema(**c) for c in res["detected_commitments"]
        ],
    )


@router.post("/commitments/detect", response_model=CommitmentDetectResponse)
async def detect_commitments(
    request: CommitmentDetectRequest,
):
    """Analyzes text to detect explicit promises, deliverables, and due dates."""
    engine = ConnectorIntelligenceEngine()
    detected = engine.detect_commitments_in_text(request.text, default_owner=request.default_owner)
    return CommitmentDetectResponse(
        commitments_found=len(detected),
        commitments=[
            DetectedCommitmentSchema(
                deliverable=d.deliverable,
                owner=d.owner,
                due_date=d.due_date,
                statement=d.statement,
            )
            for d in detected
        ],
    )


@router.post("/actions/draft", response_model=InternalActionDraftResponse)
async def draft_internal_action(
    request: InternalActionDraftRequest,
):
    """
    Generates an internal draft for user review.
    Guaranteed: No autonomous external communication.
    """
    engine = ConnectorIntelligenceEngine()
    try:
        a_type = InternalActionType(request.action_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action type '{request.action_type}'. Must be one of: {[e.value for e in InternalActionType]}",
        )

    res = engine.draft_internal_action(
        action_type=a_type,
        recipient_or_target=request.target,
        context=request.context,
        user_intent=request.user_intent,
    )
    return InternalActionDraftResponse(**res)
