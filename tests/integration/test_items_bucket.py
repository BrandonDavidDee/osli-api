from io import BytesIO
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.items.bucket.controllers.item_upload import BatchUploadController
from app.items.bucket.controllers.item_list import ItemBucketListController


@pytest.fixture
def mock_s3_api_controller():
    with patch.object(
        BatchUploadController, "s3_batch_upload", new_callable=AsyncMock
    ) as mock_s3_api_controller:
        yield mock_s3_api_controller


@pytest.fixture
def mock_database_select_many():
    with patch("app.controller.db.select_many") as mock_method:
        yield mock_method


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


class TestItemBucketSearch:
    url = "/api/items/bucket/search?source_id=1"

    def test_search_no_tags(self, client):
        sample_payload = {"tag_ids": []}
        mock_db_response = [
            {
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
            },
        ]
        with patch(
            "app.db.Database.select_many", return_value=mock_db_response
        ) as mock_select_many:
            response = client.post(self.url, json=sample_payload)
            assert response.status_code == 200
            mock_select_many.assert_called_once()
            data = response.json()
            assert "source" in data
            assert "items" in data
            assert len(data["items"]) == len(mock_db_response)

    def test_search_no_tags_no_results(self, client):
        sample_payload = {"tag_ids": []}
        mock_db_response = []
        mock_source_detail_response = MagicMock()
        with patch(
            "app.db.Database.select_many", return_value=mock_db_response
        ) as mock_select_many, patch.object(
            ItemBucketListController,
            "source_detail",
            return_value=mock_source_detail_response,
        ) as mock_source_detail:
            response = client.post(self.url, json=sample_payload)
            assert response.status_code == 200
            mock_select_many.assert_called_once()
            mock_source_detail.assert_called_once()  # is called when there are no results
            data = response.json()
            assert "source" in data
            assert "items" in data
            assert len(data["items"]) == len(mock_db_response)
