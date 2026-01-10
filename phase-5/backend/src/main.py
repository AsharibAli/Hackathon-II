"""
Todo Backend API - FastAPI application entry point.
Initializes the FastAPI app with middleware, CORS, and route handlers.

[Task]: T075, T130, Cloud-Native Implementation
[Spec]: F-006, F-011
[Description]: Phase 5 with reminder scheduler, graceful shutdown, and full observability
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import create_db_and_tables
from core.logging import setup_logging, get_logger
from middleware.logging import LoggingMiddleware
from middleware.errors import ErrorHandlingMiddleware
from middleware.correlation import CorrelationMiddleware
from middleware.metrics import PrometheusMiddleware, get_metrics_route
from middleware.tracing import (
    setup_tracing,
    instrument_fastapi,
    instrument_httpx,
    shutdown_tracing,
)
from api import auth as auth_router
from api import tasks as tasks_router
from api import chat as chat_router
from api import conversations as conversations_router
from api import password_reset as password_reset_router
from api import health as health_router
from services.reminder_scheduler import reminder_scheduler
from services.events.publisher import event_publisher

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)

# Graceful shutdown timeout (seconds)
SHUTDOWN_TIMEOUT = 30

# Global flag for shutdown state
_shutting_down = False


async def graceful_shutdown():
    """Execute graceful shutdown of all services."""
    global _shutting_down
    if _shutting_down:
        return
    _shutting_down = True

    logger.info("Graceful shutdown started")

    try:
        # Create shutdown tasks with timeout
        async with asyncio.timeout(SHUTDOWN_TIMEOUT):
            # Stop reminder scheduler
            logger.info("Stopping reminder scheduler")
            await reminder_scheduler.stop()
            logger.info("Reminder scheduler stopped")

            # Close event publisher HTTP client
            logger.info("Closing event publisher")
            await event_publisher.close()
            logger.info("Event publisher closed")

            # Shutdown tracing (flush spans)
            logger.info("Shutting down tracing")
            shutdown_tracing()
            logger.info("Tracing shutdown complete")

    except asyncio.TimeoutError:
        logger.warning(f"Shutdown timeout after {SHUTDOWN_TIMEOUT} seconds")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

    logger.info("Graceful shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events with graceful handling.
    """
    # Startup
    logger.info(f"Application starting: {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize tracing
    logger.info("Initializing tracing")
    setup_tracing(app_name=settings.APP_NAME, app_version=settings.APP_VERSION)
    instrument_httpx()  # Instrument outgoing HTTP calls
    logger.info("Tracing initialized")

    # Create database tables
    logger.info("Creating database tables")
    create_db_and_tables()
    logger.info("Database tables created")

    # Start reminder scheduler (Phase 5)
    logger.info("Starting reminder scheduler")
    await reminder_scheduler.start()
    logger.info("Reminder scheduler started")

    logger.info("Application startup complete - ready")

    yield

    # Shutdown
    await graceful_shutdown()


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A modern, secure, multi-user AI-Powered Todo application with JWT authentication",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add custom middleware (order matters: last added runs first)
# PrometheusMiddleware runs first to capture all requests
# CorrelationMiddleware sets correlation ID for tracing
# LoggingMiddleware uses the correlation ID for logging
# ErrorHandlingMiddleware catches errors with correlation context
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationMiddleware)
app.add_middleware(PrometheusMiddleware, app_name=settings.APP_NAME, app_version=settings.APP_VERSION)

# Instrument FastAPI with OpenTelemetry
instrument_fastapi(app)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health checks."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


# API Routes
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(password_reset_router.router, prefix="/api/auth", tags=["Password Reset"])
app.include_router(tasks_router.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])
app.include_router(conversations_router.router, prefix="/api/conversations", tags=["Conversations"])

# Health check routes (for Kubernetes probes)
app.include_router(health_router.router, tags=["Health"])

# Observability Routes
app.include_router(get_metrics_route(), tags=["Observability"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
