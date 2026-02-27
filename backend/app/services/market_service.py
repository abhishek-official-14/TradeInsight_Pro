from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.market_data import AISignal, NiftySnapshot, OptionContract
from app.repositories.market_repository import MarketRepository


class MarketService:
    def __init__(self, db: Session) -> None:
        self.market_repository = MarketRepository(db)

    def get_latest_nifty(self) -> NiftySnapshot:
        snapshot = self.market_repository.latest_nifty()
        if snapshot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Nifty data not found')
        return snapshot

    def get_latest_options(self, limit: int = 20) -> list[OptionContract]:
        return self.market_repository.latest_options(limit=limit)

    def get_latest_signal(self) -> AISignal:
        signal = self.market_repository.latest_ai_signal()
        if signal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Signal not found')
        return signal
