from typing import Any, Optional

from pydantic import BaseModel, Field


class BenchmarkRequest(BaseModel):
    connection_id: str
    table: str
    algorithms: list[str] = Field(
        default=["redaccion", "hashing", "encriptacion", "fpe"],
    )
    iterations: int = Field(default=10, ge=1, le=1000)
    query: Optional[str] = None


class BenchmarkResultItem(BaseModel):
    algorithm: str
    iteration: int
    db_latency_ms: float
    masking_latency_ms: float
    total_latency_ms: float
    overhead_percent: float
    cpu_percent: float
    ram_mb: float


class BenchmarkSummary(BaseModel):
    engine: str
    algorithm: str
    iterations: int
    avg_db_latency_ms: float
    avg_masking_latency_ms: float
    avg_total_latency_ms: float
    avg_overhead_percent: float
    avg_cpu_percent: float
    avg_ram_mb: float
    throughput_qps: float
    p50_ms: float
    p95_ms: float
    p99_ms: float


class BenchmarkResponse(BaseModel):
    results: list[BenchmarkResultItem]
    summary: list[BenchmarkSummary]
    total_duration_ms: float
