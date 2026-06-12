import sqlite3
from typing import Any

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class SQLiteDatabase(BaseDatabase):
    def connect(self) -> sqlite3.Connection:
        db_path = self.credentials.get("database", "local_monitor.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        tables = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        for t in tables:
            t_name = t["name"]
            cols = self.execute_query(f"PRAGMA table_info('{t_name}')")
            schema[t_name] = [c["name"] for c in cols]
        return {"tables": schema}

    def execute_query(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if cursor.description:
                return [dict(row) for row in cursor.fetchall()]
            conn.commit()
            return []
        finally:
            conn.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("sqlite", SQLiteDatabase)
