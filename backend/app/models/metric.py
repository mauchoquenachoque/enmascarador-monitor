import uuid

from sqlalchemy import Column, Float, String

from app.models.base import Base, TimestampMixin


class Metric(Base, TimestampMixin):
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_type = Column(String(50), nullable=False, index=True)
    engine = Column(String(50), nullable=True)
    algorithm = Column(String(50), nullable=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="ms")

    def __repr__(self) -> str:
        return f"<Metric {self.metric_type}={self.value}{self.unit}>"
