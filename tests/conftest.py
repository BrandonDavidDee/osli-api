# type: ignore
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def auth_headers(client):
    response = client.post(
        "/api/authentication/login",
        json={"username": "", "password": ""}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def authenticated_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client
