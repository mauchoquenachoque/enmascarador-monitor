import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.dependencies import SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.connection import Connection
from app.core.dependencies import engine
from app.core.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    email="admin@masking-monitor.local",
                    hashed_password=hash_password("Admin123!"),
                    role="admin",
                )
            )
            print("[SEED] Admin user created: admin / Admin123!")

        if not db.query(User).filter(User.username == "analyst").first():
            db.add(
                User(
                    username="analyst",
                    email="analyst@masking-monitor.local",
                    hashed_password=hash_password("Analyst123!"),
                    role="analyst",
                )
            )
            print("[SEED] Analyst user created: analyst / Analyst123!")

        if not db.query(User).filter(User.username == "viewer").first():
            db.add(
                User(
                    username="viewer",
                    email="viewer@masking-monitor.local",
                    hashed_password=hash_password("Viewer123!"),
                    role="viewer",
                )
            )
            print("[SEED] Viewer user created: viewer / Viewer123!")

        if not db.query(Connection).first():
            demo_connections = [
                Connection(
                    alias="SQLite Demo",
                    engine="sqlite",
                    credentials={"database": "local_monitor.db"},
                ),
                Connection(
                    alias="PostgreSQL Local",
                    engine="postgres",
                    credentials={
                        "host": "localhost",
                        "port": 5432,
                        "user": "postgres",
                        "password": "postgres",
                        "database": "postgres",
                    },
                ),
            ]
            for conn in demo_connections:
                db.add(conn)
            print(f"[SEED] {len(demo_connections)} demo connections created")

        db.commit()
        print("[SEED] Database seeded successfully!")

    except Exception as e:
        print(f"[SEED] Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
