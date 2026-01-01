# [Task]: T098, T127
# [Spec]: F-010 (R-010.3), F-011 (R-011.1)
# [Description]: Structured logging configuration with correlation ID support
import uuid
import structlog
from contextvars import ContextVar
from .config import settings

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_var.set(correlation_id)


def extract_correlation_id(headers: dict, body: dict = None) -> str:
    """
    Extract correlation ID from request headers or CloudEvent.

    Args:
        headers: Request headers dict
        body: Optional CloudEvent body

    Returns:
        Extracted or generated correlation ID
    """
    # Try standard headers
    correlation_id = (
        headers.get("x-correlation-id")
        or headers.get("x-request-id")
        or headers.get("X-Correlation-ID")
        or headers.get("X-Request-ID")
    )

    # Try traceparent header (OpenTelemetry/Dapr)
    if not correlation_id:
        traceparent = headers.get("traceparent")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 2:
                correlation_id = parts[1]

    # Try CloudEvent ID from body
    if not correlation_id and body:
        correlation_id = body.get("id")

    # Generate new if not found
    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    return correlation_id


def add_correlation_id(logger, method_name, event_dict):
    """Structlog processor to add correlation ID to all log entries."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def configure_logging() -> None:
    """Configure structlog for JSON logging with correlation ID support."""
    processors = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)
