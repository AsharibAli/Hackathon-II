# [Task]: T028
# [Spec]: F-009 (R-009.4)
# [Description]: Health check endpoints for notification service
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe endpoint."""
    return {"status": "healthy", "service": "notification-service"}


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe endpoint."""
    return {"status": "ready", "service": "notification-service"}
