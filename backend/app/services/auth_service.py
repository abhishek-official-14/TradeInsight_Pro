from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        existing = self.user_repository.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')

        return self.user_repository.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )

    def login(self, payload: LoginRequest) -> Token:
        user = self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')

        token = create_access_token(subject=user.email)
        return Token(access_token=token)
