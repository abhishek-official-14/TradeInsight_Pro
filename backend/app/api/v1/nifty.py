from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.market import NiftyImpactResponse, NiftySnapshotRead
from app.services.market_service import MarketService
from app.services.nifty_analytics_service import NiftyAnalyticsService

router = APIRouter(prefix='/nifty', tags=['nifty'])


@router.get('/latest', response_model=NiftySnapshotRead)
def latest_nifty(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NiftySnapshotRead:
    _ = current_user
    snapshot = MarketService(db).get_latest_nifty()
    return NiftySnapshotRead.model_validate(snapshot)


@router.get('/impact', response_model=NiftyImpactResponse)
def nifty_impact(
    current_user: User = Depends(get_current_user),
) -> NiftyImpactResponse:
    _ = current_user
    payload = NiftyAnalyticsService().get_impact_snapshot()
    return NiftyImpactResponse.model_validate(payload)
