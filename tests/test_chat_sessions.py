import pytest
from fastapi.testclient import TestClient


def test_create_session(client: TestClient, auth_token: str):
    response = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "thread_id" in data


def test_list_sessions(client: TestClient, auth_token: str):
    client.post("/api/v1/chat/sessions", headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/api/v1/chat/sessions", headers={"Authorization": f"Bearer {auth_token}"})
    response = client.get(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_session(client: TestClient, auth_token: str):
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


def test_update_session_clear_title(client: TestClient, auth_token: str):
    create_resp = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    thread_id = create_resp.json()["thread_id"]
    response = client.patch(
        f"/api/v1/chat/sessions/{thread_id}",
        json={"title": None},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] is None


def test_delete_session(client: TestClient, auth_token: str):
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


def test_list_sessions_no_token(client: TestClient):
    response = client.get("/api/v1/chat/sessions")
    assert response.status_code == 401
