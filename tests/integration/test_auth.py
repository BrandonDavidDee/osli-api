from unittest.mock import AsyncMock, patch

import pytest

from app.authentication.controller import AuthControllerBase
from app.users.models import UserInDB

hashed_password = "$2b$12$OjH9jIdb5qpptt/GiWWk0O/hHRmVcopmiciccbPePjBTbhaJLG5Gm"
plain_password = "mypassword"
wrong_password = "incorrect-password"

user = UserInDB(id=1, is_active=True, hashed_password=hashed_password, username="")


@pytest.fixture
def mock_get_user_in_db():
    with patch.object(
        AuthControllerBase, "get_user_in_db", new_callable=AsyncMock
    ) as mock_get_user_in_db:
        yield mock_get_user_in_db


@pytest.fixture
def mock_create_token_pair():
    with patch.object(
        AuthControllerBase, "create_token_pair"
    ) as mock_create_token_pair:
        yield mock_create_token_pair


class TestLogin:
    def test_login_active_user(
        self, client, mock_get_user_in_db, mock_create_token_pair
    ):
        mock_get_user_in_db.return_value = user
        output_user = user.model_dump(exclude={"hashed_password"})
        mock_create_token_pair.return_value = {
            "access_token": "<AccessToken>",
            "refresh_token": "<RefreshToken>",
            "user": output_user,
        }
        payload = {"username": "", "password": plain_password}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 200
        assert response.json() == {
            "access_token": "<AccessToken>",
            "refresh_token": "<RefreshToken>",
            "user": output_user,
        }

    def test_login_incorrect_password(self, client, mock_get_user_in_db):
        mock_get_user_in_db.return_value = user
        payload = {"username": "", "password": wrong_password}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 400

    def test_login_inactive_user(self, client, mock_get_user_in_db):
        user.is_active = False
        mock_get_user_in_db.return_value = user
        payload = {"username": "", "password": plain_password}
        response = client.post("/api/authentication/login", json=payload)
        assert response.status_code == 401


class TestRefreshToken:
    def test_refresh_token(self, client, mock_get_user_in_db):
        user.is_active = True
        mock_get_user_in_db.return_value = user
        refresh_token = self._get_access_token(client)
        headers = {"Authorization": "Bearer " + refresh_token}
        response = client.post("/api/authentication/refresh-tokens", headers=headers)
        assert response.status_code == 200

    def test_refresh_token_not_present(self, client, mock_get_user_in_db):
        headers = {"Authorization": "Bearer "}
        response = client.post("/api/authentication/refresh-tokens", headers=headers)
        assert response.status_code == 401
        response = client.post("/api/authentication/refresh-tokens")
        assert response.status_code == 401

    @staticmethod
    def _get_access_token(client):
        payload = {"username": "", "password": plain_password}
        response = client.post("/api/authentication/login", json=payload)
        data = response.json()
        refresh_token = data["refresh_token"]
        return refresh_token


class TestPermissions:
    def test_get_permissions(self, client):
        response = client.get("/api/authentication/permissions")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_permission_groups(self, client):
        response = client.get("/api/authentication/permission-groups")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
