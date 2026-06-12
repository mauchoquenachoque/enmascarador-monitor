from typing import Any

import pymssql

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class SQLServerDatabase(BaseDatabase):
    def connect(self) -> pymssql.Connection:
        return pymssql.connect(
            server=self.credentials.get("host", "localhost"),
            port=str(self.credentials.get("port", 1433)),
            user=self.credentials.get("user", "sa"),
            password=self.credentials.get("password", ""),
            database=self.credentials.get("database", "master"),
            as_dict=True,
            login_timeout=10,
        )

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        query = "SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS ORDER BY TABLE_NAME, ORDINAL_POSITION"
        results = self.execute_query(query)
        for row in results:
            t = row["TABLE_NAME"]
            c = row["COLUMN_NAME"]
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


DatabaseFactory.register("sqlserver", SQLServerDatabase)
DatabaseFactory.register("mssql", SQLServerDatabase)
