from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: str = "",
        ip_address: str = "",
        overhead_percent: float | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            overhead_percent=overhead_percent,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 200) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
