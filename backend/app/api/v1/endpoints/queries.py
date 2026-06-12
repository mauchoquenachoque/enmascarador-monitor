from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_analyst
from app.core.dependencies import get_db
from app.database.factory import DatabaseFactory
from app.masking.factory import MaskingFactory
from app.metrics.collector import collector
from app.models.query_history import QueryHistory
from app.repositories.user_repository import UserRepository
from app.schemas.query import QueryHistoryResponse, QueryRunRequest, QueryRunResponse

router = APIRouter(prefix="/queries", tags=["Consultas"])


@router.post("/run", response_model=QueryRunResponse)
def run_query(
    data: QueryRunRequest,
    current_user: dict = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> QueryRunResponse:
    from app.repositories.connection_repository import ConnectionRepository

    conn_repo = ConnectionRepository(db)
    conn = conn_repo.get_by_id(data.connection_id)
    if not conn:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conexión")

    engine = DatabaseFactory.create(conn.engine, conn.credentials)

    query = data.query
    kwargs: dict[str, Any] = {}

    if not query:
        if conn.engine in ("postgres", "mysql", "sqlserver", "sqlite"):
            if data.table:
                query = (
                    f"SELECT TOP {data.limit} * FROM {data.table}"
                    if conn.engine == "sqlserver"
                    else f"SELECT * FROM {data.table} LIMIT {data.limit}"
                )
        elif conn.engine in ("mongodb", "mongo"):
            kwargs["collection"] = data.table or ""
            query = {}
        elif conn.engine == "neo4j":
            query = f"MATCH (n:{data.table or ''}) RETURN n LIMIT {data.limit}"
        elif conn.engine == "redis":
            query = data.table or "*"
            kwargs["command_type"] = "keys"

    def db_func() -> list[dict[str, Any]]:
        return engine.execute_query(query, **kwargs)

    masking_func = None
    if data.masking_rules:

        def masking_func(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
            masked, _ = MaskingFactory.apply_masking(raw, data.masking_rules)
            return masked

    result = collector.measure_query(
        db_func=db_func,
        masking_func=masking_func,
        engine=conn.engine,
        algorithm=",".join(data.masking_rules.values()) if data.masking_rules else "none",
    )

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(current_user["username"])
    if user:
        qh = QueryHistory(
            user_id=user.id,
            connection_id=data.connection_id,
            engine=conn.engine,
            query=str(query),
            masking_algorithm=",".join(data.masking_rules.keys()) if data.masking_rules else None,
            rows_returned=result.rows_processed,
            db_latency_ms=result.db_latency_ms,
            masking_latency_ms=result.masking_latency_ms,
            total_latency_ms=result.total_latency_ms,
            overhead_percent=result.overhead_percent,
        )
        db.add(qh)
        db.commit()

    return QueryRunResponse(
        engine=conn.engine,
        db_latency_ms=result.db_latency_ms,
        masking_latency_ms=result.masking_latency_ms,
        total_latency_ms=result.total_latency_ms,
        overhead_percent=result.overhead_percent,
        rows_returned=result.rows_processed,
        data=collector.get_history()[-1:],
        masking_applied=bool(data.masking_rules),
    )


@router.get("/history")
def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    from app.repositories.query_history_repository import QueryHistoryRepository

    repo = QueryHistoryRepository(db)
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(current_user["username"])

    if current_user["role"] == "admin":
        records = repo.get_all(limit=limit)
    elif user:
        records = repo.get_by_user(user.id, limit=limit)
    else:
        records = []

    return [
        {
            "id": r.id,
            "engine": r.engine,
            "query": r.query,
            "masking_algorithm": r.masking_algorithm,
            "rows_returned": r.rows_returned,
            "db_latency_ms": r.db_latency_ms,
            "masking_latency_ms": r.masking_latency_ms,
            "total_latency_ms": r.total_latency_ms,
            "overhead_percent": r.overhead_percent,
            "created_at": str(r.created_at),
        }
        for r in records
    ]
