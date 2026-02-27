from app.services.ai_signal_service import AISignalEngineService
from app.tasks.celery_app import celery_app
from app.utils.redis_client import redis_client


@celery_app.task(name='tasks.cache_market_heartbeat')
def cache_market_heartbeat() -> str:
    redis_client.set('market:heartbeat', 'ok', ex=60)
    return 'ok'


@celery_app.task(name='tasks.generate_ai_trading_signal')
def generate_ai_trading_signal(symbol: str = 'NIFTY') -> dict:
    return AISignalEngineService().generate_signal(symbol=symbol)


@celery_app.task(name='tasks.monitor_market_alerts')
def monitor_market_alerts(symbol: str = 'NIFTY') -> dict:
    return AISignalEngineService().generate_signal(symbol=symbol)
