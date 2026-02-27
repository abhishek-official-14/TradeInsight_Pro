from collections.abc import Awaitable, Callable

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.security import TokenType

settings = get_settings()


class TokenValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_prefixes: tuple[str, ...] | None = None) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.excluded_prefixes = excluded_prefixes or ('/health', f"{settings.API_V1_PREFIX}/auth")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path.startswith(self.excluded_prefixes):
            return await call_next(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return await call_next(request)

        if not auth_header.startswith('Bearer '):
            return JSONResponse(status_code=401, content={'detail': 'Invalid authorization header'})

        token = auth_header.removeprefix('Bearer ').strip()
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get('type') != TokenType.ACCESS:
                return JSONResponse(status_code=401, content={'detail': 'Invalid token type'})
        except JWTError:
            return JSONResponse(status_code=401, content={'detail': 'Invalid or expired token'})

        return await call_next(request)
