import json
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    PaymentVerifyRequest,
    SubscriptionOrderCreateRequest,
    SubscriptionOrderCreateResponse,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix='/subscription', tags=['subscription'])


@router.post('/create-order', response_model=SubscriptionOrderCreateResponse)
def create_order(
    payload: SubscriptionOrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionOrderCreateResponse:
    order = SubscriptionService(db).create_order(current_user, payload)
    return SubscriptionOrderCreateResponse(**order)


@router.post('/verify-payment', status_code=status.HTTP_200_OK)
def verify_payment(
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    SubscriptionService(db).verify_payment(current_user, payload)
    return {'message': 'Payment verified successfully'}


@router.post('/webhook', include_in_schema=False)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    body = await request.body()
    service = SubscriptionService(db)
    service.process_webhook(body=body, signature=x_razorpay_signature)

    try:
        payload = json.loads(body.decode())
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid webhook payload') from exc

    event = payload.get('event')
    payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    order_id = payment_entity.get('order_id')
    payment_id = payment_entity.get('id')

    if not isinstance(order_id, str):
        return {'message': 'Webhook accepted'}

    subscription = service.subscription_repository.get_by_order_id(order_id)
    if subscription is None:
        return {'message': 'Webhook accepted'}

    if event == 'payment.failed':
        service.subscription_repository.mark_failed(subscription, payment_id=payment_id if isinstance(payment_id, str) else None)
        return {'message': 'Webhook accepted'}

    if event == 'payment.captured' and isinstance(payment_id, str):
        service.activate_subscription(subscription, payment_id)

    return {'message': 'Webhook accepted'}
