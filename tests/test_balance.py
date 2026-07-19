from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

TEST_EMAIL = "pytest_balance@example.com"


def get_token():
    client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "role": "employer", "initial_credits": 0}
    )

    r = client.post("/auth/login", json={"email": TEST_EMAIL})
    return r.json()["token"]


def test_get_balance():
    token = get_token()

    response = client.get(
        "/balance",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "credits" in response.json()


def test_top_up_balance():
    token = get_token()

    response = client.post(
        "/balance/top-up",
        json={"amount": 50},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "new_balance" in response.json()


def test_invalid_top_up():
    token = get_token()

    response = client.post(
        "/balance/top-up",
        json={"amount": 0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
  
