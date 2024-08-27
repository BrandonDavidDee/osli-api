import pytest
from unittest.mock import patch, AsyncMock
from app.authentication.controller import AuthControllerBase
from app.users.models import UserInDB, User

HASHED_PASSWORD = "$2b$12$OjH9jIdb5qpptt/GiWWk0O/hHRmVcopmiciccbPePjBTbhaJLG5Gm"
PLAIN_PASSWORD = "mypassword"
WRONG_PASSWORD = "incorrect-password"

USER = UserInDB(
    id=1,
    is_active=True,
    hashed_password=HASHED_PASSWORD,
    username=""
)


@pytest.fixture
def mock_get_user_in_db():
    with patch.object(AuthControllerBase, 'get_user_in_db', new_callable=AsyncMock) as mock_get_user_in_db:
        yield mock_get_user_in_db


@pytest.fixture
def mock_create_token_pair():
    with patch.object(AuthControllerBase, 'create_token_pair') as mock_create_token_pair:
        yield mock_create_token_pair


class TestLogin:
    def test_login_active_user(self, client, mock_get_user_in_db, mock_create_token_pair):
        mock_get_user_in_db.return_value = USER
        output_user = USER.model_dump(exclude={"hashed_password"})
        mock_create_token_pair.return_value = {
            "access_token": "<AccessToken>",
            "refresh_token": "<RefreshToken>",
            "user": output_user,
        }
        payload = {"username": "", "password": PLAIN_PASSWORD}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 200
        assert response.json() == {
            "access_token": "<AccessToken>",
            "refresh_token": "<RefreshToken>",
            "user": output_user,
        }

    def test_login_incorrect_password(self, client, mock_get_user_in_db):
        mock_get_user_in_db.return_value = USER
        payload = {"username": "", "password": WRONG_PASSWORD}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 400

    def test_login_inactive_user(self, client, mock_get_user_in_db):
        USER.is_active = False
        mock_get_user_in_db.return_value = USER
        payload = {"username": "", "password": PLAIN_PASSWORD}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 401


class TestRefreshToken:
    @staticmethod
    def get_access_token(client):
        payload = {"username": "", "password": PLAIN_PASSWORD}
        response = client.post("/api/authentication/login", json=payload)
        data = response.json()
        refresh_token = data["refresh_token"]
        return refresh_token

    def test_refresh_token(self, client, mock_get_user_in_db):
        USER.is_active = True
        mock_get_user_in_db.return_value = USER
        refresh_token = self.get_access_token(client)
        headers = {"Authorization": "Bearer " + refresh_token}
        response = client.post("/api/authentication/refresh-tokens", headers=headers)
        assert response.status_code == 200
