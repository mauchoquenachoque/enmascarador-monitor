from typing import Any

import pymysql
import pymysql.cursors

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class MySQLDatabase(BaseDatabase):
    def connect(self) -> pymysql.Connection:
        return pymysql.connect(
            host=self.credentials.get("host", "localhost"),
            port=int(self.credentials.get("port", 3306)),
            user=self.credentials.get("user", "root"),
            password=self.credentials.get("password", ""),
            database=self.credentials.get("database", "mysql"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        db = self.credentials.get("database", "mysql")
        query = (
            f"SELECT table_name, column_name FROM information_schema.columns "
            f"WHERE table_schema = '{db}' ORDER BY table_name, ordinal_position"
        )
        results = self.execute_query(query)
        for row in results:
            t = row.get("table_name") or row.get("TABLE_NAME")
            c = row.get("column_name") or row.get("COLUMN_NAME")
            schema.setdefault(t, []).append(c)
        return {"tables": schema}

    def execute_query(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                if cursor.description:
                    return cursor.fetchall()
                conn.commit()
                return []
        finally:
            conn.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("mysql", MySQLDatabase)
