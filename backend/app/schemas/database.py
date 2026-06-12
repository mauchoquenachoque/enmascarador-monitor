from typing import Any, Optional

from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    engine: str = Field(
        ...,
        pattern="^(postgres|mysql|sqlserver|sqlite|mongodb|redis|neo4j)$",
    )
    alias: str = Field(..., min_length=1, max_length=100)
    credentials: dict[str, Any]


class ConnectionResponse(BaseModel):
    id: str
    alias: str
    engine: str
    is_active: str

    model_config = {"from_attributes": True}


class ConnectionTestRequest(BaseModel):
    engine: str
    credentials: dict[str, Any]


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    schema: Optional[dict[str, Any]] = None


class SchemaResponse(BaseModel):
    tables: dict[str, list[str]]
