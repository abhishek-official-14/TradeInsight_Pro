from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.admin import (
    APIUsageLogRead,
    FeatureFlagRead,
    FeatureFlagToggleRequest,
    PaginatedAPIUsageLogsResponse,
    PaginatedFeatureFlagsResponse,
    PaginatedSubscriptionsResponse,
    PaginatedUsersResponse,
    SubscriptionAdminRead,
)
from app.schemas.user import UserRead, UserRoleUpdate
from app.services.admin_service import AdminService

router = APIRouter(prefix='/admin', tags=['admin'])


Page = Annotated[int, Query(ge=1, description='Page number (1-indexed)')]
Size = Annotated[int, Query(ge=1, le=100, description='Page size')]


@router.get('/users', response_model=PaginatedUsersResponse)
def list_users(
    page: Page = 1,
    size: Size = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> PaginatedUsersResponse:
    _ = current_user
    users, total = AdminService(db).list_users(page=page, size=size)
    return PaginatedUsersResponse(
        items=[UserRead.model_validate(user) for user in users],
        total=total,
        page=page,
        size=size,
    )


@router.patch('/users/{user_id}/role', response_model=UserRead)
def update_user_role(
    payload: UserRoleUpdate,
    user_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserRead:
    _ = current_user
    updated = AdminService(db).update_user_role(user_id=user_id, role=payload.role)
    return UserRead.model_validate(updated)


@router.get('/subscriptions', response_model=PaginatedSubscriptionsResponse)
def list_subscriptions(
    page: Page = 1,
    size: Size = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> PaginatedSubscriptionsResponse:
    _ = current_user
    rows, total = AdminService(db).list_subscriptions(page=page, size=size)
    return PaginatedSubscriptionsResponse(
        items=[
            SubscriptionAdminRead(
                id=subscription.id,
                user_id=subscription.user_id,
                user_email=user.email,
                status=subscription.status,
                razorpay_order_id=subscription.razorpay_order_id,
                razorpay_payment_id=subscription.razorpay_payment_id,
                expiry_date=subscription.expiry_date,
                created_at=subscription.created_at,
            )
            for subscription, user in rows
        ],
        total=total,
        page=page,
        size=size,
    )


@router.get('/api-usage-logs', response_model=PaginatedAPIUsageLogsResponse)
def list_api_usage_logs(
    page: Page = 1,
    size: Size = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> PaginatedAPIUsageLogsResponse:
    _ = current_user
    logs, total = AdminService(db).list_api_usage_logs(page=page, size=size)
    return PaginatedAPIUsageLogsResponse(
        items=[APIUsageLogRead.model_validate(log) for log in logs],
        total=total,
        page=page,
        size=size,
    )


@router.get('/feature-flags', response_model=PaginatedFeatureFlagsResponse)
def list_feature_flags(
    page: Page = 1,
    size: Size = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> PaginatedFeatureFlagsResponse:
    _ = current_user
    flags, total = AdminService(db).list_feature_flags(page=page, size=size)
    return PaginatedFeatureFlagsResponse(
        items=[FeatureFlagRead.model_validate(flag) for flag in flags],
        total=total,
        page=page,
        size=size,
    )


@router.patch('/feature-flags/{name}', response_model=FeatureFlagRead)
def toggle_feature_flag(
    payload: FeatureFlagToggleRequest,
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> FeatureFlagRead:
    _ = current_user
    flag = AdminService(db).toggle_feature_flag(name=name, enabled=payload.enabled)
    return FeatureFlagRead.model_validate(flag)
