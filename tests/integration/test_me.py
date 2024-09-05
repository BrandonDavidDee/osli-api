from unittest.mock import AsyncMock, patch

import pytest

from app.me.controllers.saved_items import SavedItemsController


@pytest.fixture
def mock_get_bucket_items():
    with patch.object(
        SavedItemsController, "get_saved_bucket_items", new_callable=AsyncMock
    ) as mock_data:
        yield mock_data


@pytest.fixture
def mock_get_vimeo_items():
    with patch.object(
        SavedItemsController, "get_saved_vimeo_items", new_callable=AsyncMock
    ) as mock_data:
        yield mock_data


def test_saved_items(client, mock_get_bucket_items, mock_get_vimeo_items):
    mock_get_bucket_items.return_value = [
        {
            "id": 1,
            "source_bucket_id": 1,
            "title": "",
            "mime_type": "",
            "file_path": "bucket-dir/my_file.jpg",
            "file_size": 1000,
            "notes": "",
            "date_created": "2024-01-01 12:12:12.000",
            "created_by_id": 1,
            "date_saved": "2024-01-01 12:12:12.000",
            "source_title": "source-title",
            "bucket_name": "bucket-name",
            "media_prefix": "",
            "grid_view": "true",
        }
    ]
    mock_get_vimeo_items.return_value = [
        {
            "id": 1,
            "source_vimeo_id": 1,
            "video_id": "12345",
            "title": "title",
            "thumbnail": "thumbnail",
            "date_created": "2024-01-01 12:12:12.000",
            "created_by_id": 1,
            "width": 1,
            "height": 1,
            "date_saved": "2024-01-01 12:12:12.000",
            "source_title": "foo",
            "client_identifier": "",
            "client_secret": "",
            "access_token": "",
            "grid_view": "true",
        }
    ]
    response = client.get("/api/me/saved-items")
    assert response.status_code == 200
