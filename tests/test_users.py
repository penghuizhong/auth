import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_get_me(auth_token):
    client = TestClient(app)
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_update_me(auth_token):
    client = TestClient(app)
    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "新昵称"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["nickname"] == "新昵称"


def test_get_me_no_token():
    client = TestClient(app)
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
