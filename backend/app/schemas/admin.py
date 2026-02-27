from datetime import datetime

from pydantic import BaseModel, Field

from app.models.subscription import SubscriptionStatus
from app.models.user import UserRole
from app.schemas.user import UserRead


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedUsersResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    size: int


class SubscriptionAdminRead(BaseModel):
    id: int
    user_id: int
    user_email: str
    status: SubscriptionStatus
    razorpay_order_id: str
    razorpay_payment_id: str | None
    expiry_date: datetime | None
    created_at: datetime


class PaginatedSubscriptionsResponse(BaseModel):
    items: list[SubscriptionAdminRead]
    total: int
    page: int
    size: int


class APIUsageLogRead(BaseModel):
    id: int
    user_id: int | None
    method: str
    path: str
    status_code: int
    ip_address: str | None
    created_at: datetime

    model_config = {'from_attributes': True}


class PaginatedAPIUsageLogsResponse(BaseModel):
    items: list[APIUsageLogRead]
    total: int
    page: int
    size: int


class FeatureFlagRead(BaseModel):
    id: int
    name: str
    enabled: bool
    updated_at: datetime

    model_config = {'from_attributes': True}


class FeatureFlagToggleRequest(BaseModel):
    enabled: bool


class PaginatedFeatureFlagsResponse(BaseModel):
    items: list[FeatureFlagRead]
    total: int
    page: int
    size: int


class UserRoleUpdateRequest(BaseModel):
    role: UserRole
