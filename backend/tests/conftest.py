import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import get_db
from app.main import application as fastapi_app
from app.models.base import Base

import app.database.engines.sqlite  # noqa: F401 - register sqlite engine
import app.database.engines.postgresql  # noqa: F401
import app.database.engines.mysql  # noqa: F401
import app.database.engines.sqlserver  # noqa: F401
import app.database.engines.mongodb  # noqa: F401
import app.database.engines.redis_db  # noqa: F401
import app.database.engines.neo4j  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    import app.core.dependencies as dep_module

    original_session_local = dep_module.SessionLocal
    dep_module.SessionLocal = TestingSessionLocal
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        dep_module.SessionLocal = original_session_local
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    from app.core.security import hash_password
    from app.models.user import User

    db = TestingSessionLocal()
    admin = User(
        username="testadmin",
        email="testadmin@test.com",
        hashed_password=hash_password("Test1234!"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "Test1234!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def analyst_token(client):
    from app.core.security import hash_password
    from app.models.user import User

    db = TestingSessionLocal()
    analyst = User(
        username="testanalyst",
        email="testanalyst@test.com",
        hashed_password=hash_password("Test1234!"),
        role="analyst",
    )
    db.add(analyst)
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/auth/login",
        json={"username": "testanalyst", "password": "Test1234!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def viewer_token(client):
    from app.core.security import hash_password
    from app.models.user import User

    db = TestingSessionLocal()
    viewer = User(
        username="testviewer",
        email="testviewer@test.com",
        hashed_password=hash_password("Test1234!"),
        role="viewer",
    )
    db.add(viewer)
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/auth/login",
        json={"username": "testviewer", "password": "Test1234!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]
