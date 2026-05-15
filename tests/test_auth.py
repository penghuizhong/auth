import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from src.main import create_app
from src.core.database import get_session
import src.main as main_module

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def override_get_session():
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(monkeypatch):
    def mock_create_db_and_tables():
        SQLModel.metadata.create_all(engine)

    monkeypatch.setattr(main_module, "create_db_and_tables", mock_create_db_and_tables)

    SQLModel.metadata.create_all(engine)

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client

    SQLModel.metadata.drop_all(engine)


def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "nickname": "测试用户",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "SecurePass123!",
    })
    response = client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "AnotherPass123!",
    })
    assert response.status_code == 409


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "SecurePass123!",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "SecurePass123!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "SecurePass123!",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "WrongPass123!",
    })
    assert response.status_code == 401
