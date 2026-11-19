"""
Shared pytest fixtures for the Online Quiz System test suite.
Configures isolated temporary SQLite databases for each test execution.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.database import get_db, init_db
from backend.main import app


@pytest.fixture
def client(tmp_path):
    """Provides a TestClient using an isolated temporary SQLite database."""
    test_db_file = tmp_path / "test_app.db"
    test_engine = create_engine(
        f"sqlite:///{test_db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    init_db(test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    """Provides an authenticated TestClient with active session cookies."""
    # Register instructor
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "name": "Prof. Test Instructor",
            "email": "instructor@example.edu",
            "password": "securepassword123",
        },
    )
    assert reg_resp.status_code == 201

    # Login to acquire session cookie
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "instructor@example.edu", "password": "securepassword123"},
    )
    assert login_resp.status_code == 200
    return client
