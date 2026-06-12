from typing import Any

from pydantic import BaseModel, Field


class MaskingApplyRequest(BaseModel):
    data: list[dict[str, Any]]
    rules: dict[str, str] = Field(
        ...,
        description="Mapa de columna -> algoritmo (redaccion, hashing, encriptacion, fpe)",
    )


class MaskingApplyResponse(BaseModel):
    masked_data: list[dict[str, Any]]
    algorithm_used: list[str]
    rows_processed: int
    masking_latency_ms: float
    cpu_percent: float
    ram_mb: float


class AlgorithmInfo(BaseModel):
    name: str
    key: str
    reversible: bool
    description: str
    performance: str


class AlgorithmListResponse(BaseModel):
    algorithms: list[AlgorithmInfo]
