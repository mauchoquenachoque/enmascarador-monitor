from app.masking.base_strategy import MaskingStrategy


class RedactionStrategy(MaskingStrategy):
    @property
    def name(self) -> str:
        return "redaccion"

    @property
    def reversible(self) -> bool:
        return False

    def mask(self, value: str) -> str:
        return "X" * len(value)
