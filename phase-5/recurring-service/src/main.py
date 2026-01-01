# [Task]: T096, T130
# [Spec]: F-010 (R-010.1), F-011
# [Description]: Recurring service with graceful shutdown
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import configure_logging, get_logger

logger = get_logger(__name__)

# Graceful shutdown timeout (seconds)
SHUTDOWN_TIMEOUT = 15

# Global flag for shutdown state
_shutting_down = False
_active_requests = 0


def increment_active_requests():
    """Increment active request counter."""
    global _active_requests
    _active_requests += 1


def decrement_active_requests():
    """Decrement active request counter."""
    global _active_requests
    _active_requests -= 1


async def wait_for_active_requests():
    """Wait for active requests to complete."""
    check_interval = 0.5
    elapsed = 0

    while _active_requests > 0 and elapsed < SHUTDOWN_TIMEOUT:
        logger.info(
            "waiting_for_requests",
            active_requests=_active_requests,
            elapsed=elapsed,
        )
        await asyncio.sleep(check_interval)
        elapsed += check_interval

    if _active_requests > 0:
        logger.warning(
            "shutdown_timeout",
            remaining_requests=_active_requests,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler with graceful shutdown."""
    global _shutting_down

    configure_logging()
    logger.info(
        "service_starting",
        service=settings.app_name,
        version=settings.app_version,
    )

    yield

    # Graceful shutdown
    _shutting_down = True
    logger.info(
        "graceful_shutdown_initiated",
        service=settings.app_name,
    )

    # Wait for active requests to complete
    await wait_for_active_requests()

    logger.info(
        "service_stopped",
        service=settings.app_name,
    )


# Import routers after lifespan to avoid circular imports
from .api.health import router as health_router
from .api.events import router as events_router


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
