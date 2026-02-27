from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.subscription import SubscriptionStatus


class SubscriptionOrderCreateRequest(BaseModel):
    amount: int = Field(gt=0, description='Amount in paise')
    currency: Literal['INR'] = 'INR'


class SubscriptionOrderCreateResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    status: SubscriptionStatus
    razorpay_order_id: str
    razorpay_payment_id: str | None
    expiry_date: datetime | None

    model_config = {'from_attributes': True}


class RazorpayWebhookPaymentEntity(BaseModel):
    order_id: str
    id: str


class RazorpayWebhookPaymentPayload(BaseModel):
    entity: RazorpayWebhookPaymentEntity


class RazorpayWebhookPayload(BaseModel):
    event: str
    payload: dict
