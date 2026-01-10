"""
Distributed tracing configuration (no-op implementation).

[Task]: Cloud-Native Implementation
[Description]: Distributed tracing with no external dependencies
"""

import os
import functools
import asyncio
from typing import Optional, Any, Dict
from contextvars import ContextVar
from contextlib import contextmanager
import uuid


# =============================================================================
# CONFIGURATION
# =============================================================================

TRACING_ENABLED = os.getenv("TRACING_ENABLED", "false").lower() == "true"
SERVICE_NAME_VALUE = os.getenv("OTEL_SERVICE_NAME", "taskai-backend")
SERVICE_VERSION_VALUE = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")


# =============================================================================
# NO-OP SPAN IMPLEMENTATION
# =============================================================================

class SpanKind:
    """Span kind enumeration."""
    INTERNAL = 0
    SERVER = 1
    CLIENT = 2
    PRODUCER = 3
    CONSUMER = 4


class StatusCode:
    """Status code enumeration."""
    UNSET = 0
    OK = 1
    ERROR = 2


class Status:
    """Span status."""
    def __init__(self, status_code: int = StatusCode.UNSET, description: str = ""):
        self.status_code = status_code
        self.description = description


class SpanContext:
    """Span context with trace and span IDs."""
    def __init__(self, trace_id: str = "", span_id: str = ""):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.span_id = span_id or uuid.uuid4().hex[:16]
        self.is_valid = bool(trace_id or span_id)

    @property
    def trace_id_int(self) -> int:
        """Get trace ID as integer."""
        try:
            return int(self.trace_id, 16)
        except ValueError:
            return 0


class NoOpSpan:
    """No-op span implementation."""

    def __init__(self, name: str = "", kind: int = SpanKind.INTERNAL, attributes: Optional[Dict] = None):
        self.name = name
        self.kind = kind
        self._attributes: Dict[str, Any] = attributes or {}
        self._events: list = []
        self._status = Status()
        self._context = SpanContext()
        self._recording = True

    def get_span_context(self) -> SpanContext:
        """Get the span context."""
        return self._context

    def is_recording(self) -> bool:
        """Check if span is recording."""
        return self._recording

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self._attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict] = None) -> None:
        """Add an event to the span."""
        self._events.append({"name": name, "attributes": attributes or {}})

    def set_status(self, status: Status) -> None:
        """Set the span status."""
        self._status = status

    def record_exception(self, exception: Exception) -> None:
        """Record an exception."""
        self.add_event("exception", {
            "exception.type": type(exception).__name__,
            "exception.message": str(exception)
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.record_exception(exc_val)
            self.set_status(Status(StatusCode.ERROR, str(exc_val)))
        return False


class NoOpTracer:
    """No-op tracer implementation."""

    def __init__(self, name: str = ""):
        self.name = name

    def start_as_current_span(
        self,
        name: str,
        kind: int = SpanKind.INTERNAL,
        attributes: Optional[Dict] = None,
    ) -> NoOpSpan:
        """Start a new span as the current span."""
        span = NoOpSpan(name, kind, attributes)
        _current_span.set(span)
        return span


# Context variable for current span
_current_span: ContextVar[Optional[NoOpSpan]] = ContextVar("current_span", default=None)

# Global state
_initialized = False
_tracer_provider: Optional[Any] = None


# =============================================================================
# PUBLIC API
# =============================================================================

def setup_tracing(app_name: str = SERVICE_NAME_VALUE, app_version: str = SERVICE_VERSION_VALUE) -> None:
    """
    Initialize tracing (no-op in this implementation).

    Args:
        app_name: Service name for traces
        app_version: Service version for traces
    """
    global _initialized
    _initialized = True


def instrument_fastapi(app) -> None:
    """
    Instrument a FastAPI application for tracing (no-op).

    Args:
        app: FastAPI application instance
    """
    pass


def instrument_httpx() -> None:
    """Instrument httpx client for tracing (no-op)."""
    pass


def shutdown_tracing() -> None:
    """Shutdown tracing (no-op)."""
    global _initialized
    _initialized = False


def get_tracer(name: str = "taskai") -> NoOpTracer:
    """
    Get a tracer instance for creating spans.

    Args:
        name: Tracer name (usually module or component name)

    Returns:
        Tracer instance
    """
    return NoOpTracer(name)


def get_current_span() -> Optional[NoOpSpan]:
    """Get the currently active span, if any."""
    return _current_span.get()


def get_trace_id() -> Optional[str]:
    """Get the current trace ID as a hex string."""
    span = get_current_span()
    if span:
        return span.get_span_context().trace_id
    return None


def get_span_id() -> Optional[str]:
    """Get the current span ID as a hex string."""
    span = get_current_span()
    if span:
        return span.get_span_context().span_id
    return None


# =============================================================================
# SPAN CONTEXT MANAGERS
# =============================================================================

@contextmanager
def create_span(
    name: str,
    kind: int = SpanKind.INTERNAL,
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

    Yields:
        Span instance
    """
    span = NoOpSpan(name, kind, attributes)
    token = _current_span.set(span)
    try:
        yield span
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise
    finally:
        _current_span.reset(token)


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


def set_span_status(status: Status) -> None:
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
        span.set_status(Status(StatusCode.ERROR, str(exception)))


# =============================================================================
# DECORATOR FOR TRACING FUNCTIONS
# =============================================================================

def traced(
    name: Optional[str] = None,
    kind: int = SpanKind.INTERNAL,
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


# =============================================================================
# COMPATIBILITY EXPORTS
# =============================================================================

# Create a trace module-like namespace for compatibility
class trace:
    """Compatibility namespace for opentelemetry.trace."""
    SpanKind = SpanKind
    Status = Status
    StatusCode = StatusCode
    Span = NoOpSpan
    Tracer = NoOpTracer

    @staticmethod
    def get_tracer(name: str = "taskai") -> NoOpTracer:
        return get_tracer(name)

    @staticmethod
    def get_current_span() -> Optional[NoOpSpan]:
        return get_current_span()
