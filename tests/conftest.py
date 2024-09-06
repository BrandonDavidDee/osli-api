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
def mock_db_select_many():
    # this replaces patch.object: patch.object(db, "select_many", new_callable=AsyncMock)
    # that did not work when called from deeply nested controllers
    with patch("app.db.Database.select_many") as mock_select_many:
        yield mock_select_many


@pytest.fixture
def mock_db_select_one():
    with patch("app.db.Database.select_one") as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_insert():
    with patch("app.db.Database.insert") as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_delete_one():
    with patch("app.db.Database.delete_one") as mock_func:
        yield mock_func
