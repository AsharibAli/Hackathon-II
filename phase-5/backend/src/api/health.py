# [Task]: T027, Cloud-Native Implementation
# [Spec]: F-011 (R-011.3)
# [Description]: Enhanced health check endpoints with dependency verification
"""
Health and readiness check endpoints for Kubernetes probes.
Includes comprehensive dependency checks for cloud-native deployment.
"""
import os
import time
from typing import Optional
from fastapi import APIRouter, Depends, Response
from sqlmodel import Session, select
import httpx

from core.database import get_session
from core.config import settings

router = APIRouter(tags=["health"])

# Dapr sidecar configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_HEALTH_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/healthz"

# Service info
SERVICE_NAME = "todo-backend"
SERVICE_VERSION = settings.APP_VERSION


async def check_database(session: Session) -> dict:
    """Check database connectivity."""
    start = time.perf_counter()
    try:
        session.exec(select(1))
        latency = (time.perf_counter() - start) * 1000
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_dapr_sidecar() -> dict:
    """Check Dapr sidecar connectivity."""
    if not os.getenv("DAPR_ENABLED", "false").lower() == "true":
        return {"status": "disabled"}

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(DAPR_HEALTH_URL)
            latency = (time.perf_counter() - start) * 1000
            if response.status_code == 204 or response.status_code == 200:
                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2)
                }
            return {
                "status": "unhealthy",
                "status_code": response.status_code
            }
    except httpx.TimeoutException:
        return {"status": "unhealthy", "error": "timeout"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_event_publisher() -> dict:
    """Check event publisher (Dapr pub/sub) connectivity."""
    if not os.getenv("DAPR_ENABLED", "false").lower() == "true":
        return {"status": "disabled"}

    pubsub_name = os.getenv("PUBSUB_NAME", "kafka-pubsub")
    # Check if pub/sub component is available via Dapr
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/metadata"
            )
            if response.status_code == 200:
                metadata = response.json()
                components = metadata.get("components", [])
                pubsub_found = any(
                    c.get("name") == pubsub_name and c.get("type") == "pubsub.kafka"
                    for c in components
                )
                if pubsub_found:
                    return {"status": "healthy", "component": pubsub_name}
                return {"status": "unhealthy", "error": f"pubsub {pubsub_name} not found"}
            return {"status": "unhealthy", "status_code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/health")
async def health_check() -> dict:
    """
    Liveness probe endpoint.

    Returns basic health status. This endpoint should always return 200
    if the application is running. Use for Kubernetes liveness probes.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": time.time()
    }


@router.get("/ready")
async def readiness_check(
    response: Response,
    session: Session = Depends(get_session)
) -> dict:
    """
    Readiness probe endpoint.

    Performs comprehensive health checks on all dependencies.
    Use for Kubernetes readiness probes.

    Returns:
        - status: "ready" or "not_ready"
        - checks: Individual check results for each dependency
    """
    # Perform all checks
    db_check = await check_database(session)
    dapr_check = await check_dapr_sidecar()
    pubsub_check = await check_event_publisher()

    # Determine overall readiness
    # Database is required, Dapr checks are optional based on configuration
    db_healthy = db_check.get("status") == "healthy"
    dapr_healthy = dapr_check.get("status") in ("healthy", "disabled")
    pubsub_healthy = pubsub_check.get("status") in ("healthy", "disabled")

    is_ready = db_healthy and dapr_healthy and pubsub_healthy

    # Set appropriate HTTP status code
    if not is_ready:
        response.status_code = 503

    return {
        "status": "ready" if is_ready else "not_ready",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": time.time(),
        "checks": {
            "database": db_check,
            "dapr_sidecar": dapr_check,
            "event_publisher": pubsub_check
        }
    }


@router.get("/startup")
async def startup_check(
    response: Response,
    session: Session = Depends(get_session)
) -> dict:
    """
    Startup probe endpoint.

    Checks if the application has started successfully.
    Use for Kubernetes startup probes with longer timeout.
    """
    try:
        session.exec(select(1))
        return {
            "status": "started",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION
        }
    except Exception as e:
        response.status_code = 503
        return {
            "status": "starting",
            "service": SERVICE_NAME,
            "error": str(e)
        }
