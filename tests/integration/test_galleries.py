from tests.conftest import get_random_datetime


class TestGalleryCreate:
    def test_gallery_missing_title(self, client):
        payload = {"id": None}
        response = client.post("/api/galleries", json=payload)
        assert response.status_code == 422

    def test_gallery_create(self, client, mock_db_insert):
        inserted_id = 1111
        mock_db_insert.return_value = {"id": inserted_id}

        payload = {"id": None, "title": "foo"}
        response = client.post("/api/galleries", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data == inserted_id


class TestGalleryList:
    def test_gallery_list_no_results(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []

        response = client.get("/api/galleries")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 0

    def test_gallery_list(self, client, mock_db_select_many):
        date_created = get_random_datetime()
        mock_db_select_many.return_value = [
            {
                "id": 100,
                "title": "Gallery Title",
                "view_type": "grid",
                "description": "Gallery Description",
                "date_created": date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "foo",
                "user_is_active": True,
            }
        ]

        response = client.get("/api/galleries")
        data = response.json()

        assert response.status_code == 200
        gallery_exists = bool(
            next(
                (x for x in data if x["title"] == "Gallery Title"),
                None,
            )
        )
        assert gallery_exists is True
        assert len(data) == 1


class TestGalleryDetail:
    gallery_id = 1
    title = "Gallery Title"
    gallery_date_created = get_random_datetime()
    gallery_item_bucket_date_created = get_random_datetime()
    gallery_item_vimeo_date_created = get_random_datetime()
    item_bucket_date_created = get_random_datetime()
    item_vimeo_date_created = get_random_datetime()

    def test_gallery_no_results(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []
        response = client.get(f"/api/galleries/{self.gallery_id}")
        assert response.status_code == 404

    def test_gallery_detail_no_items(self, client, mock_db_select_many):
        mock_rows = [
            {
                "id": self.gallery_id,
                "title": self.title,
                "view_type": "grid",
                "description": "Anything",
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "foo-username",
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
                "item_vimeo_width": None,
                "item_vimeo_height": None,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": None,
                "item_vimeo_video_id": None,
                "item_vimeo_date_created": None,
                "item_vimeo_created_by_id": None,
            },
        ]
        mock_db_select_many.return_value = mock_rows

        response = client.get(f"/api/galleries/{self.gallery_id}")
        data = response.json()

        assert response.status_code == 200
        assert len(data["items"]) == 0

    def test_gallery_detail(self, client, mock_db_select_many):
        mock_rows = [
            {
                "id": self.gallery_id,
                "title": self.title,
                "view_type": "grid",
                "description": "Anything",
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "foo-username",
                "user_is_active": True,
                "gallery_item_id": 37,
                "item_order": 1,
                "item_date_created": self.gallery_item_vimeo_date_created,
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
                "item_vimeo_id": 158,
                "source_vimeo_id": 1,
                "item_vimeo_width": 2160,
                "item_vimeo_height": 3840,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": "some-random-image.jpg",
                "item_vimeo_video_id": "998340896",
                "item_vimeo_date_created": self.item_vimeo_date_created,
                "item_vimeo_created_by_id": 1,
            },
            {
                "id": self.gallery_id,
                "title": self.title,
                "view_type": "grid",
                "description": "Anything",
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "foo-username",
                "user_is_active": True,
                "gallery_item_id": 35,
                "item_order": 23,
                "item_date_created": self.gallery_item_bucket_date_created,
                "item_bucket_id": 916,
                "bucket_title": None,
                "bucket_mime_type": "image/jpeg",
                "bucket_file_path": "images/a-random-image.jpg",
                "bucket_file_size": 530397,
                "bucket_date_created": self.item_bucket_date_created,
                "bucket_created_by_id": 1,
                "source_bucket_id": 1,
                "source_bucket_title": "Bucket Title",
                "source_bucket_media_prefix": "",
                "item_vimeo_id": None,
                "source_vimeo_id": None,
                "item_vimeo_width": None,
                "item_vimeo_height": None,
                "item_vimeo_title": None,
                "item_vimeo_thumbnail": None,
                "item_vimeo_video_id": None,
                "item_vimeo_date_created": None,
                "item_vimeo_created_by_id": None,
            },
        ]
        mock_db_select_many.return_value = mock_rows

        response = client.get(f"/api/galleries/{self.gallery_id}")
        data = response.json()

        assert response.status_code == 200
        assert len(data["items"]) == 2


class TestGalleryUpdate:
    def test_gallery_update(self, client, mock_db_bulk_update):
        gallery_id = 1
        mock_db_bulk_update.return_value = None

        payload = {"id": gallery_id, "title": "Gallery Title", "items": []}
        response = client.put(f"/api/galleries/{gallery_id}", json=payload)

        assert response.status_code == 200


class TestGalleryItems:
    def test_gallery_item_unknown_create(self, client):
        payload = {
            "id": 0,
            "item_order": 0,
            "source_id": 1,
            "source_type": "something-else",
        }
        response = client.post("/api/galleries/1/items", json=payload)

        assert response.status_code == 422

    def test_gallery_item_bucket_create(
        self, client, dummy_item_bucket, mock_db_insert
    ):
        mock_db_insert.return_value = {"id": 919191}
        payload = {
            "id": 0,
            "item_order": 0,
            "source_id": 1,
            "source_type": "bucket",
            "item_bucket": dummy_item_bucket,
        }
        response = client.post("/api/galleries/1/items", json=payload)
        assert response.status_code == 200

    def test_gallery_item_vimeo_create(self, client, dummy_item_vimeo, mock_db_insert):
        mock_db_insert.return_value = {"id": 919191}
        payload = {
            "id": 0,
            "item_order": 0,
            "source_id": 1,
            "source_type": "vimeo",
            "item_vimeo": dummy_item_vimeo,
        }
        response = client.post("/api/galleries/1/items", json=payload)
        assert response.status_code == 200

    def test_gallery_item_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = None
        response = client.delete("/api/galleries/1/items/76543")
        assert response.status_code == 200
