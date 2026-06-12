from sqlalchemy.orm import Session

from app.models.connection import Connection


class ConnectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, conn: Connection) -> Connection:
        self.db.add(conn)
        self.db.commit()
        self.db.refresh(conn)
        return conn

    def get_by_id(self, conn_id: str) -> Connection | None:
        return self.db.query(Connection).filter(Connection.id == conn_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Connection]:
        return self.db.query(Connection).offset(skip).limit(limit).all()

    def get_active(self) -> list[Connection]:
        return self.db.query(Connection).filter(Connection.is_active == "1").all()

    def update(self, conn: Connection) -> Connection:
        self.db.commit()
        self.db.refresh(conn)
        return conn

    def delete(self, conn: Connection) -> None:
        self.db.delete(conn)
        self.db.commit()
