"""FastAPI middleware for error handling and request logging."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ros2_web_monitor.core.errors import RWMError

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch RWMError exceptions and return structured JSON responses."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        try:
            return await call_next(request)  # type: ignore[arg-type]
        except RWMError as exc:
            logger.warning("Application error: %s (status=%d)", exc.message, exc.status_code)
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.message},
            )
        except Exception:
            logger.exception("Unhandled exception during request %s %s", request.method, request.url)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)  # type: ignore[arg-type]
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "%s %s → %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
