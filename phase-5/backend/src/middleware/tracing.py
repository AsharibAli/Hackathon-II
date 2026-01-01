"""
OpenTelemetry distributed tracing configuration.

[Task]: Cloud-Native Implementation
[Description]: Distributed tracing with Jaeger integration for observability
"""

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

# Import exporters conditionally based on availability
try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    JAEGER_AVAILABLE = True
except ImportError:
    JAEGER_AVAILABLE = False

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False


# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment variables for tracing configuration
TRACING_ENABLED = os.getenv("TRACING_ENABLED", "true").lower() == "true"
SERVICE_NAME_VALUE = os.getenv("OTEL_SERVICE_NAME", "taskai-backend")
SERVICE_VERSION_VALUE = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")

# Jaeger configuration
JAEGER_AGENT_HOST = os.getenv("JAEGER_AGENT_HOST", "localhost")
JAEGER_AGENT_PORT = int(os.getenv("JAEGER_AGENT_PORT", "6831"))
JAEGER_COLLECTOR_ENDPOINT = os.getenv(
    "JAEGER_COLLECTOR_ENDPOINT",
    "http://jaeger-collector:14268/api/traces"
)

# OTLP configuration (alternative to Jaeger)
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector:4317")

# Sampling rate (0.0 to 1.0)
SAMPLING_RATE = float(os.getenv("OTEL_SAMPLING_RATE", "1.0"))


# =============================================================================
# TRACER PROVIDER SETUP
# =============================================================================

_tracer_provider: Optional[TracerProvider] = None
_initialized = False


def setup_tracing(app_name: str = SERVICE_NAME_VALUE, app_version: str = SERVICE_VERSION_VALUE) -> None:
    """
    Initialize OpenTelemetry tracing.

    Args:
        app_name: Service name for traces
        app_version: Service version for traces
    """
    global _tracer_provider, _initialized

    if _initialized:
        return

    if not TRACING_ENABLED:
        _initialized = True
        return

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: app_name,
        SERVICE_VERSION: app_version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        "service.namespace": "taskai",
    })

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add exporter based on availability and configuration
    exporter = _create_exporter()
    if exporter:
        span_processor = BatchSpanProcessor(exporter)
        _tracer_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)

    # Set B3 propagator for compatibility with Dapr and other systems
    set_global_textmap(B3MultiFormat())

    _initialized = True


def _create_exporter():
    """Create the appropriate span exporter based on configuration."""
    exporter_type = os.getenv("OTEL_EXPORTER_TYPE", "jaeger").lower()

    if exporter_type == "otlp" and OTLP_AVAILABLE:
        return OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)

    if exporter_type == "jaeger" and JAEGER_AVAILABLE:
        # Try collector endpoint first, fall back to agent
        try:
            return JaegerExporter(
                collector_endpoint=JAEGER_COLLECTOR_ENDPOINT,
            )
        except Exception:
            return JaegerExporter(
                agent_host_name=JAEGER_AGENT_HOST,
                agent_port=JAEGER_AGENT_PORT,
            )

    # No exporter available - traces will be discarded
    return None


def instrument_fastapi(app) -> None:
    """
    Instrument a FastAPI application for tracing.

    Args:
        app: FastAPI application instance
    """
    if not TRACING_ENABLED:
        return

    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="health,metrics,docs,redoc,openapi.json",
        tracer_provider=_tracer_provider,
    )


def instrument_httpx() -> None:
    """Instrument httpx client for tracing outgoing HTTP requests."""
    if not TRACING_ENABLED:
        return

    HTTPXClientInstrumentor().instrument()


def shutdown_tracing() -> None:
    """Shutdown tracing and flush any pending spans."""
    global _tracer_provider, _initialized

    if _tracer_provider:
        _tracer_provider.shutdown()
        _tracer_provider = None

    _initialized = False


# =============================================================================
# TRACER UTILITIES
# =============================================================================

def get_tracer(name: str = "taskai") -> trace.Tracer:
    """
    Get a tracer instance for creating spans.

    Args:
        name: Tracer name (usually module or component name)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_current_span() -> Optional[trace.Span]:
    """Get the currently active span, if any."""
    return trace.get_current_span()


def get_trace_id() -> Optional[str]:
    """Get the current trace ID as a hex string."""
    span = get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


def get_span_id() -> Optional[str]:
    """Get the current span ID as a hex string."""
    span = get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return None


# =============================================================================
# SPAN CONTEXT MANAGERS
# =============================================================================

def create_span(
    name: str,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    attributes: Optional[dict] = None
):
    """
    Create a new span as a context manager.

    Usage:
        with create_span("process_task", attributes={"task_id": task_id}) as span:
            # Do work
            span.set_attribute("result", "success")

    Args:
        name: Span name
        kind: Span kind (INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER)
        attributes: Initial span attributes

    Returns:
        Span context manager
    """
    tracer = get_tracer()
    return tracer.start_as_current_span(
        name,
        kind=kind,
        attributes=attributes or {},
    )


def add_span_event(name: str, attributes: Optional[dict] = None) -> None:
    """
    Add an event to the current span.

    Args:
        name: Event name
        attributes: Event attributes
    """
    span = get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes or {})


def set_span_attribute(key: str, value) -> None:
    """
    Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    span = get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, value)


def set_span_status(status: trace.Status) -> None:
    """
    Set the status of the current span.

    Args:
        status: Span status (OK or ERROR)
    """
    span = get_current_span()
    if span and span.is_recording():
        span.set_status(status)


def record_exception(exception: Exception) -> None:
    """
    Record an exception on the current span.

    Args:
        exception: The exception to record
    """
    span = get_current_span()
    if span and span.is_recording():
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))


# =============================================================================
# DECORATOR FOR TRACING FUNCTIONS
# =============================================================================

def traced(
    name: Optional[str] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    attributes: Optional[dict] = None,
):
    """
    Decorator to trace a function.

    Usage:
        @traced("process_task")
        async def process_task(task_id: str):
            ...

        @traced(attributes={"component": "task_service"})
        def sync_function():
            ...

    Args:
        name: Span name (defaults to function name)
        kind: Span kind
        attributes: Span attributes
    """
    import functools
    import asyncio

    def decorator(func):
        span_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with create_span(span_name, kind=kind, attributes=attributes):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with create_span(span_name, kind=kind, attributes=attributes):
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
