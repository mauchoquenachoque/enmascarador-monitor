from typing import Any

from neo4j import GraphDatabase

from app.database.base import BaseDatabase
from app.database.factory import DatabaseFactory


class Neo4jDatabase(BaseDatabase):
    def connect(self) -> Any:
        return GraphDatabase.driver(
            self.credentials.get("host", "bolt://localhost:7687"),
            auth=(
                self.credentials.get("user", "neo4j"),
                self.credentials.get("password", ""),
            ),
            connection_timeout=10,
        )

    def get_schema(self) -> dict[str, list[str]]:
        driver = self.connect()
        try:
            with driver.session() as session:
                result = session.run(
                    "MATCH (n) RETURN labels(n) AS labels, keys(n) AS properties LIMIT 20"
                )
                schema: dict[str, list[str]] = {}
                for record in result:
                    labels = record["labels"]
                    props = record["properties"]
                    if labels:
                        lbl = labels[0]
                        schema[lbl] = list(set(schema.get(lbl, []) + props))
                return {"tables": schema}
        finally:
            driver.close()

    def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        driver = self.connect()
        try:
            with driver.session() as session:
                result = session.run(query, parameters=parameters or {})
                rows = []
                for record in result:
                    flat: dict[str, Any] = {}
                    for key, value in dict(record).items():
                        if hasattr(value, "items"):
                            flat.update(dict(value.items()))
                        else:
                            flat[key] = value
                    rows.append(flat)
                return rows
        finally:
            driver.close()

    def close(self) -> None:
        pass


DatabaseFactory.register("neo4j", Neo4jDatabase)
