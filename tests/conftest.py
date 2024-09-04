from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.db import db
from app.main import app

app.dependency_overrides[get_current_user] = lambda: AccessTokenData(user_id="1")


@pytest.fixture(scope="session")
def client():
    with patch.object(db, "open_conn_pool", new=AsyncMock()) as mock_open_conn_pool:
        with patch.object(db, "close_pool", new=AsyncMock()) as mock_close_pool:
            with TestClient(app) as client:
                yield client


@pytest.fixture
def db_select_many():
    with patch.object(db, "select_many", new_callable=AsyncMock) as mock_select_many:
        yield mock_select_many
