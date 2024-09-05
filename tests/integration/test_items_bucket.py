from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest

from app.items.bucket.controllers.item_upload import BatchUploadController
from app.items.bucket.controllers.item_list import ItemBucketListController


@pytest.fixture
def mock_s3_api_controller():
    with patch.object(
        BatchUploadController, "s3_batch_upload", new_callable=AsyncMock
    ) as mock_s3_api_controller:
        yield mock_s3_api_controller


class TestItemBucketUpload:
    def test_item_batch_upload(self, client, mock_s3_api_controller):
        mock_s3_api_controller.return_value = {"new_keys": ["key1", "key2"]}
        files = [
            ("files", ("file1.txt", BytesIO(b"file1 content"), "text/plain")),
            ("files", ("file2.txt", BytesIO(b"file2 content"), "text/plain")),
        ]
        data = {"source_id": 123, "encryption_key": "my-secret-key"}
        response = client.post("/api/items/bucket", params=data, files=files)
        assert response.status_code == 200
        assert response.json() == {"new_keys": ["key1", "key2"]}


@pytest.fixture
def mock_database_select_many():
    with patch("app.db.Database.select_many") as mock_select_many:
        yield mock_select_many


@pytest.fixture
def mock_source_detail():
    with patch.object(ItemBucketListController, "source_detail") as mock_source_detail:
        yield mock_source_detail


class TestItemBucketSearch:
    url = "/api/items/bucket/search?source_id=1"
    payload = {"tag_ids": []}
    payload_with_tags = {"tag_ids": [1, 2, 3, 4]}
    mock_db_row = {
        "total_count": 1075,
        "id": 1111,
        "source_bucket_id": 1,
        "title": "Some Title",
        "mime_type": "image/jpeg",
        "file_path": "images/some_file.jpg",
        "file_size": 123456789,
        "notes": None,
        "date_created": "2024-08-08T19:17:38.419580+00:00",
        "created_by_id": 1,
        "source_title": "Source Title",
        "bucket_name": "bucket-name",
        "media_prefix": "",
        "grid_view": True,
    }

    def test_search_no_tags(self, client, mock_database_select_many):
        mock_database_select_many.return_value = [self.mock_db_row]

        response = client.post(self.url, json=self.payload)
        data = response.json()

        assert response.status_code == 200
        mock_database_select_many.assert_called_once()
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1

    def test_search_no_tags_no_results(
        self, client, mock_database_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_database_select_many.return_value = []

        response = client.post(self.url, json=self.payload)
        data = response.json()

        assert response.status_code == 200
        mock_database_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0

    def test_search_with_tags(self, client, mock_database_select_many):
        mock_database_select_many.return_value = [self.mock_db_row]

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        mock_database_select_many.assert_called_once()
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1

    def test_search_with_tags_no_results(
        self, client, mock_database_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_database_select_many.return_value = []

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        mock_database_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0
