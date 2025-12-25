# [Task]: T029
# [Spec]: F-010 (R-010.4)
# [Description]: Health check endpoints for recurring service
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe endpoint."""
    return {"status": "healthy", "service": "recurring-service"}


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe endpoint."""
    return {"status": "ready", "service": "recurring-service"}
