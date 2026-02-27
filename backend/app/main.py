from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging import LoggingMiddleware, configure_logging
from app.core.subscription_middleware import SubscriptionAccessMiddleware
from app.core.token_middleware import TokenValidationMiddleware
from app.utils.error_middleware import ErrorHandlingMiddleware

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TokenValidationMiddleware)
app.add_middleware(SubscriptionAccessMiddleware)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get('/health', tags=['health'])
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
