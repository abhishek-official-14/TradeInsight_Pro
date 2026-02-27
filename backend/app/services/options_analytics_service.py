import json
from datetime import datetime

import requests
from fastapi import HTTPException, status

from app.utils.redis_client import redis_client


NSE_BASE_URL = 'https://www.nseindia.com'
OPTION_CHAIN_INDICES_ENDPOINT = '/api/option-chain-indices'
OPTION_CHAIN_EQUITIES_ENDPOINT = '/api/option-chain-equities'
OPTIONS_ANALYTICS_CACHE_PREFIX = 'options:analytics'
OPTIONS_ANALYTICS_CACHE_SECONDS = 60
INDEX_SYMBOLS = {'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'NIFTYNXT50'}


class OptionsAnalyticsService:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{NSE_BASE_URL}/option-chain',
            }
        )

    def get_analytics(self, symbol: str, expiry_date: str | None = None) -> dict:
        normalized_symbol = symbol.strip().upper()
        cache_key = self._cache_key(normalized_symbol, expiry_date)
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        payload = self._fetch_option_chain_payload(normalized_symbol)
        selected_expiry = expiry_date or payload['records'].get('expiryDates', [None])[0]
        if not selected_expiry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Expiry date unavailable for selected symbol',
            )

        rows = [
            row
            for row in payload['records'].get('data', [])
            if row.get('expiryDate') == selected_expiry
        ]
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No option chain data found for selected expiry',
            )

        analytics = self._calculate_analytics(rows)
        response_payload = {
            'symbol': normalized_symbol,
            'expiry_date': selected_expiry,
            'underlying_value': self._safe_float(payload['records'].get('underlyingValue')),
            'timestamp': datetime.utcnow().isoformat(),
            **analytics,
        }
        redis_client.set(cache_key, json.dumps(response_payload), ex=OPTIONS_ANALYTICS_CACHE_SECONDS)
        return response_payload

    def _fetch_option_chain_payload(self, symbol: str) -> dict:
        endpoint = (
            OPTION_CHAIN_INDICES_ENDPOINT if symbol in INDEX_SYMBOLS else OPTION_CHAIN_EQUITIES_ENDPOINT
        )
        try:
            self.session.get(f'{NSE_BASE_URL}/option-chain', timeout=10)
            response = self.session.get(
                f'{NSE_BASE_URL}{endpoint}',
                params={'symbol': symbol},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='NSE option chain is currently unavailable',
            ) from exc

        if 'records' not in payload:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Invalid option chain payload from NSE',
            )
        return payload

    def _calculate_analytics(self, rows: list[dict]) -> dict:
        total_call_oi = calculate_total_call_oi(rows)
        total_put_oi = calculate_total_put_oi(rows)
        total_call_change_oi, total_put_change_oi = calculate_change_in_oi(rows)

        return {
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'pcr': calculate_pcr(total_put_oi, total_call_oi),
            'change_in_call_oi': total_call_change_oi,
            'change_in_put_oi': total_put_change_oi,
            'change_oi_pcr': calculate_pcr(total_put_change_oi, total_call_change_oi),
            'strongest_support': calculate_strongest_support(rows),
            'strongest_resistance': calculate_strongest_resistance(rows),
            'max_pain': calculate_max_pain(rows),
        }

    def _cache_key(self, symbol: str, expiry_date: str | None) -> str:
        expiry_segment = expiry_date or 'nearest'
        return f'{OPTIONS_ANALYTICS_CACHE_PREFIX}:{symbol}:{expiry_segment}'

    def _safe_float(self, value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def calculate_total_call_oi(rows: list[dict]) -> int:
    return sum(int((row.get('CE') or {}).get('openInterest', 0) or 0) for row in rows)


def calculate_total_put_oi(rows: list[dict]) -> int:
    return sum(int((row.get('PE') or {}).get('openInterest', 0) or 0) for row in rows)


def calculate_change_in_oi(rows: list[dict]) -> tuple[int, int]:
    total_call_change_oi = sum(int((row.get('CE') or {}).get('changeinOpenInterest', 0) or 0) for row in rows)
    total_put_change_oi = sum(int((row.get('PE') or {}).get('changeinOpenInterest', 0) or 0) for row in rows)
    return total_call_change_oi, total_put_change_oi


def calculate_pcr(put_oi: int, call_oi: int) -> float | None:
    if call_oi == 0:
        return None
    return round(put_oi / call_oi, 6)


def calculate_strongest_support(rows: list[dict]) -> float | None:
    support_row = max(rows, key=lambda row: int((row.get('PE') or {}).get('openInterest', 0) or 0), default=None)
    if support_row is None:
        return None
    return float(support_row.get('strikePrice'))


def calculate_strongest_resistance(rows: list[dict]) -> float | None:
    resistance_row = max(rows, key=lambda row: int((row.get('CE') or {}).get('openInterest', 0) or 0), default=None)
    if resistance_row is None:
        return None
    return float(resistance_row.get('strikePrice'))


def calculate_max_pain(rows: list[dict]) -> float | None:
    if not rows:
        return None

    strike_rows: list[tuple[float, int, int]] = []
    for row in rows:
        strike = row.get('strikePrice')
        if strike is None:
            continue
        strike_rows.append(
            (
                float(strike),
                int((row.get('CE') or {}).get('openInterest', 0) or 0),
                int((row.get('PE') or {}).get('openInterest', 0) or 0),
            )
        )

    if not strike_rows:
        return None

    pain_by_strike: dict[float, float] = {}
    for candidate_strike, _, _ in strike_rows:
        total_pain = 0.0
        for strike, call_oi, put_oi in strike_rows:
            total_pain += max(0.0, candidate_strike - strike) * call_oi
            total_pain += max(0.0, strike - candidate_strike) * put_oi
        pain_by_strike[candidate_strike] = total_pain

    return min(pain_by_strike, key=pain_by_strike.get)
