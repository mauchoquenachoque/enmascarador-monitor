import hashlib
import random
import string

from app.masking.base_strategy import MaskingStrategy


class FPEStrategy(MaskingStrategy):
    def __init__(self) -> None:
        self._char_map = self._build_char_map()

    @property
    def name(self) -> str:
        return "fpe"

    @property
    def reversible(self) -> bool:
        return False

    @staticmethod
    def _build_char_map() -> dict[str, str]:
        digits = list(string.digits)
        shuffled_digits = digits.copy()
        random.seed(42)
        random.shuffle(shuffled_digits)
        mapping = dict(zip(digits, shuffled_digits))

        lower = list(string.ascii_lowercase)
        shuffled_lower = lower.copy()
        random.seed(42)
        random.shuffle(shuffled_lower)
        mapping.update(zip(lower, shuffled_lower))

        upper = list(string.ascii_uppercase)
        shuffled_upper = upper.copy()
        random.seed(42)
        random.shuffle(shuffled_upper)
        mapping.update(zip(upper, shuffled_upper))

        return mapping

    def mask(self, value: str) -> str:
        result = []
        for ch in value:
            if ch in self._char_map:
                result.append(self._char_map[ch])
            else:
                result.append(ch)
        return "".join(result)


class FPESimulationStrategy(MaskingStrategy):
    def __init__(self) -> None:
        self._iterations = 5000

    @property
    def name(self) -> str:
        return "fpe"

    @property
    def reversible(self) -> bool:
        return False

    def mask(self, value: str) -> str:
        hash_val = value.encode("utf-8")
        for _ in range(self._iterations):
            hash_val = hashlib.sha256(hash_val).digest()
        return hash_val.hex()[: len(value)]
