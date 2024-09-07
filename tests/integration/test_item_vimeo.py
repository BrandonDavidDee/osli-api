from unittest.mock import patch

import pytest

from app.items.vimeo.controllers.item_list import ItemVimeoListController
from app.items.vimeo.controllers.item_detail import ItemVimeoDetailController
from app.sources.vimeo.controllers.vimeo_api import VimeoApiController


@pytest.fixture(scope="function")
def mock_source_detail():
    with patch.object(ItemVimeoListController, "source_detail") as mock_source_detail:
        yield mock_source_detail


class TestItemVimeoCreate:
    def test_item_vimeo_create_missing_encryption_key(self, client):
        response = client.post("/api/items/vimeo?source_id=1", json={})
        assert response.status_code == 422

    def test_item_vimeo_create_missing_source_id(self, client):
        response = client.post("/api/items/vimeo?encryption_key=foo", json={})
        assert response.status_code == 422

    def test_item_vimeo_create(self, client, mock_db_insert):
        meta_data_return_value = {
            "thumbnail": "foobar.jpg",
            "width": 100,
            "height": 300,
        }
        mock_db_insert.return_value = {"id": 123456789}
        with patch.object(
            VimeoApiController, "get_thumbnails", return_value=meta_data_return_value
        ) as mock_get_thumbnails:
            payload = {
                "id": None,
                "title": "foo",
                "video_id": "192837465",
                "thumbnail": "some-location-on-vimeo.jpg",
                "width": None,
                "height": None,
            }
            response = client.post(
                "/api/items/vimeo?source_id=1&encryption_key=foo", json=payload
            )
            data = response.json()

            assert response.status_code == 200
            assert data == 123456789
            mock_get_thumbnails.assert_called_once()
            mock_db_insert.assert_called_once()


class TestItemVimeoSearch:
    url = "/api/items/vimeo/search?source_id=1"
    payload = {"tag_ids": []}
    payload_with_tags = {"tag_ids": [1, 2, 3, 4]}
    mock_db_row = {
        "total_count": 1075,
        "id": 1111,
        "source_vimeo_id": 1,
        "title": "Some Title",
        "video_id": "192837465",
        "thumbnail": "some-location-on-vimeo.jpg",
        "width": None,
        "height": None,
        "notes": None,
        "date_created": "2024-08-08T19:17:38.419580+00:00",
        "created_by_id": 1,
        "source_title": "Source Title",
        "client_identifier": "foo",
        "client_secret": "foo",
        "access_token": "foo",
        "grid_view": True,
    }

    def test_search_no_tags(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [self.mock_db_row]

        response = client.post(self.url, json=self.payload)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1
        mock_db_select_many.assert_called_once()

    def test_search_no_tags_no_results(
        self, client, mock_db_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_db_select_many.return_value = []

        response = client.post(self.url, json=self.payload)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0
        mock_db_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results

    def test_search_with_tags(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [self.mock_db_row]

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 1
        mock_db_select_many.assert_called_once()

    def test_search_with_tags_no_results(
        self, client, mock_db_select_many, mock_source_detail
    ):
        mock_source_detail.return_value = {}
        mock_db_select_many.return_value = []

        response = client.post(self.url, json=self.payload_with_tags)
        data = response.json()

        assert response.status_code == 200
        assert "source" in data
        assert "items" in data
        assert len(data["items"]) == 0
        mock_db_select_many.assert_called_once()
        mock_source_detail.assert_called_once()  # is called when there are no results


class TestItemVimeoDetail:
    item_id = 100
    source_id = 1
    mock_tag_id_alpha = 11002299
    mock_tag_id_bravo = 33884477
    url = f"/api/items/vimeo/{item_id}?source_id={source_id}"
    mock_db_rows = [
        {
            "id": item_id,
            "source_vimeo_id": source_id,
            "title": None,
            "video_id": "192837465",
            "thumbnail": "some-location-on-vimeo.jpg",
            "width": None,
            "height": None,
            "notes": None,
            "date_created": "2023-07-13T16:45:52.038852+00:00",
            "created_by_id": 1,
            "saved_item_id": None,
            "source_title": "",
            "client_identifier": "foo",
            "client_secret": "foo",
            "access_token": "foo",
            "grid_view": True,
            "tag_item_id": 318,
            "tag_id": mock_tag_id_alpha,
            "tag_title": "Alpha",
        },
        {
            "id": item_id,
            "source_vimeo_id": source_id,
            "title": None,
            "video_id": "192837465",
            "thumbnail": "some-location-on-vimeo.jpg",
            "width": None,
            "height": None,
            "notes": None,
            "date_created": "2023-07-13T16:45:52.038852+00:00",
            "created_by_id": 1,
            "saved_item_id": None,
            "source_title": "",
            "client_identifier": "foo",
            "client_secret": "foo",
            "access_token": "foo",
            "grid_view": True,
            "tag_item_id": 319,
            "tag_id": mock_tag_id_bravo,
            "tag_title": "Bravo",
        },
    ]

    def test_detail_missing_source_id(self, client):
        url = f"/api/items/vimeo/{self.item_id}"
        response = client.get(url)
        assert response.status_code == 422

    def test_detail_not_found(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []
        response = client.get(self.url)
        assert response.status_code == 404

    def test_detail(self, client, mock_db_select_many):
        mock_db_select_many.return_value = self.mock_db_rows

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
        mock_db_select_many.assert_called_once()


class TestItemVimeoUpdate:
    item_id = 100

    def test_update_missing_source_id(self, client):
        response = client.put(f"/api/items/vimeo/{self.item_id}", json={})
        assert response.status_code == 422

    def test_update(self, client, mock_db_insert):
        mock_db_insert.return_value = {}

        payload = {
            "id": self.item_id,
            "title": "foo",
            "video_id": "192837465",
            "thumbnail": "some-location-on-vimeo.jpg",
            "width": None,
            "height": None,
        }
        response = client.put(
            f"/api/items/vimeo/{self.item_id}?source_id=1", json=payload
        )
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == self.item_id


class TestItemVimeoDelete:
    item_id = 100

    url = f"/api/items/vimeo/{item_id}?source_id=1"

    def test_delete_missing_source_id(self, client):
        response = client.delete(f"/api/items/vimeo/{self.item_id}")
        assert response.status_code == 422

    def test_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = {}

        response = client.delete(self.url)
        data = response.json()

        assert response.status_code == 200
        assert data == self.item_id


class TestItemVimeoRelated:
    item_id = 100
    url = f"/api/items/vimeo/{item_id}/related?source_id=1"

    def test_related_missing_source_id(self, client):
        response = client.get(f"/api/items/vimeo/{self.item_id}/related")
        assert response.status_code == 422

    def test_related(self, client):
        with patch.object(
            ItemVimeoDetailController,
            "_get_related_gallery_items",
            return_value=[],
        ) as mock_get_related_gallery_items, patch.object(
            ItemVimeoDetailController,
            "_get_related_saved_items",
            return_value=[],
        ) as mock_get_related_saved_items:
            response = client.get(self.url)
            data = response.json()

            assert response.status_code == 200
            assert data["has_related"] is False
            mock_get_related_gallery_items.assert_called_once()
            mock_get_related_saved_items.assert_called_once()
