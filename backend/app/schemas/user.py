from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class TelegramLinkRequest(BaseModel):
    telegram_id: str = Field(min_length=1, max_length=64)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    telegram_id: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {'from_attributes': True}


class UserRoleUpdate(BaseModel):
    role: UserRole
