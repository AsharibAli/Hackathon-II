"""
Prometheus metrics middleware for FastAPI.

[Task]: Cloud-Native Implementation
[Description]: Collects and exposes Prometheus metrics for observability
"""

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

# =============================================================================
# METRICS DEFINITIONS
# =============================================================================

# Application info
APP_INFO = Info(
    "taskai_app",
    "TaskAI application information"
)

# Request metrics
REQUEST_COUNT = Counter(
    "taskai_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "taskai_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUEST_IN_PROGRESS = Gauge(
    "taskai_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"]
)

# Error metrics
ERROR_COUNT = Counter(
    "taskai_errors_total",
    "Total number of errors",
    ["type", "endpoint"]
)

# Business metrics
TASKS_CREATED = Counter(
    "taskai_tasks_created_total",
    "Total number of tasks created",
    ["priority"]
)

TASKS_COMPLETED = Counter(
    "taskai_tasks_completed_total",
    "Total number of tasks completed"
)

EVENTS_PUBLISHED = Counter(
    "taskai_events_published_total",
    "Total number of events published to Kafka",
    ["event_type", "status"]
)

AI_REQUESTS = Counter(
    "taskai_ai_requests_total",
    "Total number of AI/LLM requests",
    ["status"]
)

AI_LATENCY = Histogram(
    "taskai_ai_request_duration_seconds",
    "AI request latency in seconds",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Database metrics
DB_QUERY_COUNT = Counter(
    "taskai_db_queries_total",
    "Total number of database queries",
    ["operation"]
)

DB_QUERY_LATENCY = Histogram(
    "taskai_db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)


# =============================================================================
# HELPER FUNCTIONS FOR METRICS
# =============================================================================

def normalize_path(path: str) -> str:
    """
    Normalize request path to reduce cardinality.
    Replaces dynamic segments (UUIDs, IDs) with placeholders.
    """
    import re

    # Replace UUIDs
    path = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "{id}",
        path,
        flags=re.IGNORECASE
    )

    # Replace numeric IDs
    path = re.sub(r"/\d+", "/{id}", path)

    return path


def record_task_created(priority: str = "medium"):
    """Record task creation metric."""
    TASKS_CREATED.labels(priority=priority).inc()


def record_task_completed():
    """Record task completion metric."""
    TASKS_COMPLETED.inc()


def record_event_published(event_type: str, success: bool = True):
    """Record event publishing metric."""
    status = "success" if success else "failure"
    EVENTS_PUBLISHED.labels(event_type=event_type, status=status).inc()


def record_ai_request(success: bool = True, duration: float = 0.0):
    """Record AI request metric."""
    status = "success" if success else "failure"
    AI_REQUESTS.labels(status=status).inc()
    if duration > 0:
        AI_LATENCY.observe(duration)


def record_db_query(operation: str, duration: float):
    """Record database query metric."""
    DB_QUERY_COUNT.labels(operation=operation).inc()
    DB_QUERY_LATENCY.labels(operation=operation).observe(duration)


def record_error(error_type: str, endpoint: str):
    """Record error metric."""
    ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()


# =============================================================================
# PROMETHEUS MIDDLEWARE
# =============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for HTTP requests.

    Tracks:
    - Request count by method, endpoint, and status code
    - Request latency histogram
    - Requests in progress gauge
    """

    def __init__(self, app, app_name: str = "taskai", app_version: str = "1.0.0"):
        super().__init__(app)
        # Set application info
        APP_INFO.info({
            "app_name": app_name,
            "version": app_version,
            "service": "backend"
        })

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = normalize_path(request.url.path)

        # Track request in progress
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        # Record start time
        start_time = time.perf_counter()

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            # Record error
            status_code = 500
            record_error(type(e).__name__, endpoint)
            raise

        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time

            # Record metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Decrement in-progress gauge
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        return response


# =============================================================================
# METRICS ENDPOINT HANDLER
# =============================================================================

async def metrics_endpoint(request: Request) -> Response:
    """
    Handler for /metrics endpoint.
    Returns Prometheus metrics in text format.
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


def get_metrics_route():
    """
    Returns a route configuration for the metrics endpoint.
    Use this with app.add_route() or as a router endpoint.
    """
    from fastapi import APIRouter
    from fastapi.responses import PlainTextResponse

    router = APIRouter()

    @router.get(
        "/metrics",
        response_class=PlainTextResponse,
        tags=["Observability"],
        summary="Prometheus metrics endpoint",
        description="Returns application metrics in Prometheus format"
    )
    async def metrics():
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )

    return router
