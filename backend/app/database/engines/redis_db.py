import json
from typing import Any

import redis

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class RedisDatabase(BaseDatabase):
    def connect(self) -> redis.Redis:
        return redis.Redis(
            host=self.credentials.get("host", "localhost"),
            port=int(self.credentials.get("port", 6379)),
            db=int(self.credentials.get("database", 0)),
            password=self.credentials.get("password") or None,
            decode_responses=True,
            socket_connect_timeout=10,
        )

    def get_schema(self) -> dict[str, list[str]]:
        client = self.connect()
        try:
            sample_keys = client.keys("*")[:10]
            schema: dict[str, list[str]] = {"redis_keys": ["value"]}
            if sample_keys:
                val = client.get(sample_keys[0])
                try:
                    obj = json.loads(val)
                    if isinstance(obj, dict):
                        schema["redis_keys"] = list(obj.keys())
                except (json.JSONDecodeError, TypeError):
                    pass
            return {"tables": schema}
        finally:
            client.close()

    def execute_query(
        self, query: str, command_type: str = "get", **kwargs: Any
    ) -> list[dict[str, Any]]:
        client = self.connect()
        try:
            if command_type.lower() == "get":
                value = client.get(query)
                try:
                    parsed = json.loads(value) if value else None
                    if isinstance(parsed, dict):
                        return [parsed]
                except (json.JSONDecodeError, TypeError):
                    parsed = value
                return [{"key": query, "value": parsed}]
            elif command_type.lower() == "hgetall":
                return [client.hgetall(query)]
            elif command_type.lower() == "keys":
                keys = client.keys(query or "*")
                return [{"key": k} for k in keys[:100]]
            return []
        finally:
            client.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("redis", RedisDatabase)
