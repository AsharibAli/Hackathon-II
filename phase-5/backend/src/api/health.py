# [Task]: T027
# [Spec]: F-011 (R-011.3)
# [Description]: Health check endpoints for backend service
"""
Health and readiness check endpoints for Kubernetes probes.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..core.database import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """
    Liveness probe endpoint.

    Returns basic health status. This endpoint should always return 200
    if the application is running.
    """
    return {
        "status": "healthy",
        "service": "todo-backend",
        "version": "2.0.0",
    }


@router.get("/ready")
async def readiness_check(
    session: Session = Depends(get_session)
) -> dict:
    """
    Readiness probe endpoint.

    Checks if the application is ready to receive traffic.
    Verifies database connectivity.
    """
    try:
        # Test database connection with a simple query
        session.exec(select(1))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    is_ready = db_status == "connected"

    return {
        "status": "ready" if is_ready else "not_ready",
        "service": "todo-backend",
        "checks": {
            "database": db_status,
        },
    }
