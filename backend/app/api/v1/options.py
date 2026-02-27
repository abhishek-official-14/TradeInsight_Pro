from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.market import OptionContractRead
from app.services.market_service import MarketService

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
