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
def mock_db_select_one():
    with patch.object(db, "select_one", new_callable=AsyncMock) as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_select_many():
    with patch.object(db, "select_many", new_callable=AsyncMock) as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_insert():
    with patch.object(db, "insert", new_callable=AsyncMock) as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_delete_one():
    with patch.object(db, "delete_one", new_callable=AsyncMock) as mock_func:
        yield mock_func
