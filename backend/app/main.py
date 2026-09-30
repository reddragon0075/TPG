"""
TPG — The Product Guy

FastAPI Application Entry Point

This is the main server that powers TPG's intelligence.
ChatGPT calls this via the Actions API. Every endpoint
is workspace-scoped and API-key authenticated.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api.health import router as health_router
from app.api.memory import router as memory_router
from app.api.intelligence import router as intelligence_router
from app.api.engineering import router as engineering_router
from app.api.qa import router as qa_router
from app.api.analytics import router as analytics_router
from app.api.customer import router as customer_router
from app.api.strategy import router as strategy_router
from app import models as _models  # noqa: F401
from app.api.connectors import router as connectors_router
from app.api.workspace import router as workspace_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Creates database tables on startup (dev mode).
    Production should use Alembic migrations.
    """
    # Startup
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "TPG Backend Intelligence Service. "
        "Powers the Knowledge Graph, Connector Framework, "
        "and Specialist Agent orchestration behind the "
        "unified TPG identity in ChatGPT."
    ),
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ─── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(memory_router)
app.include_router(intelligence_router)
app.include_router(engineering_router)
app.include_router(qa_router)
app.include_router(analytics_router)
app.include_router(customer_router)
app.include_router(strategy_router)
app.include_router(connectors_router)
app.include_router(workspace_router)


# ─── Root ──────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs" if settings.debug else "disabled",
    }
