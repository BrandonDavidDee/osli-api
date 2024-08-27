import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import db
from app.authentication.token import get_current_user
from app.authentication.models import AccessTokenData
from unittest.mock import patch, AsyncMock

app.dependency_overrides[get_current_user] = lambda: AccessTokenData(user_id="1")


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db_select_many():
    with patch.object(db, 'select_many', new_callable=AsyncMock) as mock_select_many:
        yield mock_select_many
