from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    'tradeinsight',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    imports=('app.tasks.market_tasks',),
    beat_schedule={
        'monitor-market-alerts-every-minute': {
            'task': 'tasks.monitor_market_alerts',
            'schedule': crontab(),
            'args': ('NIFTY',),
        },
    },
)
