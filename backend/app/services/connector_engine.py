"""
Connector Intelligence Framework Engine (CIFE) — PRD-0004

Implements:
1. Connector Lifecycle & OAuth State (PRD-0004 §4, §91-§107)
2. Multi-Channel Signal Ingestion (Gmail, Slack, Jira, GitHub, Calendar) (PRD-0004 §110-§144)
3. Automatic Commitment Detection & Tracking (PRD-0004 §146-§155, PRD-0001 §370-§384)
4. Internal Action Execution & Draft Generation (PRD-0004 §28-§30, §37-§47)

Constitutional Principle:
- Read everywhere. Understand intelligently. Act internally (PRD-0004 §37).
- TPG never communicates autonomously with external clients.
- Raw messages are never the source of truth; TPG Memory is.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connector import Connector, ConnectorType, ConnectorStatus
from app.models.entity import (
    Entity,
    EntityType,
    ConfidenceLevel,
    EntityStatus,
    EntityRelationship,
    RelationshipType,
)


# ─── Enums ─────────────────────────────────────────────────────────

class CommitmentStatus(str, Enum):
    PENDING = "PENDING"
    REMINDER_SENT = "REMINDER_SENT"
    FULFILLED = "FULFILLED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class InternalActionType(str, Enum):
    EMAIL_DRAFT = "EMAIL_DRAFT"
    SLACK_DRAFT = "SLACK_DRAFT"
    JIRA_ISSUE_DRAFT = "JIRA_ISSUE_DRAFT"
    GITHUB_PR_COMMENT_DRAFT = "GITHUB_PR_COMMENT_DRAFT"


# ─── Dataclasses ───────────────────────────────────────────────────

@dataclass
class DetectedCommitment:
    statement: str
    owner: str
    deliverable: str
    due_date: str | None = None
    confidence: float = 0.85
    source_channel: str = "slack"


@dataclass
class IngestionBatchItem:
    channel: str  # gmail, slack, jira, github, calendar
    sender: str
    content: str
    timestamp: str | None = None
    thread_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ─── Connector Engine Implementation ───────────────────────────────

class ConnectorIntelligenceEngine:
    """
    Manages external connectors, ingests continuous streams into knowledge graph signals,
    and extracts commitments and internal drafts without external leakage.
    """

    def __init__(self, db: AsyncSession | None = None, workspace_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id

    # ─── 1. Connector Lifecycle ────────────────────────────────────

    async def register_connector(
        self,
        connector_type: ConnectorType,
        display_name: str,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Registers a new connector connection in the workspace."""
        conn_id = str(uuid.uuid4())
        cfg = config or {}

        if self.db and self.workspace_id:
            connector = Connector(
                id=conn_id,
                workspace_id=self.workspace_id,
                connector_type=connector_type,
                display_name=display_name,
                status=ConnectorStatus.CONNECTED,
                config=cfg,
                last_synced_at=datetime.now(timezone.utc),
            )
            self.db.add(connector)
            await self.db.flush()

        return {
            "connector_id": conn_id,
            "connector_type": connector_type.value,
            "display_name": display_name,
            "status": ConnectorStatus.CONNECTED.value,
            "config": cfg,
        }

    async def list_connectors(self) -> list[dict[str, Any]]:
        """Lists all registered connectors in current workspace."""
        if not self.db or not self.workspace_id:
            return []

        stmt = select(Connector).where(Connector.workspace_id == self.workspace_id)
        res = await self.db.execute(stmt)
        connectors = res.scalars().all()

        return [
            {
                "id": c.id,
                "connector_type": c.connector_type.value,
                "display_name": c.display_name,
                "status": c.status.value,
                "last_synced_at": c.last_synced_at.isoformat() if c.last_synced_at else None,
                "is_active": c.is_active,
            }
            for c in connectors
        ]

    # ─── 2. Multi-Channel Signal Ingestion ─────────────────────────

    async def ingest_batch(
        self,
        items: list[IngestionBatchItem],
    ) -> dict[str, Any]:
        """
        Ingests a batch of raw communication items (Slack, Gmail, Jira, GitHub)
        and translates them into Knowledge Graph signals and detected commitments.
        """
        created_signals = []
        detected_commitments = []

        for item in items:
            # 1. Store as signal
            signal_id = str(uuid.uuid4())
            props = {
                "channel": item.channel,
                "sender": item.sender,
                "raw_content": item.content,
                "thread_id": item.thread_id,
                "metadata": item.metadata,
            }

            if self.db and self.workspace_id:
                entity = Entity(
                    id=signal_id,
                    workspace_id=self.workspace_id,
                    entity_type=EntityType.SIGNAL,
                    name=f"[{item.channel.upper()}] Signal from {item.sender}",
                    description=item.content[:500],
                    properties=props,
                    confidence=ConfidenceLevel.CONFIRMED,
                    status=EntityStatus.ACTIVE,
                )
                self.db.add(entity)

            created_signals.append({
                "signal_id": signal_id,
                "channel": item.channel,
                "sender": item.sender,
            })

            # 2. Check for commitments in text
            detected = self.detect_commitments_in_text(item.content, default_owner=item.sender)
            for c in detected:
                c.source_channel = item.channel
                detected_commitments.append(c)
                # Store commitment entity
                if self.db and self.workspace_id:
                    com_id = str(uuid.uuid4())
                    com_entity = Entity(
                        id=com_id,
                        workspace_id=self.workspace_id,
                        entity_type=EntityType.COMMITMENT,
                        name=f"Commitment: {c.deliverable[:80]}",
                        description=c.statement,
                        properties={
                            "owner": c.owner,
                            "deliverable": c.deliverable,
                            "due_date": c.due_date,
                            "status": CommitmentStatus.PENDING.value,
                            "channel": item.channel,
                        },
                        confidence=ConfidenceLevel.INFERRED,
                        status=EntityStatus.ACTIVE,
                    )
                    self.db.add(com_entity)
                    # Link signal to commitment
                    rel = EntityRelationship(
                        source_entity_id=signal_id,
                        target_entity_id=com_id,
                        relationship_type=RelationshipType.CREATED_FROM,
                        properties={"source": "auto_detected_commitment"},
                    )
                    self.db.add(rel)

        if self.db:
            await self.db.flush()

        return {
            "processed_count": len(items),
            "signals_ingested": len(created_signals),
            "commitments_detected": len(detected_commitments),
            "detected_commitments": [
                {
                    "deliverable": dc.deliverable,
                    "owner": dc.owner,
                    "due_date": dc.due_date,
                    "statement": dc.statement,
                }
                for dc in detected_commitments
            ],
        }

    # ─── 3. Automatic Commitment Detection ─────────────────────────

    def detect_commitments_in_text(
        self,
        text: str,
        default_owner: str = "Unknown",
    ) -> list[DetectedCommitment]:
        """
        Scans communication text for promises and commitments (PRD-0004 §146, PRD-0001 §370).
        Matches patterns like:
        - 'We will deliver X by [date]'
        - 'I will submit X tomorrow / on Monday'
        - 'We'll have the PRD ready by 15 Oct'
        """
        results: list[DetectedCommitment] = []
        patterns = [
            r"(?:we|i)(?:'ll| will| shall)\s+(?:submit|deliver|ship|complete|provide|have|finish)\s+(.*?)\s+(?:by|on|before)\s+([A-Za-z0-9\s,\-_]+?)(?:\.|$)",
            r"(?:promised|committed) to\s+(.*?)\s+(?:by|on)\s+([A-Za-z0-9\s,\-_]+?)(?:\.|$)",
            r"(?:will have)\s+(.*?)\s+(?:ready by)\s+([A-Za-z0-9\s,\-_]+?)(?:\.|$)",
        ]

        sentences = re.split(r"[.\n]+", text)
        for sent in sentences:
            sent_str = sent.strip()
            if not sent_str:
                continue
            for pat in patterns:
                m = re.search(pat, sent_str, re.IGNORECASE)
                if m:
                    deliverable = m.group(1).strip()
                    due_date = m.group(2).strip()
                    results.append(
                        DetectedCommitment(
                            statement=sent_str,
                            owner=default_owner,
                            deliverable=deliverable,
                            due_date=due_date,
                            confidence=0.85,
                        )
                    )
                    break

        return results

    # ─── 4. Internal Action Execution (Drafting Only) ──────────────

    def draft_internal_action(
        self,
        action_type: InternalActionType,
        recipient_or_target: str,
        context: str,
        user_intent: str,
    ) -> dict[str, Any]:
        """
        Generates an internal draft for user review (PRD-0004 §28-§30).
        Constitutional guarantee: Drafts are returned for human review, NEVER dispatched autonomously.
        """
        if action_type == InternalActionType.EMAIL_DRAFT:
            subject = f"Follow-up regarding {user_intent[:40]}"
            body = (
                f"Hi {recipient_or_target},\n\n"
                f"Regarding our recent discussion on {user_intent}:\n"
                f"We are evaluating the requirements against our current roadmap priorities.\n\n"
                f"Context note:\n{context}\n\n"
                f"Best regards,\n[Product Lead]"
            )
            return {
                "action_type": action_type.value,
                "target": recipient_or_target,
                "subject": subject,
                "draft_body": body,
                "requires_human_approval": True,
                "dispatched": False,
            }

        elif action_type == InternalActionType.JIRA_ISSUE_DRAFT:
            summary = f"Initiative: {user_intent}"
            desc = (
                f"h3. Background\n{context}\n\n"
                f"h3. Requirements\n- Driven by customer signals and strategic priorities.\n\n"
                f"h3. Acceptance Criteria\n- Verified against PRD specifications."
            )
            return {
                "action_type": action_type.value,
                "target": recipient_or_target,
                "summary": summary,
                "issue_type": "Story",
                "draft_body": desc,
                "requires_human_approval": True,
                "dispatched": False,
            }

        else:
            return {
                "action_type": action_type.value,
                "target": recipient_or_target,
                "draft_body": f"Internal Note: {user_intent}\nContext: {context}",
                "requires_human_approval": True,
                "dispatched": False,
            }
