from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.market import AISignalRead
from app.services.market_service import MarketService

router = APIRouter(prefix='/ai-signal', tags=['ai_signal'])


@router.get('/latest', response_model=AISignalRead)
def latest_signal(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PRO, UserRole.ADMIN)),
) -> AISignalRead:
    _ = current_user
    signal = MarketService(db).get_latest_signal()
    return AISignalRead.model_validate(signal)
