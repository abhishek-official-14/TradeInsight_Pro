from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.feature_flag import FeatureFlag
from app.models.subscription import Subscription
from app.models.user import User, UserRole
from app.repositories.admin_repository import AdminRepository


class AdminService:
    def __init__(self, db: Session) -> None:
        self.repository = AdminRepository(db)

    def list_users(self, *, page: int, size: int) -> tuple[list[User], int]:
        offset = (page - 1) * size
        return self.repository.list_users(offset=offset, limit=size)

    def update_user_role(self, *, user_id: int, role: UserRole) -> User:
        user = self.repository.update_user_role(user_id=user_id, role=role)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user

    def list_subscriptions(self, *, page: int, size: int) -> tuple[list[tuple[Subscription, User]], int]:
        offset = (page - 1) * size
        return self.repository.list_subscriptions(offset=offset, limit=size)

    def list_api_usage_logs(self, *, page: int, size: int):
        offset = (page - 1) * size
        return self.repository.list_api_usage_logs(offset=offset, limit=size)

    def list_feature_flags(self, *, page: int, size: int) -> tuple[list[FeatureFlag], int]:
        offset = (page - 1) * size
        return self.repository.list_feature_flags(offset=offset, limit=size)

    def toggle_feature_flag(self, *, name: str, enabled: bool) -> FeatureFlag:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Feature flag name is required')
        return self.repository.toggle_feature_flag(name=normalized_name, enabled=enabled)
