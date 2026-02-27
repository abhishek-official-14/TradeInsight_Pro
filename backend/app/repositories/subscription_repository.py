from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription, SubscriptionStatus
from app.repositories.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def create_pending(self, *, user_id: int, razorpay_order_id: str) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            razorpay_order_id=razorpay_order_id,
            status=SubscriptionStatus.PENDING,
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_by_order_id(self, order_id: str) -> Subscription | None:
        return self.db.scalar(select(Subscription).where(Subscription.razorpay_order_id == order_id))

    def mark_active(self, subscription: Subscription, *, payment_id: str, expiry_date: datetime) -> Subscription:
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.razorpay_payment_id = payment_id
        subscription.expiry_date = expiry_date
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def mark_failed(self, subscription: Subscription, *, payment_id: str | None = None) -> Subscription:
        subscription.status = SubscriptionStatus.FAILED
        if payment_id:
            subscription.razorpay_payment_id = payment_id
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
