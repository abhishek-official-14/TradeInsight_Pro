from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    APP_NAME: str = 'TradeInsight Pro'
    APP_ENV: Literal['development', 'production'] = 'development'
    DEBUG: bool = True
    API_V1_PREFIX: str = '/api/v1'

    DATABASE_URL: str = Field(..., description='PostgreSQL DSN')
    REDIS_URL: str = Field(..., description='Redis DSN')

    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    AUTH_RATE_LIMIT_ATTEMPTS: int = 5
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60

    CELERY_BROKER_URL: str = Field(...)
    CELERY_RESULT_BACKEND: str = Field(...)

    LOG_LEVEL: str = 'INFO'

    RAZORPAY_KEY_ID: str = Field(...)
    RAZORPAY_KEY_SECRET: str = Field(...)
    RAZORPAY_WEBHOOK_SECRET: str = Field(...)
    SUBSCRIPTION_DURATION_DAYS: int = 30

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == 'production'


class DevelopmentSettings(Settings):
    APP_ENV: Literal['development', 'production'] = 'development'
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'


class ProductionSettings(Settings):
    APP_ENV: Literal['development', 'production'] = 'production'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'


@lru_cache
def get_settings() -> Settings:
    base_settings = Settings()
    if base_settings.APP_ENV == 'production':
        return ProductionSettings()
    return DevelopmentSettings()
