from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.api_usage_log import APIUsageLog
from app.models.feature_flag import FeatureFlag
from app.models.subscription import Subscription
from app.models.user import User, UserRole


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self, *, offset: int, limit: int) -> tuple[list[User], int]:
        total = self.db.scalar(select(func.count()).select_from(User)) or 0
        users = list(self.db.scalars(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)).all())
        return users, total

    def update_user_role(self, *, user_id: int, role: UserRole) -> User | None:
        user = self.db.get(User, user_id)
        if user is None:
            return None
        user.role = role
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_subscriptions(self, *, offset: int, limit: int) -> tuple[list[tuple[Subscription, User]], int]:
        total = self.db.scalar(select(func.count()).select_from(Subscription)) or 0
        rows = list(
            self.db.execute(
                select(Subscription, User)
                .join(User, User.id == Subscription.user_id)
                .order_by(Subscription.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )
        return rows, total

    def list_api_usage_logs(self, *, offset: int, limit: int) -> tuple[list[APIUsageLog], int]:
        total = self.db.scalar(select(func.count()).select_from(APIUsageLog)) or 0
        logs = list(self.db.scalars(select(APIUsageLog).order_by(APIUsageLog.created_at.desc()).offset(offset).limit(limit)).all())
        return logs, total

    def list_feature_flags(self, *, offset: int, limit: int) -> tuple[list[FeatureFlag], int]:
        total = self.db.scalar(select(func.count()).select_from(FeatureFlag)) or 0
        flags = list(self.db.scalars(select(FeatureFlag).order_by(FeatureFlag.name.asc()).offset(offset).limit(limit)).all())
        return flags, total

    def toggle_feature_flag(self, *, name: str, enabled: bool) -> FeatureFlag:
        flag = self.db.scalar(select(FeatureFlag).where(FeatureFlag.name == name))
        if flag is None:
            flag = FeatureFlag(name=name, enabled=enabled)
        else:
            flag.enabled = enabled

        self.db.add(flag)
        self.db.commit()
        self.db.refresh(flag)
        return flag
