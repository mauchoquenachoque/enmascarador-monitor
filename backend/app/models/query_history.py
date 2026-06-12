import uuid

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class QueryHistory(Base, TimestampMixin):
    __tablename__ = "query_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    connection_id = Column(String(36), nullable=False)
    engine = Column(String(50), nullable=False)
    query = Column(Text, nullable=False)
    masking_algorithm = Column(String(50), nullable=True)
    rows_returned = Column(Integer, default=0)
    db_latency_ms = Column(Float, default=0.0)
    masking_latency_ms = Column(Float, default=0.0)
    total_latency_ms = Column(Float, default=0.0)
    overhead_percent = Column(Float, default=0.0)

    user = relationship("User", back_populates="query_history")

    def __repr__(self) -> str:
        return f"<QueryHistory engine={self.engine} latency={self.total_latency_ms}ms>"
