"""
Structured logging configuration using standard Python logging.

[Task]: Cloud-Native Implementation
[Description]: Production-ready logging with correlation ID support (no structlog dependency)
"""

import logging
import sys
import json
from typing import Any
from contextvars import ContextVar
from datetime import datetime, timezone

from core.config import settings

# Context variable for storing additional log context
_log_context: ContextVar[dict] = ContextVar("log_context", default={})


class JSONFormatter(logging.Formatter):
    """JSON formatter for production logging (Kubernetes/Loki compatible)."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "func_name": record.funcName,
        }

        # Add context variables
        context = _log_context.get()
        if context:
            log_data.update(context)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console output."""
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build base message
        message = f"{color}{timestamp} [{record.levelname}]{self.RESET} {record.name}: {record.getMessage()}"

        # Add context if present
        context = _log_context.get()
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}"

        # Add extra fields if present
        if hasattr(record, "extra_fields") and record.extra_fields:
            extras = " ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            message = f"{message} | {extras}"

        # Add exception info if present
        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"

        return message


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

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Set formatter based on environment
    if settings.DEBUG:
        formatter = ConsoleFormatter()
    else:
        formatter = JSONFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a configured logger.

    Args:
        name: Logger name (defaults to module name)

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables to the current logging context.

    These will be included in all subsequent log messages
    within the current context (async task, request, etc.).

    Args:
        **kwargs: Key-value pairs to bind to context
    """
    current = _log_context.get().copy()
    current.update(kwargs)
    _log_context.set(current)


def unbind_context(*keys: str) -> None:
    """
    Remove context variables from the current logging context.

    Args:
        *keys: Keys to remove from context
    """
    current = _log_context.get().copy()
    for key in keys:
        current.pop(key, None)
    _log_context.set(current)


def clear_context() -> None:
    """Clear all context variables from the current logging context."""
    _log_context.set({})


# Create default logger instance
logger = get_logger("taskai")


def _log_with_extra(log_func, message: str, **kwargs: Any) -> None:
    """Helper to log with extra fields stored in the record."""
    log_func(message, extra={"extra_fields": kwargs} if kwargs else None)


# Log event helpers for common operations
def log_request_start(
    method: str,
    path: str,
    correlation_id: str | None = None,
    **kwargs: Any
) -> None:
    """Log the start of an HTTP request."""
    bind_context(correlation_id=correlation_id)
    _log_with_extra(
        logger.info,
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
    _log_with_extra(
        logger.info,
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
        extra_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs
        }
        logger.error(message, exc_info=error, extra={"extra_fields": extra_data})
    else:
        _log_with_extra(logger.error, message, **kwargs)


def log_event_published(
    event_type: str,
    topic: str,
    success: bool = True,
    **kwargs: Any
) -> None:
    """Log an event publishing operation."""
    log_func = logger.info if success else logger.error
    _log_with_extra(
        log_func,
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
    _log_with_extra(
        logger.debug,
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
    log_data: dict[str, Any] = {
        "model": model,
        "success": success,
        **kwargs
    }
    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)
    if tokens is not None:
        log_data["tokens"] = tokens

    if success:
        _log_with_extra(logger.info, "ai_request_completed", **log_data)
    else:
        _log_with_extra(logger.error, "ai_request_failed", **log_data)


def log_task_event(
    action: str,
    task_id: str,
    user_id: str,
    **kwargs: Any
) -> None:
    """Log a task-related event."""
    _log_with_extra(
        logger.info,
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
    log_data: dict[str, Any] = {
        "action": action,
        "success": success,
        **kwargs
    }
    if user_id:
        log_data["user_id"] = user_id
    if email:
        log_data["email"] = email

    if success:
        _log_with_extra(logger.info, "auth_event", **log_data)
    else:
        _log_with_extra(logger.warning, "auth_event", **log_data)
