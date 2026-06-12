from typing import Any

from pymongo import MongoClient

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class MongoDBDatabase(BaseDatabase):
    def connect(self) -> MongoClient:
        uri = self.credentials.get("host", "mongodb://localhost:27017/")
        return MongoClient(uri, serverSelectionTimeoutMS=10000)

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        client = self.connect()
        try:
            db_name = self.credentials.get("database", "admin")
            db = client[db_name]
            for col_name in db.list_collection_names():
                doc = db[col_name].find_one()
                schema[col_name] = list(doc.keys()) if doc else []
            return {"tables": schema}
        finally:
            client.close()

    def execute_query(
        self, query: Any, collection: str = "", limit: int = 100, **kwargs: Any
    ) -> list[dict[str, Any]]:
        if not collection:
            raise ValueError("MongoDB requiere parámetro 'collection'")
        client = self.connect()
        try:
            db_name = self.credentials.get("database", "admin")
            col = client[db_name][collection]
            results = list(col.find(query if isinstance(query, dict) else {}).limit(limit))
            for doc in results:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            return results
        finally:
            client.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("mongodb", MongoDBDatabase)
DatabaseFactory.register("mongo", MongoDBDatabase)
