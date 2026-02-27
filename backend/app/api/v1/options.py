from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.market import OptionContractRead, OptionsAnalyticsResponse
from app.services.market_service import MarketService
from app.services.options_analytics_service import OptionsAnalyticsService

router = APIRouter(prefix='/options', tags=['options'])


@router.get('/latest', response_model=list[OptionContractRead])
def latest_options(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.PRO, UserRole.ADMIN)),
) -> list[OptionContractRead]:
    _ = current_user
    options = MarketService(db).get_latest_options(limit=limit)
    return [OptionContractRead.model_validate(item) for item in options]


@router.get('/analytics', response_model=OptionsAnalyticsResponse)
def option_chain_analytics(
    symbol: str = Query(default='NIFTY', min_length=1, max_length=30),
    expiry_date: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
) -> OptionsAnalyticsResponse:
    _ = current_user
    payload = OptionsAnalyticsService().get_analytics(symbol=symbol, expiry_date=expiry_date)
    return OptionsAnalyticsResponse.model_validate(payload)
