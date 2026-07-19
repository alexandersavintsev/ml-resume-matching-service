import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

TEST_EMAIL = "pytest_user@example.com"


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "role": "employer",
            "initial_credits": 0
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == TEST_EMAIL
    assert data["role"] == "employer"


def test_login_user():
    response = client.post(
        "/auth/login",
        json={"email": TEST_EMAIL}
    )

    assert response.status_code == 200
    data = response.json()

    assert "token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_user():
    response = client.post(
        "/auth/login",
        json={"email": "no_such_user@example.com"}
    )

    assert response.status_code == 404
