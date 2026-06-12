from typing import Any

from app.masking.aes_strategy import AESStrategy
from app.masking.base_strategy import MaskingStrategy
from app.masking.fpe_strategy import FPEStrategy
from app.masking.redaction_strategy import RedactionStrategy
from app.masking.sha256_strategy import SHA256Strategy


class MaskingFactory:
    _strategies: dict[str, type[MaskingStrategy]] = {}
    _instances: dict[str, MaskingStrategy] = {}

    @classmethod
    def register(cls, key: str, strategy_class: type[MaskingStrategy]) -> None:
        cls._strategies[key.lower()] = strategy_class

    @classmethod
    def get(cls, algorithm: str) -> MaskingStrategy:
        key = algorithm.lower()
        if key not in cls._instances:
            if key not in cls._strategies:
                raise ValueError(
                    f"Algoritmo '{algorithm}' no registrado. "
                    f"Disponibles: {list(cls._strategies.keys())}"
                )
            cls._instances[key] = cls._strategies[key]()
        return cls._instances[key]

    @classmethod
    def available(cls) -> list[dict[str, Any]]:
        result = []
        for key, strategy_class in cls._strategies.items():
            s = strategy_class()
            result.append(
                {
                    "name": s.name,
                    "key": key,
                    "reversible": s.reversible,
                }
            )
        return result

    @classmethod
    def apply_masking(
        cls,
        data: list[dict[str, Any]],
        rules: dict[str, str],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        if not rules:
            return data, []

        algorithms_used = set()
        masked_data = data

        for column, algorithm in rules.items():
            strategy = cls.get(algorithm)
            algorithms_used.add(algorithm)
            masked_data = strategy.mask_dict(masked_data, {column: algorithm})

        return masked_data, list(algorithms_used)


MaskingFactory.register("redaccion", RedactionStrategy)
MaskingFactory.register("redaction", RedactionStrategy)
MaskingFactory.register("hashing", SHA256Strategy)
MaskingFactory.register("sha256", SHA256Strategy)
MaskingFactory.register("encriptacion", AESStrategy)
MaskingFactory.register("aes", AESStrategy)
MaskingFactory.register("fpe", FPEStrategy)
