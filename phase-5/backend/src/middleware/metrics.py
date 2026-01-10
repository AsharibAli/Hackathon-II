"""
Metrics middleware for FastAPI.

[Task]: Cloud-Native Implementation
[Description]: Collects and exposes metrics for observability (no external dependencies)
"""

import time
import re
from typing import Callable, Dict, List, Any
from collections import defaultdict
from threading import Lock
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# =============================================================================
# IN-MEMORY METRICS STORAGE
# =============================================================================

class MetricsRegistry:
    """Simple in-memory metrics registry."""

    def __init__(self):
        self._lock = Lock()
        self._counters: Dict[str, Dict[tuple, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: Dict[str, Dict[tuple, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: Dict[str, Dict[tuple, List[float]]] = defaultdict(lambda: defaultdict(list))
        self._info: Dict[str, Dict[str, str]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register_counter(self, name: str, help_text: str, labels: List[str] = None):
        """Register a counter metric."""
        self._metadata[name] = {"type": "counter", "help": help_text, "labels": labels or []}

    def register_gauge(self, name: str, help_text: str, labels: List[str] = None):
        """Register a gauge metric."""
        self._metadata[name] = {"type": "gauge", "help": help_text, "labels": labels or []}

    def register_histogram(self, name: str, help_text: str, labels: List[str] = None, buckets: List[float] = None):
        """Register a histogram metric."""
        self._metadata[name] = {
            "type": "histogram",
            "help": help_text,
            "labels": labels or [],
            "buckets": buckets or [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        }

    def register_info(self, name: str, help_text: str):
        """Register an info metric."""
        self._metadata[name] = {"type": "info", "help": help_text}

    def inc_counter(self, name: str, labels: tuple = (), value: float = 1.0):
        """Increment a counter."""
        with self._lock:
            self._counters[name][labels] += value

    def set_gauge(self, name: str, labels: tuple = (), value: float = 0.0):
        """Set a gauge value."""
        with self._lock:
            self._gauges[name][labels] = value

    def inc_gauge(self, name: str, labels: tuple = (), value: float = 1.0):
        """Increment a gauge."""
        with self._lock:
            self._gauges[name][labels] += value

    def dec_gauge(self, name: str, labels: tuple = (), value: float = 1.0):
        """Decrement a gauge."""
        with self._lock:
            self._gauges[name][labels] -= value

    def observe_histogram(self, name: str, labels: tuple = (), value: float = 0.0):
        """Add an observation to a histogram."""
        with self._lock:
            self._histograms[name][labels].append(value)

    def set_info(self, name: str, info: Dict[str, str]):
        """Set info metric values."""
        with self._lock:
            self._info[name] = info

    def generate_metrics(self) -> str:
        """Generate metrics in Prometheus text format."""
        lines = []

        with self._lock:
            # Output counters
            for name, values in self._counters.items():
                meta = self._metadata.get(name, {})
                if meta:
                    lines.append(f"# HELP {name} {meta.get('help', '')}")
                    lines.append(f"# TYPE {name} counter")
                for labels, value in values.items():
                    label_str = self._format_labels(meta.get('labels', []), labels)
                    lines.append(f"{name}{label_str} {value}")

            # Output gauges
            for name, values in self._gauges.items():
                meta = self._metadata.get(name, {})
                if meta:
                    lines.append(f"# HELP {name} {meta.get('help', '')}")
                    lines.append(f"# TYPE {name} gauge")
                for labels, value in values.items():
                    label_str = self._format_labels(meta.get('labels', []), labels)
                    lines.append(f"{name}{label_str} {value}")

            # Output histograms (simplified - just count and sum)
            for name, values in self._histograms.items():
                meta = self._metadata.get(name, {})
                if meta:
                    lines.append(f"# HELP {name} {meta.get('help', '')}")
                    lines.append(f"# TYPE {name} histogram")
                for labels, observations in values.items():
                    if observations:
                        label_str = self._format_labels(meta.get('labels', []), labels)
                        count = len(observations)
                        total = sum(observations)
                        lines.append(f"{name}_count{label_str} {count}")
                        lines.append(f"{name}_sum{label_str} {total}")

            # Output info metrics
            for name, info in self._info.items():
                meta = self._metadata.get(name, {})
                if meta:
                    lines.append(f"# HELP {name}_info {meta.get('help', '')}")
                    lines.append(f"# TYPE {name}_info gauge")
                info_labels = ",".join(f'{k}="{v}"' for k, v in info.items())
                lines.append(f"{name}_info{{{info_labels}}} 1")

        return "\n".join(lines) + "\n"

    def _format_labels(self, label_names: List[str], label_values: tuple) -> str:
        """Format labels for Prometheus output."""
        if not label_names or not label_values:
            return ""
        pairs = [f'{name}="{value}"' for name, value in zip(label_names, label_values)]
        return "{" + ",".join(pairs) + "}"


# Global registry
REGISTRY = MetricsRegistry()


# =============================================================================
# METRIC WRAPPERS (Compatible API)
# =============================================================================

class Counter:
    """Counter metric wrapper."""

    def __init__(self, name: str, help_text: str, labels: List[str] = None):
        self.name = name
        self.labels_list = labels or []
        REGISTRY.register_counter(name, help_text, labels)

    def labels(self, **kwargs) -> "CounterLabeled":
        label_values = tuple(kwargs.get(label, "") for label in self.labels_list)
        return CounterLabeled(self.name, label_values)

    def inc(self, value: float = 1.0):
        REGISTRY.inc_counter(self.name, (), value)


class CounterLabeled:
    """Labeled counter instance."""

    def __init__(self, name: str, label_values: tuple):
        self.name = name
        self.label_values = label_values

    def inc(self, value: float = 1.0):
        REGISTRY.inc_counter(self.name, self.label_values, value)


class Gauge:
    """Gauge metric wrapper."""

    def __init__(self, name: str, help_text: str, labels: List[str] = None):
        self.name = name
        self.labels_list = labels or []
        REGISTRY.register_gauge(name, help_text, labels)

    def labels(self, **kwargs) -> "GaugeLabeled":
        label_values = tuple(kwargs.get(label, "") for label in self.labels_list)
        return GaugeLabeled(self.name, label_values)

    def set(self, value: float):
        REGISTRY.set_gauge(self.name, (), value)

    def inc(self, value: float = 1.0):
        REGISTRY.inc_gauge(self.name, (), value)

    def dec(self, value: float = 1.0):
        REGISTRY.dec_gauge(self.name, (), value)


class GaugeLabeled:
    """Labeled gauge instance."""

    def __init__(self, name: str, label_values: tuple):
        self.name = name
        self.label_values = label_values

    def set(self, value: float):
        REGISTRY.set_gauge(self.name, self.label_values, value)

    def inc(self, value: float = 1.0):
        REGISTRY.inc_gauge(self.name, self.label_values, value)

    def dec(self, value: float = 1.0):
        REGISTRY.dec_gauge(self.name, self.label_values, value)


class Histogram:
    """Histogram metric wrapper."""

    def __init__(self, name: str, help_text: str, labels: List[str] = None, buckets: List[float] = None):
        self.name = name
        self.labels_list = labels or []
        REGISTRY.register_histogram(name, help_text, labels, buckets)

    def labels(self, **kwargs) -> "HistogramLabeled":
        label_values = tuple(kwargs.get(label, "") for label in self.labels_list)
        return HistogramLabeled(self.name, label_values)

    def observe(self, value: float):
        REGISTRY.observe_histogram(self.name, (), value)


class HistogramLabeled:
    """Labeled histogram instance."""

    def __init__(self, name: str, label_values: tuple):
        self.name = name
        self.label_values = label_values

    def observe(self, value: float):
        REGISTRY.observe_histogram(self.name, self.label_values, value)


class Info:
    """Info metric wrapper."""

    def __init__(self, name: str, help_text: str):
        self.name = name
        REGISTRY.register_info(name, help_text)

    def info(self, info_dict: Dict[str, str]):
        REGISTRY.set_info(self.name, info_dict)


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
    Middleware to collect metrics for HTTP requests.

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

CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


async def metrics_endpoint(request: Request) -> Response:
    """
    Handler for /metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    return Response(
        content=REGISTRY.generate_metrics(),
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
            content=REGISTRY.generate_metrics(),
            media_type=CONTENT_TYPE_LATEST
        )

    return router
