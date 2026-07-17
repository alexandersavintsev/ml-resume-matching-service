from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

TEST_EMAIL = "pytest_history@example.com"


def get_token():
    client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "role": "employer", "initial_credits": 0}
    )

    r = client.post("/auth/login", json={"email": TEST_EMAIL})
    token = r.json()["token"]

    client.post(
        "/balance/top-up",
        json={"amount": 50},
        headers={"Authorization": f"Bearer {token}"}
    )

    return token


def test_transactions_history():
    token = get_token()

    response = client.get(
        "/history/transactions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_predictions_history():
    token = get_token()

    response = client.get(
        "/history/predictions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
  
