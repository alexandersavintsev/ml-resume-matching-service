from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

TEST_EMAIL = "pytest_predict@example.com"


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


def test_predict_success():
    token = get_token()

    response = client.post(
        "/predict",
        json={
            "keywords": ["python", "fastapi"],
            "resumes": [
                "Python developer FastAPI",
                "Java developer"
            ],
            "top_k": 1,
            "cost_credits": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "task_id" in data
    assert "top" in data


def test_predict_invalid_input():
    token = get_token()

    response = client.post(
        "/predict",
        json={
            "keywords": ["python"],
            "resumes": [" ", ""],
            "top_k": 5,
            "cost_credits": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
