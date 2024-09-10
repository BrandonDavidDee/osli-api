import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import get_random_datetime


@pytest.fixture(scope="function")
def mock_bg_tasks():
    with patch("app.public.gallery_links.routes.BackgroundTasks.add_task") as mock_func:
        yield mock_func


class TestPublicGalleryLinks:
    gallery_link_id = 5
    gallery_date_created = get_random_datetime()
    url = "/api/public/gallery/some-random-string"

    def test_public_gallery_links_not_found(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []
        response = client.get(self.url)
        assert response.status_code == 404

    def test_public_gallery_links_not_active(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "gallery_link_id": self.gallery_link_id,
                "view_count": 100,
                "public_link_title": "Public Link Title",
                "is_active": False,
                "id": 1,
                "title": None,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@user",
                "user_is_active": True,
                "gallery_item_id": None,
                "item_order": None,
                "item_date_created": None,
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
                "item_vimeo_id": None,
                "source_vimeo_id": None,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": None,
                "item_vimeo_width": None,
                "item_vimeo_height": None,
                "item_vimeo_video_id": None,
                "item_vimeo_date_created": None,
                "item_vimeo_created_by_id": None,
            }
        ]
        response = client.get(self.url)
        assert response.status_code == 404

    def test_public_gallery_links_no_items(
        self, client, mock_db_select_many, mock_bg_tasks
    ):
        mock_bg_tasks.return_value = MagicMock()
        mock_db_select_many.return_value = [
            {
                "gallery_link_id": self.gallery_link_id,
                "view_count": 100,
                "public_link_title": "Public Link Title",
                "is_active": True,
                "id": 1,
                "title": None,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@user",
                "user_is_active": True,
                "gallery_item_id": None,
                "item_order": None,
                "item_date_created": None,
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
                "item_vimeo_id": None,
                "source_vimeo_id": None,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": None,
                "item_vimeo_width": None,
                "item_vimeo_height": None,
                "item_vimeo_video_id": None,
                "item_vimeo_date_created": None,
                "item_vimeo_created_by_id": None,
            }
        ]
        response = client.get(self.url)
        assert response.status_code == 200

    def test_public_gallery_links(self, client, mock_db_select_many, mock_bg_tasks):
        mock_bg_tasks.return_value = MagicMock()
        mock_db_select_many.return_value = [
            {
                "gallery_link_id": self.gallery_link_id,
                "view_count": 100,
                "public_link_title": "Public Link Title",
                "is_active": True,
                "id": 1,
                "title": None,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@user",
                "user_is_active": True,
                "gallery_item_id": 2001,
                "item_order": 0,
                "item_date_created": get_random_datetime(),
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
                "item_vimeo_id": 152,
                "source_vimeo_id": 1,
                "item_vimeo_title": "Vimeo Item Title",
                "item_vimeo_thumbnail": "https://i.vimeocdn.com/video/file_name_960x540?r=pad",
                "item_vimeo_width": 1920,
                "item_vimeo_height": 1014,
                "item_vimeo_video_id": "8254447490565",
                "item_vimeo_date_created": get_random_datetime(),
                "item_vimeo_created_by_id": 1,
            },
            {
                "gallery_link_id": self.gallery_link_id,
                "view_count": 100,
                "public_link_title": "Public Link Title",
                "is_active": True,
                "id": 1,
                "title": None,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@user",
                "user_is_active": True,
                "gallery_item_id": 2002,
                "item_order": 1,
                "item_date_created": get_random_datetime(),
                "item_bucket_id": 916,
                "bucket_title": None,
                "bucket_mime_type": "image/jpeg",
                "bucket_file_path": "images/random-file.jpg",
                "bucket_file_size": 530397,
                "bucket_date_created": get_random_datetime(),
                "bucket_created_by_id": 1,
                "source_bucket_id": 1,
                "source_bucket_title": "Bucket Title",
                "source_bucket_media_prefix": "https://bucket-prefix.com",
                "item_vimeo_id": None,
                "source_vimeo_id": None,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": None,
                "item_vimeo_width": None,
                "item_vimeo_height": None,
                "item_vimeo_video_id": None,
                "item_vimeo_date_created": None,
                "item_vimeo_created_by_id": None,
            },
        ]
        response = client.get(self.url)
        assert response.status_code == 200
