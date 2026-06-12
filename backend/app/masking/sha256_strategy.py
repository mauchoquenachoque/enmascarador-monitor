import hashlib

from app.masking.base_strategy import MaskingStrategy


class SHA256Strategy(MaskingStrategy):
    @property
    def name(self) -> str:
        return "hashing"

    @property
    def reversible(self) -> bool:
        return False

    def mask(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16] + "..."
