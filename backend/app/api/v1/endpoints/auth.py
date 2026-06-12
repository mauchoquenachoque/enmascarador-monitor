from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.auth.service import AuthService
from app.core.dependencies import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
) -> UserResponse:
    service = AuthService(db)
    user = service.register_user(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return service.authenticate_user(data.username, data.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return service.refresh_access_token(data.refresh_token)


@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db),
) -> dict:
    service = AuthService(db)
    service.logout(data.refresh_token)
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user = service.get_user_by_username(current_user["username"])
    if not user:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Usuario")
    return UserResponse.model_validate(user)
