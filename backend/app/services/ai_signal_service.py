import json
from datetime import datetime

from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.options_analytics_service import OptionsAnalyticsService
from app.utils.redis_client import redis_client
from app.utils.telegram_client import send_bulk_telegram_messages

AI_SIGNAL_CACHE_PREFIX = 'ai:signal'
AI_SIGNAL_CLASSIFICATION_CACHE_PREFIX = 'ai:signal:classification'
AI_ALERT_STATE_CACHE_PREFIX = 'ai:alert:state'
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
        self._process_alerts(
            symbol=normalized_symbol,
            analytics=analytics,
            classification=classification,
            score=score,
        )
        return signal_payload

    def _process_alerts(self, *, symbol: str, analytics: dict, classification: str, score: int) -> None:
        chat_ids = self._linked_chat_ids()
        if not chat_ids:
            return

        self._alert_on_classification_change(symbol, classification, score, chat_ids)
        self._alert_on_pcr_extreme(symbol, analytics.get('pcr'), chat_ids)
        self._alert_on_support_break(
            symbol,
            analytics.get('underlying_value'),
            analytics.get('strongest_support'),
            chat_ids,
        )
        self._alert_on_resistance_break(
            symbol,
            analytics.get('underlying_value'),
            analytics.get('strongest_resistance'),
            chat_ids,
        )

    def _linked_chat_ids(self) -> list[str]:
        db = SessionLocal()
        try:
            users = UserRepository(db).list_with_telegram_id()
            return [user.telegram_id for user in users if user.telegram_id]
        finally:
            db.close()

    def _alert_on_classification_change(self, symbol: str, classification: str, score: int, chat_ids: list[str]) -> None:
        classification_key = self._classification_key(symbol)
        previous = redis_client.get(classification_key)
        if previous and previous != classification:
            send_bulk_telegram_messages(
                chat_ids,
                (
                    f'📈 AI Trading Signal Changed for {symbol}\n'
                    f'Previous: {previous}\n'
                    f'Current: {classification}\n'
                    f'Score: {score}'
                ),
            )
        redis_client.set(classification_key, classification)

    def _alert_on_pcr_extreme(self, symbol: str, pcr: float | None, chat_ids: list[str]) -> None:
        if pcr is None:
            return
        state_key = self._alert_state_key(symbol, 'pcr_extreme')
        is_extreme = pcr >= 1.3 or pcr <= 0.7
        previous_state = redis_client.get(state_key) == '1'
        if is_extreme and not previous_state:
            direction = 'Bullish Extreme' if pcr >= 1.3 else 'Bearish Extreme'
            send_bulk_telegram_messages(
                chat_ids,
                f'⚠️ PCR Extreme for {symbol}\nPCR: {pcr}\nState: {direction}',
            )
        redis_client.set(state_key, '1' if is_extreme else '0')

    def _alert_on_support_break(
        self,
        symbol: str,
        underlying: float | None,
        support: float | None,
        chat_ids: list[str],
    ) -> None:
        if underlying is None or support is None:
            return
        state_key = self._alert_state_key(symbol, 'support_break')
        is_broken = underlying < support
        previous_state = redis_client.get(state_key) == '1'
        if is_broken and not previous_state:
            send_bulk_telegram_messages(
                chat_ids,
                f'🔻 Support Break for {symbol}\nUnderlying: {underlying}\nSupport: {support}',
            )
        redis_client.set(state_key, '1' if is_broken else '0')

    def _alert_on_resistance_break(
        self,
        symbol: str,
        underlying: float | None,
        resistance: float | None,
        chat_ids: list[str],
    ) -> None:
        if underlying is None or resistance is None:
            return
        state_key = self._alert_state_key(symbol, 'resistance_break')
        is_broken = underlying > resistance
        previous_state = redis_client.get(state_key) == '1'
        if is_broken and not previous_state:
            send_bulk_telegram_messages(
                chat_ids,
                f'🚀 Resistance Break for {symbol}\nUnderlying: {underlying}\nResistance: {resistance}',
            )
        redis_client.set(state_key, '1' if is_broken else '0')

    def _cache_key(self, symbol: str) -> str:
        return f'{AI_SIGNAL_CACHE_PREFIX}:{symbol}'

    def _classification_key(self, symbol: str) -> str:
        return f'{AI_SIGNAL_CLASSIFICATION_CACHE_PREFIX}:{symbol}'

    def _alert_state_key(self, symbol: str, alert_type: str) -> str:
        return f'{AI_ALERT_STATE_CACHE_PREFIX}:{symbol}:{alert_type}'

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
