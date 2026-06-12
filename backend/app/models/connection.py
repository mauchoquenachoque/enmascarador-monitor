import uuid

from sqlalchemy import Column, JSON, String

from app.models.base import Base, TimestampMixin


class Connection(Base, TimestampMixin):
    __tablename__ = "connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alias = Column(String(100), nullable=False)
    engine = Column(String(50), nullable=False)
    credentials = Column(JSON, nullable=False)
    is_active = Column(String(1), default="1")

    def __repr__(self) -> str:
        return f"<Connection {self.alias} engine={self.engine}>"
