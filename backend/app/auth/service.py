from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_refresh_token_valid,
    revoke_refresh_token,
    store_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate

logger = get_logger("auth_service")
settings = get_settings()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, user_data: UserCreate) -> User:
        existing = (
            self.db.query(User)
            .filter((User.username == user_data.username) | (User.email == user_data.email))
            .first()
        )
        if existing:
            raise AuthenticationError("Usuario o email ya existe")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("user_registered", username=user.username, role=user.role)
        return user

    def authenticate_user(self, username: str, password: str) -> TokenResponse:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Credenciales inválidas")

        if not user.is_active:
            raise AuthenticationError("Usuario desactivado")

        access_token = create_access_token(subject=user.username, role=user.role)
        refresh_token = create_refresh_token(subject=user.username)
        store_refresh_token(refresh_token)

        logger.info("user_authenticated", username=user.username, role=user.role)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Refresh token inválido")

        if not is_refresh_token_valid(refresh_token):
            raise AuthenticationError("Refresh token revocado")

        username = payload["sub"]
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise AuthenticationError("Usuario no encontrado")

        revoke_refresh_token(refresh_token)
        new_access = create_access_token(subject=user.username, role=user.role)
        new_refresh = create_refresh_token(subject=user.username)
        store_refresh_token(new_refresh)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout(self, refresh_token: str) -> None:
        revoke_refresh_token(refresh_token)
        logger.info("user_logged_out")

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
