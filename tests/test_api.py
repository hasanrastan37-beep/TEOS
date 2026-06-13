from fastapi.testclient import TestClient
from src.api.rest import app

client = TestClient(app)

def test_health():
    response = client.get("/docs")
    assert response.status_code == 200

def test_login_invalid():
    resp = client.post("/auth/login", json={"username": "wrong", "password": "wrong"})
    assert resp.status_code == 401
