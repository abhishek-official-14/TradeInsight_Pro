import json
from datetime import datetime

from app.services.options_analytics_service import OptionsAnalyticsService
from app.utils.redis_client import redis_client
from app.utils.telegram_client import send_telegram_message

AI_SIGNAL_CACHE_PREFIX = 'ai:signal'
AI_SIGNAL_CLASSIFICATION_CACHE_PREFIX = 'ai:signal:classification'
AI_SIGNAL_CACHE_SECONDS = 60


class AISignalEngineService:
    def __init__(self) -> None:
        self.options_analytics_service = OptionsAnalyticsService()

    def get_latest_signal(self, symbol: str = 'NIFTY') -> dict:
        normalized_symbol = symbol.strip().upper()
        cache_key = self._cache_key(normalized_symbol)
        cached_signal = redis_client.get(cache_key)
        if cached_signal:
            return json.loads(cached_signal)
        return self.generate_signal(normalized_symbol)

    def generate_signal(self, symbol: str = 'NIFTY') -> dict:
        normalized_symbol = symbol.strip().upper()
        analytics = self.options_analytics_service.get_analytics(normalized_symbol)

        pcr_score = self._score_pcr(analytics.get('pcr'))
        change_oi_score = self._score_change_in_oi(
            analytics.get('change_in_put_oi'),
            analytics.get('change_in_call_oi'),
        )
        proximity_score = self._score_support_resistance_proximity(
            analytics.get('underlying_value'),
            analytics.get('strongest_support'),
            analytics.get('strongest_resistance'),
        )
        buildup_score = self._score_oi_buildup(
            analytics.get('change_in_put_oi'),
            analytics.get('change_in_call_oi'),
            analytics.get('pcr'),
        )

        score = round(
            (pcr_score * 0.30)
            + (change_oi_score * 0.25)
            + (proximity_score * 0.25)
            + (buildup_score * 0.20)
        )
        classification = self._classify_signal(score)

        signal_payload = {
            'symbol': normalized_symbol,
            'score': score,
            'classification': classification,
            'generated_at': datetime.utcnow().isoformat(),
        }
        redis_client.set(self._cache_key(normalized_symbol), json.dumps(signal_payload), ex=AI_SIGNAL_CACHE_SECONDS)
        self._alert_on_classification_change(normalized_symbol, classification, score)
        return signal_payload

    def _alert_on_classification_change(self, symbol: str, classification: str, score: int) -> None:
        classification_key = self._classification_key(symbol)
        previous = redis_client.get(classification_key)
        if previous and previous != classification:
            send_telegram_message(
                (
                    f'📈 AI Trading Signal Changed for {symbol}\n'
                    f'Previous: {previous}\n'
                    f'Current: {classification}\n'
                    f'Score: {score}'
                )
            )
        redis_client.set(classification_key, classification)

    def _cache_key(self, symbol: str) -> str:
        return f'{AI_SIGNAL_CACHE_PREFIX}:{symbol}'

    def _classification_key(self, symbol: str) -> str:
        return f'{AI_SIGNAL_CLASSIFICATION_CACHE_PREFIX}:{symbol}'

    def _score_pcr(self, pcr: float | None) -> float:
        if pcr is None:
            return 50.0
        if pcr >= 1.3:
            return 90.0
        if pcr >= 1.1:
            return 80.0
        if pcr >= 0.95:
            return 60.0
        if pcr >= 0.8:
            return 40.0
        return 20.0

    def _score_change_in_oi(self, put_change: int | None, call_change: int | None) -> float:
        put_value = put_change or 0
        call_value = call_change or 0
        net_change = put_value - call_value
        total_magnitude = abs(put_value) + abs(call_value)
        if total_magnitude == 0:
            return 50.0
        ratio = net_change / total_magnitude
        return max(0.0, min(100.0, 50.0 + (ratio * 50.0)))

    def _score_support_resistance_proximity(
        self,
        underlying: float | None,
        support: float | None,
        resistance: float | None,
    ) -> float:
        if underlying is None or support is None or resistance is None:
            return 50.0
        if support >= resistance:
            return 50.0

        support_distance = max(0.0, (underlying - support) / underlying)
        resistance_distance = max(0.0, (resistance - underlying) / underlying)
        if support_distance + resistance_distance == 0:
            return 50.0

        bullish_bias = resistance_distance - support_distance
        normalized_bias = bullish_bias / (support_distance + resistance_distance)
        return max(0.0, min(100.0, 50.0 + (normalized_bias * 50.0)))

    def _score_oi_buildup(self, put_change: int | None, call_change: int | None, pcr: float | None) -> float:
        put_value = put_change or 0
        call_value = call_change or 0

        if put_value > 0 and call_value < 0:
            return 90.0
        if put_value > 0 and call_value > 0:
            return 70.0 if (pcr or 1.0) >= 1 else 55.0
        if put_value < 0 and call_value > 0:
            return 15.0
        if put_value < 0 and call_value < 0:
            return 45.0
        return 50.0

    def _classify_signal(self, score: int) -> str:
        if score >= 75:
            return 'Strong Bullish'
        if score >= 60:
            return 'Bullish'
        if score >= 40:
            return 'Neutral'
        if score >= 25:
            return 'Bearish'
        return 'Strong Bearish'
