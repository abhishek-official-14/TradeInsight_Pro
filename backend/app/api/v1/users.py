from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TelegramLinkRequest, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserRead)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead.model_validate(current_user)


@router.put('/me/telegram-link', response_model=UserRead)
def link_telegram(
    payload: TelegramLinkRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserRead:
    user = UserService(db).link_telegram_id(current_user, payload.telegram_id)
    return UserRead.model_validate(user)
