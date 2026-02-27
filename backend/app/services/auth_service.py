from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import TokenType, create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate
from app.utils.rate_limiter import enforce_auth_rate_limit

settings = get_settings()


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
        enforce_auth_rate_limit(payload.email)
        user = self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')

        return Token(
            access_token=create_access_token(subject=user.email),
            refresh_token=create_refresh_token(subject=user.email),
        )

    def refresh_access_token(self, refresh_token: str) -> Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            subject = payload.get('sub')
            token_type = payload.get('type')
            if not isinstance(subject, str) or token_type != TokenType.REFRESH:
                raise credentials_exception
        except JWTError as exc:
            raise credentials_exception from exc

        user = self.user_repository.get_by_email(subject)
        if user is None or not user.is_active:
            raise credentials_exception

        return Token(
            access_token=create_access_token(subject=user.email),
            refresh_token=create_refresh_token(subject=user.email),
        )
