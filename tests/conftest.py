import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

os.environ["AUTH_SECRET"] = "test-secret-key-for-testing-only"

from api.service import create_app
from core.database import get_session


@pytest.fixture
def db_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def client(db_url: str):
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    app = create_app()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    engine.dispose()


@pytest.fixture
def auth_token(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "user@example.com",
        "password": "SecurePass123!",
        "nickname": "原始昵称",
    })
    return response.json()["access_token"]
