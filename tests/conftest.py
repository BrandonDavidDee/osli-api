from unittest.mock import AsyncMock, patch
import random
import string
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


def get_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


@pytest.fixture(scope="session")
def dummy_user():
    return {
        "id": random.randint(1, 100),
        "username": get_random_string(10),
        "date_created": get_random_datetime(),
        "created_by_id": random.randint(0, 365),
    }


@pytest.fixture(scope="session")
def dummy_source_bucket():
    return {
        "id": random.randint(1, 100),
        "title": get_random_string(10),
        "bucket_name": get_random_string(10),
        "access_key_id": get_random_string(50),
        "secret_access_key": get_random_string(50),
        "media_prefix": get_random_string(50),
        "created_by_id": random.randint(0, 365),
        "date_created": get_random_datetime(),
    }


@pytest.fixture(scope="session")
def dummy_source_vimeo():
    return {
        "id": random.randint(1, 100),
        "title": get_random_string(10),
        "client_identifier": get_random_string(50),
        "client_secret": get_random_string(50),
        "access_token": get_random_string(50),
        "created_by_id": random.randint(0, 365),
        "date_created": get_random_datetime(),
    }


@pytest.fixture(scope="session")
def dummy_item_bucket():
    file_name = get_random_string(10)
    return {
        "id": random.randint(1, 10000),
        "title": get_random_string(10),
        "mime_type": "image/jpeg",
        "file_path": f"images/{file_name}.jpg",
        "file_size": random.randint(100000, 10000000),
        "created_by_id": random.randint(0, 365),
        "date_created": get_random_datetime(),
    }


@pytest.fixture(scope="session")
def dummy_item_vimeo():
    file_name = get_random_string(30)
    return {
        "id": random.randint(1, 10000),
        "title": get_random_string(10),
        "video_id": "None",
        "thumbnail": f"https://i.vimeocdn.com/video/{file_name}_960x540?r=pad",
        "width": 1920,
        "height": 1080,
        "created_by_id": random.randint(0, 365),
        "date_created": get_random_datetime(),
    }


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


@pytest.fixture(scope="function")
def mock_db_bulk_update():
    with patch("app.db.Database.bulk_update") as mock_func:
        yield mock_func
