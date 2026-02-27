from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.user import UserRead, UserRoleUpdate
from app.services.user_service import UserService

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/users', response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> list[UserRead]:
    _ = current_user
    users = UserService(db).list_users()
    return [UserRead.model_validate(user) for user in users]


@router.patch('/users/{user_id}/role', response_model=UserRead)
def update_user_role(
    payload: UserRoleUpdate,
    user_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserRead:
    _ = current_user
    updated = UserService(db).update_role(user_id=user_id, role=payload.role)
    return UserRead.model_validate(updated)
