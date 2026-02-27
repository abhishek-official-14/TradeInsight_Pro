import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User, UserRole
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.subscription import PaymentVerifyRequest, SubscriptionOrderCreateRequest

settings = get_settings()


class SubscriptionService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)
        self.subscription_repository = SubscriptionRepository(db)

    def _build_auth(self) -> tuple[str, str]:
        return settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET

    def create_order(self, user: User, payload: SubscriptionOrderCreateRequest) -> dict[str, str | int]:
        request_payload = {
            'amount': payload.amount,
            'currency': payload.currency,
            'receipt': f'user-{user.id}-{int(datetime.now(tz=timezone.utc).timestamp())}',
            'notes': {'user_id': str(user.id)},
        }
        try:
            response = requests.post(
                'https://api.razorpay.com/v1/orders',
                auth=self._build_auth(),
                json=request_payload,
                timeout=10,
            )
        except requests.RequestException as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Unable to create Razorpay order') from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Razorpay order creation failed')

        order = response.json()
        order_id = order.get('id')
        if not isinstance(order_id, str):
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Invalid Razorpay response')

        self.subscription_repository.create_pending(user_id=user.id, razorpay_order_id=order_id)
        return {
            'order_id': order_id,
            'amount': payload.amount,
            'currency': payload.currency,
            'key_id': settings.RAZORPAY_KEY_ID,
        }

    def verify_payment(self, user: User, payload: PaymentVerifyRequest) -> None:
        subscription = self.subscription_repository.get_by_order_id(payload.razorpay_order_id)
        if subscription is None or subscription.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subscription order not found')

        generated_signature = self.generate_payment_signature(
            order_id=payload.razorpay_order_id,
            payment_id=payload.razorpay_payment_id,
        )

        if not hmac.compare_digest(generated_signature, payload.razorpay_signature):
            self.subscription_repository.mark_failed(subscription, payment_id=payload.razorpay_payment_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid payment signature')

        self.activate_subscription(subscription, payload.razorpay_payment_id)

    def process_webhook(self, *, body: bytes, signature: str | None) -> None:
        if not signature:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing webhook signature')

        expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid webhook signature')

    def generate_payment_signature(self, *, order_id: str, payment_id: str) -> str:
        return hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f'{order_id}|{payment_id}'.encode(),
            hashlib.sha256,
        ).hexdigest()

    def activate_subscription(self, subscription: Subscription, payment_id: str) -> None:
        expiry = datetime.now(tz=timezone.utc) + timedelta(days=settings.SUBSCRIPTION_DURATION_DAYS)
        self.subscription_repository.mark_active(subscription, payment_id=payment_id, expiry_date=expiry)
        user = self.user_repository.get_by_id(subscription.user_id)
        if user:
            self.user_repository.update_role(user, UserRole.PRO)
