import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "nickname": "测试用户",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_email(client: TestClient):
    client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "SecurePass123!",
    })
    response = client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "AnotherPass123!",
    })
    assert response.status_code == 409


def test_login_success(client: TestClient):
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


def test_login_wrong_password(client: TestClient):
    client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "SecurePass123!",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "WrongPass123!",
    })
    assert response.status_code == 401


def test_register_weak_password(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "weak@example.com",
        "password": "weakpass",
    })
    assert response.status_code == 422


def test_register_no_uppercase(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "noupper@example.com",
        "password": "nouppercase1!",
    })
    assert response.status_code == 422


def test_register_no_lowercase(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "nolower@example.com",
        "password": "NOLOWERCASE1!",
    })
    assert response.status_code == 422


def test_register_no_digit(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "nodigit@example.com",
        "password": "NoDigitPassword!",
    })
    assert response.status_code == 422


def test_logout_invalidates_token(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "email": "logout@example.com",
        "password": "SecurePass123!",
        "nickname": "登出测试",
    })
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
