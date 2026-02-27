import json
from dataclasses import dataclass

import requests
from fastapi import HTTPException, status

from app.utils.redis_client import redis_client


NSE_BASE_URL = 'https://www.nseindia.com'
NIFTY_50_INDEX = 'NIFTY 50'
WEIGHTS_CACHE_KEY = 'nifty:50:weights'
LIVE_CACHE_KEY = 'nifty:50:live'
WEIGHTS_CACHE_SECONDS = 15 * 60
LIVE_CACHE_SECONDS = 5 * 60


@dataclass
class NiftyConstituent:
    symbol: str
    company_name: str
    weight: float
    last_price: float
    percent_change: float

    @property
    def impact(self) -> float:
        return self.weight * self.percent_change


class NiftyAnalyticsService:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{NSE_BASE_URL}/',
            }
        )

    def get_impact_snapshot(self) -> dict:
        weights = self._get_weights()
        live_changes = self._get_live_changes()

        constituents: list[NiftyConstituent] = []
        for symbol, weight_payload in weights.items():
            live_payload = live_changes.get(symbol)
            if live_payload is None:
                continue

            constituent = NiftyConstituent(
                symbol=symbol,
                company_name=weight_payload['company_name'],
                weight=weight_payload['weight'],
                last_price=live_payload['last_price'],
                percent_change=live_payload['percent_change'],
            )
            constituents.append(constituent)

        if not constituents:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Nifty live data unavailable',
            )

        constituents.sort(key=lambda row: row.impact)
        top_draggers = constituents[:5]
        total_impact = sum(row.impact for row in constituents)

        return {
            'index': NIFTY_50_INDEX,
            'total_impact': round(total_impact, 6),
            'top_draggers': [self._to_dict(row) for row in top_draggers],
            'constituents': [self._to_dict(row) for row in constituents],
        }

    def _to_dict(self, row: NiftyConstituent) -> dict:
        return {
            'symbol': row.symbol,
            'company_name': row.company_name,
            'weight': round(row.weight, 6),
            'last_price': round(row.last_price, 2),
            'percent_change': round(row.percent_change, 4),
            'impact': round(row.impact, 6),
        }

    def _get_weights(self) -> dict[str, dict]:
        cached = redis_client.get(WEIGHTS_CACHE_KEY)
        if cached:
            return json.loads(cached)

        payload = self._fetch_nifty50_payload()
        weights: dict[str, dict] = {}
        for item in payload.get('data', []):
            symbol = str(item.get('symbol', '')).strip().upper()
            if not symbol:
                continue

            weight = self._safe_float(item.get('weightage'))
            if weight is None:
                continue

            weights[symbol] = {
                'company_name': str(item.get('meta', {}).get('companyName') or symbol),
                'weight': weight,
            }

        if not weights:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Unable to fetch Nifty 50 weights',
            )

        redis_client.set(WEIGHTS_CACHE_KEY, json.dumps(weights), ex=WEIGHTS_CACHE_SECONDS)
        return weights

    def _get_live_changes(self) -> dict[str, dict]:
        cached = redis_client.get(LIVE_CACHE_KEY)
        if cached:
            return json.loads(cached)

        payload = self._fetch_nifty50_payload()
        live_changes: dict[str, dict] = {}

        for item in payload.get('data', []):
            symbol = str(item.get('symbol', '')).strip().upper()
            if not symbol:
                continue

            last_price = self._safe_float(item.get('lastPrice'))
            percent_change = self._safe_float(item.get('pChange'))
            if last_price is None or percent_change is None:
                continue

            live_changes[symbol] = {
                'last_price': last_price,
                'percent_change': percent_change,
            }

        if not live_changes:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Unable to fetch Nifty 50 live prices',
            )

        redis_client.set(LIVE_CACHE_KEY, json.dumps(live_changes), ex=LIVE_CACHE_SECONDS)
        return live_changes

    def _fetch_nifty50_payload(self) -> dict:
        try:
            self.session.get(f'{NSE_BASE_URL}/', timeout=10)
            response = self.session.get(
                f'{NSE_BASE_URL}/api/equity-stockIndices',
                params={'index': NIFTY_50_INDEX},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='NSE is currently unavailable',
            ) from exc

    def _safe_float(self, value: object) -> float | None:
        if value is None:
            return None

        if isinstance(value, str):
            cleaned = value.replace(',', '').strip()
            if not cleaned or cleaned == '-':
                return None
            value = cleaned

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
