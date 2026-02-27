from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.market import AISignalEngineResponse
from app.services.ai_signal_service import AISignalEngineService

router = APIRouter(prefix='/ai-signal', tags=['ai_signal'])


@router.get('/latest', response_model=AISignalEngineResponse)
def latest_signal(
    current_user: User = Depends(require_role(UserRole.PRO, UserRole.ADMIN)),
) -> AISignalEngineResponse:
    _ = current_user
    signal = AISignalEngineService().get_latest_signal(symbol='NIFTY')
    return AISignalEngineResponse(score=signal['score'], classification=signal['classification'])
