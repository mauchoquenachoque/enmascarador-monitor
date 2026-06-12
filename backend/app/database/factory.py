from typing import Any

from app.database.base import BaseDatabase


class DatabaseFactory:
    _engines: dict[str, type[BaseDatabase]] = {}

    @classmethod
    def register(cls, name: str, engine_class: type[BaseDatabase]) -> None:
        cls._engines[name.lower()] = engine_class

    @classmethod
    def create(cls, engine: str, credentials: dict[str, Any]) -> BaseDatabase:
        engine_lower = engine.lower()
        if engine_lower not in cls._engines:
            raise ValueError(
                f"Motor '{engine}' no soportado. Disponibles: {list(cls._engines.keys())}"
            )
        return cls._engines[engine_lower](credentials)

    @classmethod
    def available_engines(cls) -> list[str]:
        return list(cls._engines.keys())
