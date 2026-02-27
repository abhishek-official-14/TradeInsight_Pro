from collections.abc import Awaitable, Callable

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import TokenType
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

settings = get_settings()


class SubscriptionAccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, premium_prefixes: tuple[str, ...] | None = None) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.premium_prefixes = premium_prefixes or (f"{settings.API_V1_PREFIX}/protected/pro",)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not request.url.path.startswith(self.premium_prefixes):
            return await call_next(request)

        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JSONResponse(status_code=401, content={'detail': 'Authorization token required'})

        token = auth_header.removeprefix('Bearer ').strip()
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            return JSONResponse(status_code=401, content={'detail': 'Invalid or expired token'})

        if payload.get('type') != TokenType.ACCESS:
            return JSONResponse(status_code=401, content={'detail': 'Invalid token type'})

        email = payload.get('sub')
        if not isinstance(email, str):
            return JSONResponse(status_code=401, content={'detail': 'Invalid token subject'})

        db = SessionLocal()
        try:
            user = UserRepository(db).get_by_email(email)
            if user is None:
                return JSONResponse(status_code=401, content={'detail': 'User not found'})
            if user.role not in (UserRole.PRO, UserRole.ADMIN):
                return JSONResponse(status_code=403, content={'detail': 'Pro subscription required'})
        finally:
            db.close()

        return await call_next(request)
