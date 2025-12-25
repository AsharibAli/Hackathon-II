# [Task]: T096
# [Spec]: F-010 (R-010.1)
# [Description]: Recurring service FastAPI application
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import configure_logging, get_logger
from .api.health import router as health_router
from .api.events import router as events_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    configure_logging()
    logger.info(
        "service_starting",
        service=settings.app_name,
        version=settings.app_version,
    )
    yield
    logger.info("service_stopping", service=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Recurring task service for TaskAI - creates next occurrence on task completion",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(events_router)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/dapr/subscribe")
async def dapr_subscribe() -> list:
    """
    Dapr subscription endpoint (programmatic fallback).

    Note: We use declarative subscriptions via Kubernetes CRD,
    but this endpoint serves as a fallback for local development.
    """
    return [
        {
            "pubsubname": settings.pubsub_name,
            "topic": "task-events",
            "route": "/api/events/task",
        }
    ]
