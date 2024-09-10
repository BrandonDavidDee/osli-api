import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import get_random_datetime


@pytest.fixture(scope="function")
def mock_bg_tasks():
    with patch("app.public.item_links.routes.BackgroundTasks.add_task") as mock_func:
        yield mock_func


class TestPublicItemLinksVimeo:
    url = "/api/public/item/some-random-string"

    def test_public_item_link_not_found(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []
        response = client.get(self.url)
        assert response.status_code == 404

    def test_public_item_not_active(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "item_link_id": 2091,
                "view_count": 3,
                "public_link_title": "Some Title",
                "is_active": False,
                "expiration_date": None,
                "item_bucket_id": None,
                "bucket_title": None,
                "bucket_mime_type": None,
                "bucket_file_path": None,
                "bucket_file_size": None,
                "bucket_date_created": None,
                "bucket_created_by_id": None,
                "source_bucket_id": None,
                "source_bucket_title": None,
                "source_bucket_media_prefix": None,
                "item_vimeo_id": 155,
                "item_vimeo_width": 1920,
                "item_vimeo_height": 1014,
                "item_vimeo_title": "Item Vimeo Title",
                "item_vimeo_thumbnail": "https://i.vimeocdn.com/video/file_name_960x540?r=pad",
                "item_vimeo_video_id": "828767544",
                "item_vimeo_date_created": get_random_datetime(),
                "item_vimeo_created_by_id": 1,
            }
        ]
        response = client.get(self.url)
        assert response.status_code == 404

    def test_public_item_links(self, client, mock_db_select_many, mock_bg_tasks):
        mock_bg_tasks.return_value = MagicMock()
        mock_db_select_many.return_value = [
            {
                "item_link_id": 2091,
                "view_count": 3,
                "public_link_title": "Some Title",
                "is_active": True,
                "expiration_date": None,
                "item_bucket_id": None,
                "bucket_title": None,
                "bucket_mime_type": None,
                "bucket_file_path": None,
                "bucket_file_size": None,
                "bucket_date_created": None,
                "bucket_created_by_id": None,
                "source_bucket_id": None,
                "source_bucket_title": None,
                "source_bucket_media_prefix": None,
                "item_vimeo_id": 155,
                "item_vimeo_width": 1920,
                "item_vimeo_height": 1014,
                "item_vimeo_title": "Item Vimeo Title",
                "item_vimeo_thumbnail": "https://i.vimeocdn.com/video/file_name_960x540?r=pad",
                "item_vimeo_video_id": "828767544",
                "item_vimeo_date_created": get_random_datetime(),
                "item_vimeo_created_by_id": 1,
            }
        ]
        response = client.get(self.url)
        assert response.status_code == 200
