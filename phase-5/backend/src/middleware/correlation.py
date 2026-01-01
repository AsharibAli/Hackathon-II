# [Task]: T127
# [Spec]: F-011 (R-011.1)
# [Description]: Request correlation ID middleware for distributed tracing
"""
Correlation ID middleware for distributed tracing.
Generates or extracts correlation IDs for request tracking across services.
"""
import uuid
import logging
from contextvars import ContextVar
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Context variable to store correlation ID for the current request
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

# Standard header names for correlation ID
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"
# Dapr uses traceparent for distributed tracing
TRACEPARENT_HEADER = "traceparent"


def get_correlation_id() -> str:
    """
    Get the correlation ID for the current request context.

    Returns:
        The correlation ID or empty string if not set
    """
    return correlation_id_var.get()


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.

    Returns:
        A new UUID-based correlation ID
    """
    return str(uuid.uuid4())


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts or generates correlation IDs for request tracking.

    Supports multiple header formats:
    - X-Correlation-ID: Standard correlation ID header
    - X-Request-ID: Alternative request ID header
    - traceparent: OpenTelemetry/Dapr tracing header

    The correlation ID is:
    1. Extracted from incoming request headers (if present)
    2. Generated if not present
    3. Stored in request state and context variable
    4. Added to response headers
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and manage correlation ID.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response with correlation ID header
        """
        # Try to extract correlation ID from various headers
        correlation_id = (
            request.headers.get(CORRELATION_ID_HEADER)
            or request.headers.get(REQUEST_ID_HEADER)
            or self._extract_from_traceparent(request.headers.get(TRACEPARENT_HEADER))
        )

        # Generate new correlation ID if not present
        if not correlation_id:
            correlation_id = generate_correlation_id()
            logger.debug(f"Generated new correlation ID: {correlation_id}")
        else:
            logger.debug(f"Using existing correlation ID: {correlation_id}")

        # Store in context variable for use in logging and other code
        token = correlation_id_var.set(correlation_id)

        # Store in request state for easy access in route handlers
        request.state.correlation_id = correlation_id

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            response.headers[REQUEST_ID_HEADER] = correlation_id

            return response
        finally:
            # Reset context variable
            correlation_id_var.reset(token)

    def _extract_from_traceparent(self, traceparent: str | None) -> str | None:
        """
        Extract trace ID from OpenTelemetry traceparent header.

        Format: {version}-{trace-id}-{parent-id}-{trace-flags}
        Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01

        Args:
            traceparent: The traceparent header value

        Returns:
            The trace ID portion or None if invalid
        """
        if not traceparent:
            return None

        parts = traceparent.split("-")
        if len(parts) >= 2:
            return parts[1]
        return None


class CorrelationLogFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records.

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(CorrelationLogFilter())
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(correlation_id)s - %(name)s - %(levelname)s - %(message)s'
        ))
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record."""
        record.correlation_id = get_correlation_id() or "no-correlation-id"
        return True
