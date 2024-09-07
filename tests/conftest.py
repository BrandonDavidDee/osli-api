from unittest.mock import AsyncMock, patch
import random
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.authentication.models import AccessTokenData
from app.authentication.token import get_current_user
from app.db import db
from app.main import app

app.dependency_overrides[get_current_user] = lambda: AccessTokenData(user_id="1")


def get_random_datetime():
    random_days = random.randint(0, 365)
    random_seconds = random.randint(0, 86400)
    random_datetime = datetime.now(timezone.utc) - timedelta(
        days=random_days, seconds=random_seconds
    )
    return random_datetime.isoformat()


@pytest.fixture(scope="session")
def client():
    with patch.object(db, "open_conn_pool", new=AsyncMock()) as mock_open_conn_pool:
        with patch.object(db, "close_pool", new=AsyncMock()) as mock_close_pool:
            with TestClient(app) as client:
                yield client


@pytest.fixture(scope="function")
def mock_db_select_many():
    # this replaces patch.object: patch.object(db, "select_many", new_callable=AsyncMock)
    # that did not work when called from deeply nested controllers
    with patch("app.db.Database.select_many") as mock_select_many:
        yield mock_select_many


@pytest.fixture(scope="function")
def mock_db_select_one():
    with patch("app.db.Database.select_one") as mock_func:
        yield mock_func


@pytest.fixture(scope="function")
def mock_db_insert():
    with patch("app.db.Database.insert") as mock_func:
        yield mock_func


@pytest.fixture(scope="function")
def mock_db_delete_one():
    with patch("app.db.Database.delete_one") as mock_func:
        yield mock_func
