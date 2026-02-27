from datetime import datetime

from pydantic import BaseModel


class NiftySnapshotRead(BaseModel):
    id: int
    symbol: str
    price: float
    captured_at: datetime

    model_config = {'from_attributes': True}


class OptionContractRead(BaseModel):
    id: int
    symbol: str
    strike_price: float
    premium: float
    option_type: str
    updated_at: datetime | None

    model_config = {'from_attributes': True}


class AISignalRead(BaseModel):
    id: int
    symbol: str
    signal: str
    confidence: float
    generated_at: datetime

    model_config = {'from_attributes': True}
