import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        settings = get_settings()
        logger = logging.getLogger('app.access')
        start_time = perf_counter()
        response = await call_next(request)
        process_time_ms = (perf_counter() - start_time) * 1000
        logger.log(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
            'method=%s path=%s status=%s duration_ms=%.2f',
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
        )
        return response


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    )
