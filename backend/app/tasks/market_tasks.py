from app.tasks.celery_app import celery_app
from app.utils.redis_client import redis_client


@celery_app.task(name='tasks.cache_market_heartbeat')
def cache_market_heartbeat() -> str:
    redis_client.set('market:heartbeat', 'ok', ex=60)
    return 'ok'
