"""
Error handling middleware for graceful error responses.
Catches unhandled exceptions and returns structured error responses.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches unhandled exceptions and returns structured error responses.
    Prevents sensitive error details from leaking to clients in production.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle any unhandled exceptions.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler or error response
        """
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log the full exception with stack trace
            logger.exception(
                f"Unhandled exception during request: {request.method} {request.url.path}"
            )

            # Return a generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "type": "internal_error"
                }
            )
