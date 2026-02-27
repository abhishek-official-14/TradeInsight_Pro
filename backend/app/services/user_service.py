from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def list_users(self) -> list[User]:
        return self.user_repository.list_all()

    def update_role(self, user_id: int, role: UserRole) -> User:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return self.user_repository.update_role(user, role)

    def link_telegram_id(self, user: User, telegram_id: str) -> User:
        normalized_telegram_id = telegram_id.strip()
        if not normalized_telegram_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Telegram ID is required')

        existing_user = self.user_repository.get_by_id(user.id)
        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        users_with_telegram = self.user_repository.list_with_telegram_id()
        if any(candidate.id != existing_user.id and candidate.telegram_id == normalized_telegram_id for candidate in users_with_telegram):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Telegram ID already linked to another user')

        return self.user_repository.update_telegram_id(existing_user, normalized_telegram_id)
