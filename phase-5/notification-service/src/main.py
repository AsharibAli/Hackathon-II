# [Task]: T091
# [Spec]: F-009 (R-009.1)
# [Description]: Notification service FastAPI application
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import configure_logging, get_logger
from .api.health import router as health_router
from .api.reminders import router as reminders_router

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
    description="Notification service for TaskAI - receives reminder events via Dapr pub/sub",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(reminders_router)


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
            "topic": "reminders",
            "route": "/api/reminders/handle",
        }
    ]
