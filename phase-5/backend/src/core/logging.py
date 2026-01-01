"""
Structured logging configuration using structlog.

[Task]: Cloud-Native Implementation
[Description]: Production-ready JSON logging with correlation ID support
"""

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from core.config import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up:
    - JSON output for production (Kubernetes/Loki compatible)
    - Console output for development
    - Correlation ID propagation
    - Standard log level filtering
    """
    # Determine log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Shared processors for all environments
    shared_processors = [
        # Add context variables (correlation_id, etc.)
        merge_contextvars,
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add timestamp in ISO format
        structlog.processors.TimeStamper(fmt="iso"),
        # Add stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.processors.format_exc_info,
        # Add caller information (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
    ]

    # Environment-specific configuration
    if settings.DEBUG:
        # Development: colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: JSON output for log aggregation
        processors = shared_processors + [
            # Ensure all values are JSON serializable
            structlog.processors.UnicodeDecoder(),
            # Render as JSON
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.

    Args:
        name: Logger name (defaults to module name)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables to the current logging context.

    These will be included in all subsequent log messages
    within the current context (async task, request, etc.).

    Args:
        **kwargs: Key-value pairs to bind to context
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """
    Remove context variables from the current logging context.

    Args:
        *keys: Keys to remove from context
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """Clear all context variables from the current logging context."""
    structlog.contextvars.clear_contextvars()


# Create default logger instance
logger = get_logger("taskai")


# Log event helpers for common operations
def log_request_start(
    method: str,
    path: str,
    correlation_id: str | None = None,
    **kwargs: Any
) -> None:
    """Log the start of an HTTP request."""
    bind_context(correlation_id=correlation_id)
    logger.info(
        "request_started",
        method=method,
        path=path,
        **kwargs
    )


def log_request_end(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """Log the end of an HTTP request."""
    logger.info(
        "request_completed",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


def log_error(
    message: str,
    error: Exception | None = None,
    **kwargs: Any
) -> None:
    """Log an error event."""
    if error:
        logger.error(
            message,
            error_type=type(error).__name__,
            error_message=str(error),
            exc_info=error,
            **kwargs
        )
    else:
        logger.error(message, **kwargs)


def log_event_published(
    event_type: str,
    topic: str,
    success: bool = True,
    **kwargs: Any
) -> None:
    """Log an event publishing operation."""
    level = "info" if success else "error"
    getattr(logger, level)(
        "event_published",
        event_type=event_type,
        topic=topic,
        success=success,
        **kwargs
    )


def log_db_operation(
    operation: str,
    table: str,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """Log a database operation."""
    logger.debug(
        "db_operation",
        operation=operation,
        table=table,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


def log_ai_request(
    model: str,
    success: bool = True,
    duration_ms: float | None = None,
    tokens: int | None = None,
    **kwargs: Any
) -> None:
    """Log an AI/LLM request."""
    log_data = {
        "model": model,
        "success": success,
        **kwargs
    }
    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)
    if tokens is not None:
        log_data["tokens"] = tokens

    if success:
        logger.info("ai_request_completed", **log_data)
    else:
        logger.error("ai_request_failed", **log_data)


def log_task_event(
    action: str,
    task_id: str,
    user_id: str,
    **kwargs: Any
) -> None:
    """Log a task-related event."""
    logger.info(
        "task_event",
        action=action,
        task_id=task_id,
        user_id=user_id,
        **kwargs
    )


def log_auth_event(
    action: str,
    user_id: str | None = None,
    email: str | None = None,
    success: bool = True,
    **kwargs: Any
) -> None:
    """Log an authentication event."""
    log_data = {
        "action": action,
        "success": success,
        **kwargs
    }
    if user_id:
        log_data["user_id"] = user_id
    if email:
        log_data["email"] = email

    if success:
        logger.info("auth_event", **log_data)
    else:
        logger.warning("auth_event", **log_data)
