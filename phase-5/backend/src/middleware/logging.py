# [Task]: T127
# [Spec]: F-011
# [Description]: Logging middleware with correlation ID support
"""
Logging middleware for request/response tracking.
Logs all HTTP requests with method, path, status code, and correlation ID.
"""
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .correlation import get_correlation_id

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all incoming HTTP requests and their responses.
    Includes request method, path, status code, processing time, and correlation ID.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler
        """
        start_time = time.time()

        # Get correlation ID (set by CorrelationMiddleware which runs first)
        correlation_id = get_correlation_id() or getattr(request.state, 'correlation_id', 'unknown')

        # Log incoming request with correlation ID
        logger.info(
            f"[{correlation_id}] Incoming request: {request.method} {request.url.path}"
        )

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response with correlation ID
        logger.info(
            f"[{correlation_id}] Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response
