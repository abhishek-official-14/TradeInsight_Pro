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
