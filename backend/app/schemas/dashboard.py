from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_queries: int
    total_benchmarks: int
    total_connections: int
    avg_db_latency_ms: float
    avg_masking_latency_ms: float
    avg_overhead_percent: float
    avg_cpu_percent: float
    avg_ram_mb: float
    top_engine: str
    top_algorithm: str
    recent_activity: list[dict]
