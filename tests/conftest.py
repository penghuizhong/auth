import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

os.environ["AUTH_SECRET"] = "test-secret-key-for-testing-only"

from src.main import app
from src.core.database import get_session

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def auth_token():
    client = TestClient(app)
    response = client.post("/api/v1/auth/register", json={
        "email": "user@example.com",
        "password": "SecurePass123!",
        "nickname": "原始昵称",
    })
    return response.json()["access_token"]
