import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.core.database import get_session
from src.main import app

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
def auth_token(setup_db):
    client = TestClient(app)
    response = client.post("/api/v1/auth/register", json={
        "email": "chat@example.com",
        "password": "SecurePass123!",
    })
    return response.json()["access_token"]


def test_create_session(auth_token):
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "thread_id" in data


def test_list_sessions(auth_token):
    client = TestClient(app)
    client.post("/api/v1/chat/sessions", headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/api/v1/chat/sessions", headers={"Authorization": f"Bearer {auth_token}"})
    response = client.get(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_session(auth_token):
    client = TestClient(app)
    create_resp = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    thread_id = create_resp.json()["thread_id"]
    response = client.patch(
        f"/api/v1/chat/sessions/{thread_id}",
        json={"title": "新标题"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "新标题"


def test_delete_session(auth_token):
    client = TestClient(app)
    create_resp = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    thread_id = create_resp.json()["thread_id"]
    response = client.delete(
        f"/api/v1/chat/sessions/{thread_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200

    list_resp = client.get(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert len(list_resp.json()) == 0
