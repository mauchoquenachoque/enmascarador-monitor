from typing import Any

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_analyst
from app.database.factory import DatabaseFactory
from app.schemas.database import (
    ConnectionTestRequest,
    ConnectionTestResponse,
    SchemaResponse,
)

router = APIRouter(prefix="/databases", tags=["Bases de Datos"])


@router.get("/engines")
def list_engines() -> dict:
    return {
        "engines": DatabaseFactory.available_engines(),
        "supported": [
            {"name": "PostgreSQL", "key": "postgres", "type": "SQL"},
            {"name": "MySQL", "key": "mysql", "type": "SQL"},
            {"name": "SQL Server", "key": "sqlserver", "type": "SQL"},
            {"name": "SQLite", "key": "sqlite", "type": "SQL"},
            {"name": "MongoDB", "key": "mongodb", "type": "NoSQL"},
            {"name": "Redis", "key": "redis", "type": "NoSQL"},
            {"name": "Neo4j", "key": "neo4j", "type": "NoSQL"},
        ],
    }


@router.post("/test", response_model=ConnectionTestResponse)
def test_connection(
    data: ConnectionTestRequest,
    _: dict = Depends(require_analyst),
) -> ConnectionTestResponse:
    try:
        engine = DatabaseFactory.create(data.engine, data.credentials)
        connected = engine.test_connection()
        if connected:
            schema = engine.get_schema()
            return ConnectionTestResponse(
                success=True,
                message=f"Conexión exitosa a {data.engine}",
                schema=schema,
            )
        return ConnectionTestResponse(
            success=False,
            message=f"No se pudo conectar a {data.engine}",
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Error: {e!s}",
        )


@router.post("/schema")
def get_schema(
    data: ConnectionTestRequest,
    _: dict = Depends(require_analyst),
) -> SchemaResponse:
    engine = DatabaseFactory.create(data.engine, data.credentials)
    schema = engine.get_schema()
    return SchemaResponse(tables=schema.get("tables", {}))


@router.post("/execute")
def execute_query(
    data: dict[str, Any],
    _: dict = Depends(require_analyst),
) -> dict:
    engine_name = data.get("engine", "")
    credentials = data.get("credentials", {})
    query = data.get("query", "")
    kwargs = data.get("kwargs", {})

    engine = DatabaseFactory.create(engine_name, credentials)
    results = engine.execute_query(query, **kwargs)
    return {"rows": len(results), "data": results}
