from fastapi import HTTPException, status
from redis import RedisError

from app.core.config import get_settings
from app.utils.redis_client import redis_client

settings = get_settings()


def enforce_auth_rate_limit(identifier: str) -> None:
    key = f'auth:rate-limit:{identifier}'
    try:
        attempts = redis_client.incr(key)
        if attempts == 1:
            redis_client.expire(key, settings.AUTH_RATE_LIMIT_WINDOW_SECONDS)
        if attempts > settings.AUTH_RATE_LIMIT_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail='Too many authentication attempts. Please try again later.',
            )
    except RedisError:
        # Fail open when redis is temporarily unavailable
        return
