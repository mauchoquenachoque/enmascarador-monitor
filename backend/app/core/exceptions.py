from typing import Any

from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Error interno del servidor",
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(AppException):
    def __init__(self, detail: str = "Credenciales inválidas"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(AppException):
    def __init__(self, detail: str = "No tienes permisos suficientes"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Recurso"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} no encontrado",
        )


class DatabaseConnectionError(AppException):
    def __init__(self, engine: str, detail: str = ""):
        msg = f"Error conectando a {engine}"
        if detail:
            msg += f": {detail}"
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)


class MaskingError(AppException):
    def __init__(self, detail: str = "Error aplicando enmascaramiento"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class BenchmarkError(AppException):
    def __init__(self, detail: str = "Error ejecutando benchmark"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class GovernanceError(AppException):
    def __init__(self, detail: str = "Error en operación de gobernanza"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class RateLimitError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes. Intenta más tarde.",
        )
