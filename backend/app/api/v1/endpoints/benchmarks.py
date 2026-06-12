import time
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_analyst
from app.core.dependencies import get_db
from app.database.factory import DatabaseFactory
from app.masking.factory import MaskingFactory
from app.metrics.benchmark import BenchmarkEngine
from app.metrics.collector import collector
from app.models.benchmark_result import BenchmarkResult
from app.repositories.benchmark_repository import BenchmarkRepository
from app.repositories.connection_repository import ConnectionRepository
from app.schemas.benchmark import BenchmarkRequest, BenchmarkResponse

router = APIRouter(prefix="/benchmarks", tags=["Benchmark"])


@router.post("/run", response_model=BenchmarkResponse)
def run_benchmark(
    data: BenchmarkRequest,
    current_user: dict = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> BenchmarkResponse:
    conn_repo = ConnectionRepository(db)
    conn = conn_repo.get_by_id(data.connection_id)
    if not conn:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Conexión")

    engine = DatabaseFactory.create(conn.engine, conn.credentials)
    bench_engine = BenchmarkEngine(collector)

    query = data.query
    kwargs: dict[str, Any] = {}
    if not query:
        if conn.engine in ("postgres", "mysql", "sqlserver", "sqlite"):
            query = (
                f"SELECT TOP 100 * FROM {data.table}"
                if conn.engine == "sqlserver"
                else f"SELECT * FROM {data.table} LIMIT 100"
            )
        elif conn.engine in ("mongodb", "mongo"):
            kwargs["collection"] = data.table
            query = {}
        elif conn.engine == "neo4j":
            query = f"MATCH (n:{data.table}) RETURN n LIMIT 100"
        elif conn.engine == "redis":
            query = data.table
            kwargs["command_type"] = "keys"

    def db_func() -> list[dict[str, Any]]:
        return engine.execute_query(query, **kwargs)

    all_results = []
    all_summaries = []
    total_start = time.perf_counter_ns()

    for algorithm in data.algorithms:

        def masking_func(raw: list[dict[str, Any]], alg=algorithm) -> list[dict[str, Any]]:
            masked, _ = MaskingFactory.apply_masking(raw, {data.table: alg})
            return masked

        result = bench_engine.run_benchmark(
            db_func=db_func,
            masking_func=masking_func,
            engine=conn.engine,
            algorithm=algorithm,
            iterations=data.iterations,
        )

        all_summaries.append(result["summary"])
        for item in result["individual"]:
            item["algorithm"] = algorithm
            all_results.append(item)

        bench_repo = BenchmarkRepository(db)
        bench_repo.create(
            BenchmarkResult(
                engine=conn.engine,
                algorithm=algorithm,
                iterations=data.iterations,
                avg_db_latency_ms=result["summary"]["avg_db_latency_ms"],
                avg_masking_latency_ms=result["summary"]["avg_masking_latency_ms"],
                avg_total_latency_ms=result["summary"]["avg_total_latency_ms"],
                avg_overhead_percent=result["summary"]["avg_overhead_percent"],
                avg_cpu_percent=result["summary"]["avg_cpu_percent"],
                avg_ram_mb=result["summary"]["avg_ram_mb"],
                throughput_qps=result["summary"]["throughput_qps"],
                p50_ms=result["summary"]["p50_ms"],
                p95_ms=result["summary"]["p95_ms"],
                p99_ms=result["summary"]["p99_ms"],
            )
        )

    total_duration = (time.perf_counter_ns() - total_start) / 1_000_000

    return BenchmarkResponse(
        results=all_results,
        summary=all_summaries,
        total_duration_ms=round(total_duration, 3),
    )


@router.get("/history")
def get_benchmark_history(
    limit: int = 50,
    _: dict = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> list[dict]:
    repo = BenchmarkRepository(db)
    results = repo.get_all(limit=limit)
    return [
        {
            "id": r.id,
            "engine": r.engine,
            "algorithm": r.algorithm,
            "iterations": r.iterations,
            "avg_db_latency_ms": r.avg_db_latency_ms,
            "avg_masking_latency_ms": r.avg_masking_latency_ms,
            "avg_total_latency_ms": r.avg_total_latency_ms,
            "avg_overhead_percent": r.avg_overhead_percent,
            "throughput_qps": r.throughput_qps,
            "p50_ms": r.p50_ms,
            "p95_ms": r.p95_ms,
            "p99_ms": r.p99_ms,
            "created_at": str(r.created_at),
        }
        for r in results
    ]
