from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.api_usage_log import APIUsageLog
from app.repositories.user_repository import UserRepository

settings = get_settings()


class APIUsageLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        db = SessionLocal()
        try:
            user_id = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.removeprefix('Bearer ').strip()
                try:
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                    subject = payload.get('sub')
                    if isinstance(subject, str):
                        user = UserRepository(db).get_by_email(subject)
                        if user is not None:
                            user_id = user.id
                except JWTError:
                    user_id = None

            log = APIUsageLog(
                user_id=user_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                ip_address=request.client.host if request.client else None,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

        return response
