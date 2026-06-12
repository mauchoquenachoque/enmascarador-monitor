from abc import ABC, abstractmethod
from typing import Any


class BaseDatabase(ABC):
    def __init__(self, credentials: dict[str, Any]) -> None:
        self.credentials = credentials

    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, list[str]]:
        pass

    @abstractmethod
    def execute_query(self, query: str | dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def test_connection(self) -> bool:
        try:
            self.connect()
            return True
        except Exception:
            return False
