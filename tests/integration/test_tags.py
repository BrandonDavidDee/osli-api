import pytest
from unittest.mock import patch, AsyncMock
from app.tags.controller import TagController


@pytest.fixture(scope="function")
def mock_get_bucket_tag_count():
    with patch.object(
        TagController, "_get_bucket_tag_count", new_callable=AsyncMock
    ) as mock_method:
        yield mock_method


@pytest.fixture(scope="function")
def mock_get_vimeo_tag_count():
    with patch.object(
        TagController, "_get_vimeo_tag_count", new_callable=AsyncMock
    ) as mock_method:
        yield mock_method


class TestTags:
    def test_tag_create(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 1111, "title": "new tag name"}
        payload = {"id": None, "title": "new tag name"}
        response = client.post("/api/tags", json=payload)
        data = response.json()
        assert data == {"id": 1111, "title": "new tag name"}

    def test_tags_list(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {"id": 1, "title": "Tag1"},
            {"id": 2, "title": "Tag2"},
        ]
        response = client.get("/api/tags")
        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "title": "Tag1"},
            {"id": 2, "title": "Tag2"},
        ]

    def test_tag_update(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 2222, "title": "updated tag name"}
        payload = {"id": 2222, "title": "updated tag name"}
        response = client.put(f"/api/tags/{2222}", json=payload)
        data = response.json()
        assert data == {"id": 2222, "title": "updated tag name"}

    def test_tag_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = 3333
        response = client.delete(f"/api/tags/{3333}")
        data = response.json()
        assert data == 3333

    def test_tags_related(
        self, client, mock_get_bucket_tag_count, mock_get_vimeo_tag_count
    ):
        mock_get_bucket_tag_count.return_value = 5
        mock_get_vimeo_tag_count.return_value = 10
        response = client.get(f"/api/tags/{3333}/related")
        data = response.json()
        assert data == 15
