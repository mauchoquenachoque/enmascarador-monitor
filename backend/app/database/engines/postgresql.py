from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class PostgreSQLDatabase(BaseDatabase):
    def connect(self) -> Any:
        return psycopg2.connect(
            host=self.credentials.get("host", "localhost"),
            port=int(self.credentials.get("port", 5432)),
            user=self.credentials.get("user", "postgres"),
            password=self.credentials.get("password", ""),
            dbname=self.credentials.get("database", "postgres"),
            cursor_factory=RealDictCursor,
            connect_timeout=10,
        )

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        query = """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """
        results = self.execute_query(query)
        for row in results:
            t = row["table_name"]
            c = row["column_name"]
            schema.setdefault(t, []).append(c)
        return {"tables": schema}

    def execute_query(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                conn.commit()
                return []
        finally:
            conn.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("postgres", PostgreSQLDatabase)
DatabaseFactory.register("postgresql", PostgreSQLDatabase)
