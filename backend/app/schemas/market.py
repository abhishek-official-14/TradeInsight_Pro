from datetime import datetime

from pydantic import BaseModel, RootModel


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


class NiftyConstituentImpact(BaseModel):
    symbol: str
    company_name: str
    weight: float
    last_price: float
    percent_change: float
    impact: float


class NiftyImpactResponse(BaseModel):
    index: str
    total_impact: float
    top_draggers: list[NiftyConstituentImpact]
    constituents: list[NiftyConstituentImpact]


class SectorImpactHeatmapResponse(RootModel[dict[str, float]]):
    pass
