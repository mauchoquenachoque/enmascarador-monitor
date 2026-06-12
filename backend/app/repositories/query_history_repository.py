from sqlalchemy.orm import Session

from app.models.query_history import QueryHistory


class QueryHistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, record: QueryHistory) -> QueryHistory:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: str) -> QueryHistory | None:
        return self.db.query(QueryHistory).filter(QueryHistory.id == record_id).first()

    def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> list[QueryHistory]:
        return (
            self.db.query(QueryHistory)
            .filter(QueryHistory.user_id == user_id)
            .order_by(QueryHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[QueryHistory]:
        return (
            self.db.query(QueryHistory)
            .order_by(QueryHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_engine(self, engine: str) -> list[QueryHistory]:
        return (
            self.db.query(QueryHistory)
            .filter(QueryHistory.engine == engine)
            .order_by(QueryHistory.created_at.desc())
            .all()
        )
