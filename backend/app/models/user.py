import uuid

from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        Enum("admin", "analyst", "viewer", name="user_role"),
        nullable=False,
        default="viewer",
    )
    is_active = Column(Boolean, default=True, nullable=False)

    audit_logs = relationship("AuditLog", back_populates="user")
    query_history = relationship("QueryHistory", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username} role={self.role}>"
