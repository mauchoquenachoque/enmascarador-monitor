from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_viewer
from app.core.dependencies import get_db
from app.metrics.collector import collector
from app.models.benchmark_result import BenchmarkResult
from app.models.connection import Connection
from app.models.query_history import QueryHistory
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    _: dict = Depends(require_viewer),
    db: Session = Depends(get_db),
) -> DashboardStats:
    total_queries = db.query(func.count(QueryHistory.id)).scalar() or 0
    total_benchmarks = db.query(func.count(BenchmarkResult.id)).scalar() or 0
    total_connections = db.query(func.count(Connection.id)).scalar() or 0

    avg_db = db.query(func.avg(QueryHistory.db_latency_ms)).scalar() or 0
    avg_mask = db.query(func.avg(QueryHistory.masking_latency_ms)).scalar() or 0
    avg_overhead = db.query(func.avg(QueryHistory.overhead_percent)).scalar() or 0

    live = collector.get_summary()

    top_engine_row = (
        db.query(QueryHistory.engine, func.count(QueryHistory.id).label("cnt"))
        .group_by(QueryHistory.engine)
        .order_by(func.count(QueryHistory.id).desc())
        .first()
    )
    top_engine = top_engine_row[0] if top_engine_row else "N/A"

    top_algo_row = (
        db.query(
            QueryHistory.masking_algorithm,
            func.count(QueryHistory.id).label("cnt"),
        )
        .filter(QueryHistory.masking_algorithm.isnot(None))
        .group_by(QueryHistory.masking_algorithm)
        .order_by(func.count(QueryHistory.id).desc())
        .first()
    )
    top_algorithm = top_algo_row[0] if top_algo_row else "N/A"

    recent = (
        db.query(QueryHistory)
        .order_by(QueryHistory.created_at.desc())
        .limit(10)
        .all()
    )
    recent_activity = [
        {
            "id": r.id,
            "engine": r.engine,
            "total_latency_ms": r.total_latency_ms,
            "overhead_percent": r.overhead_percent,
            "created_at": str(r.created_at),
        }
        for r in recent
    ]

    return DashboardStats(
        total_queries=total_queries,
        total_benchmarks=total_benchmarks,
        total_connections=total_connections,
        avg_db_latency_ms=round(float(avg_db), 3),
        avg_masking_latency_ms=round(float(avg_mask), 3),
        avg_overhead_percent=round(float(avg_overhead), 2),
        avg_cpu_percent=live.get("avg_cpu_percent", 0),
        avg_ram_mb=live.get("avg_ram_mb", 0),
        top_engine=top_engine,
        top_algorithm=top_algorithm,
        recent_activity=recent_activity,
    )
