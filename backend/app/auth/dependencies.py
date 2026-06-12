from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.core.logging import get_logger

logger = get_logger("auth")
security_scheme = HTTPBearer()


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    ) -> dict:
        token = credentials.credentials
        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso requerido",
            )

        role = payload.get("role", "viewer")
        if role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol '{role}' no autorizado. Permitidos: {self.allowed_roles}",
            )

        return {"username": payload["sub"], "role": role}


require_admin = RoleChecker(["admin"])
require_analyst = RoleChecker(["admin", "analyst"])
require_viewer = RoleChecker(["admin", "analyst", "viewer"])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    return {"username": payload["sub"], "role": payload.get("role", "viewer")}
