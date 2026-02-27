from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market_data import AISignal, NiftySnapshot, OptionContract
from app.repositories.base_repository import BaseRepository


class MarketRepository(BaseRepository[NiftySnapshot]):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def latest_nifty(self) -> NiftySnapshot | None:
        return self.db.scalar(select(NiftySnapshot).order_by(NiftySnapshot.captured_at.desc()).limit(1))

    def latest_options(self, limit: int = 20) -> list[OptionContract]:
        return list(self.db.scalars(select(OptionContract).order_by(OptionContract.updated_at.desc()).limit(limit)).all())

    def latest_ai_signal(self) -> AISignal | None:
        return self.db.scalar(select(AISignal).order_by(AISignal.generated_at.desc()).limit(1))
