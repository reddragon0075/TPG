"""
Health API

System health check and basic diagnostics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.entity import Entity
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check.

    Verifies database connectivity and returns basic system info.
    Called by monitoring and by the Custom GPT to verify availability.
    """
    db_status = "connected"
    entity_count = 0

    try:
        # Verify DB connectivity
        await db.execute(text("SELECT 1"))

        # Count entities
        result = await db.execute(select(func.count(Entity.id)))
        entity_count = result.scalar() or 0
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.app_version,
        database=db_status,
        entity_count=entity_count,
    )
