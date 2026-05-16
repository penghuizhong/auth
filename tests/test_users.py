import pytest
from fastapi.testclient import TestClient


def test_get_me(client: TestClient, auth_token: str):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_update_me(client: TestClient, auth_token: str):
    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "新昵称"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["nickname"] == "新昵称"


def test_get_me_no_token(client: TestClient):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
