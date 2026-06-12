from typing import Any, Optional

from pydantic import BaseModel


class MetricPoint(BaseModel):
    timestamp: str
    value: float
    unit: str


class MetricSummary(BaseModel):
    metric_type: str
    engine: Optional[str] = None
    algorithm: Optional[str] = None
    count: int
    avg: float
    min_val: float
    max_val: float
    unit: str


class LiveMetrics(BaseModel):
    cpu_percent: float
    ram_mb: float
    ram_percent: float
    active_connections: int
    total_queries: int


class MetricsExport(BaseModel):
    format: str
    data: list[dict[str, Any]]
