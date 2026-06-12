from typing import Any, Optional

from pydantic import BaseModel, Field


class QueryRunRequest(BaseModel):
    connection_id: str
    query: Optional[str] = None
    table: Optional[str] = None
    masking_rules: dict[str, str] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=10000)


class QueryRunResponse(BaseModel):
    engine: str
    db_latency_ms: float
    masking_latency_ms: float
    total_latency_ms: float
    overhead_percent: float
    rows_returned: int
    data: list[dict[str, Any]]
    masking_applied: bool


class QueryHistoryResponse(BaseModel):
    id: str
    connection_id: str
    engine: str
    query: str
    masking_algorithm: Optional[str]
    rows_returned: int
    db_latency_ms: float
    masking_latency_ms: float
    total_latency_ms: float
    overhead_percent: float
    created_at: Any

    model_config = {"from_attributes": True}
