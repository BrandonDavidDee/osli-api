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
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1
        mock_database_select_many.assert_called_once()

    def test_search_no_tags_no_results(
        self, client, mock_database_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_database_select_many.return_value = []

        response = client.post(self.url, json=self.payload)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0
        mock_database_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results

    def test_search_with_tags(self, client, mock_database_select_many):
        mock_database_select_many.return_value = [self.mock_db_row]

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1
        mock_database_select_many.assert_called_once()

    def test_search_with_tags_no_results(
        self, client, mock_database_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_database_select_many.return_value = []

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0
        mock_database_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results


class TestItemBucketDetail:
    item_id = 100
    source_id = 1
    mock_tag_id_alpha = 11002299
    mock_tag_id_bravo = 33884477
    url = f"/api/items/bucket/{item_id}?source_id={source_id}"
    mock_db_rows = [
        {
            "id": item_id,
            "source_bucket_id": source_id,
            "title": None,
            "mime_type": "image/jpeg",
            "file_path": "pages/a_random_image.jpg",
            "file_size": 239762,
            "notes": None,
            "date_created": "2023-07-13T16:45:52.038852+00:00",
            "created_by_id": 1,
            "saved_item_id": None,
            "source_title": "",
            "bucket_name": "",
            "media_prefix": "",
            "grid_view": True,
            "tag_item_id": 318,
            "tag_id": mock_tag_id_alpha,
            "tag_title": "Alpha",
        },
        {
            "id": item_id,
            "source_bucket_id": source_id,
            "title": None,
            "mime_type": "image/jpeg",
            "file_path": "pages/a_random_image.jpg",
            "file_size": 239762,
            "notes": None,
            "date_created": "2023-07-13T16:45:52.038852+00:00",
            "created_by_id": 1,
            "saved_item_id": None,
            "source_title": "",
            "bucket_name": "",
            "media_prefix": "",
            "grid_view": True,
            "tag_item_id": 319,
            "tag_id": mock_tag_id_bravo,
            "tag_title": "Bravo",
        },
    ]

    def test_detail_not_found(self, client, mock_database_select_many):
        mock_database_select_many.return_value = []
        response = client.get(self.url)
        assert response.status_code == 404

    def test_detail(self, client, mock_database_select_many):
        mock_database_select_many.return_value = self.mock_db_rows

        response = client.get(self.url)
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == self.item_id
        assert len(data["tags"]) == 2
        tag_alpha_exists = bool(
            next(
                (x for x in data["tags"] if x["tag"]["id"] == self.mock_tag_id_alpha),
                None,
            )
        )
        tag_bravo_exists = bool(
            next(
                (x for x in data["tags"] if x["tag"]["id"] == self.mock_tag_id_bravo),
                None,
            )
        )
        assert tag_alpha_exists is True
        assert tag_bravo_exists is True
        mock_database_select_many.assert_called_once()
