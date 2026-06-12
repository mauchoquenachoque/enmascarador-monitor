from abc import ABC, abstractmethod
from typing import Any


class MaskingStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def reversible(self) -> bool:
        pass

    @abstractmethod
    def mask(self, value: str) -> str:
        pass

    def mask_dict(
        self, data: list[dict[str, Any]], rules: dict[str, str]
    ) -> list[dict[str, Any]]:
        masked = []
        for row in data:
            new_row = row.copy()
            for column, algorithm in rules.items():
                if column in new_row and isinstance(new_row[column], str):
                    new_row[column] = self.mask(new_row[column])
            masked.append(new_row)
        return masked
