from datetime import datetime
from tests.conftest import get_random_datetime


class TestGalleryLinkCreate:
    def test_gallery_link_create(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 1987, "date_created": datetime.now()}

        payload = {
            "id": None,
            "title": "Test Title",
            "link": "",
            "is_active": True,
            "expiration_date": None,
        }
        response = client.post("/api/galleries/1/links", json=payload)

        assert response.status_code == 200


class TestGalleryLinkList:
    gallery_id = 1
    gallery_title = "Test Title"
    gallery_date_created = get_random_datetime()

    def test_gallery_not_found(self, client, mock_db_select_many):
        mock_db_select_many.return_value = []
        response = client.get(f"/api/galleries/{self.gallery_id}/links")
        assert response.status_code == 404

    def test_gallery_links_none(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "id": self.gallery_id,
                "title": self.gallery_title,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@username",
                "user_is_active": True,
                "link_id": None,
                "link_title": None,
                "link_link": None,
                "link_expiration_date": None,
                "link_view_count": None,
                "link_date_created": None,
                "link_is_active": None,
                "link_user_id": None,
                "link_username": None,
                "link_user_is_active": None,
            },
        ]
        response = client.get(f"/api/galleries/{self.gallery_id}/links")
        data = response.json()
        links = data["links"]

        assert response.status_code == 200
        assert len(links) == 0

    def test_gallery_links_list(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "id": self.gallery_id,
                "title": self.gallery_title,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@username",
                "user_is_active": True,
                "link_id": 33,
                "link_title": None,
                "link_link": "665f4bcb-f74c-4119-9d01-f61d3efa0d92",
                "link_expiration_date": None,
                "link_view_count": None,
                "link_date_created": get_random_datetime(),
                "link_is_active": None,
                "link_user_id": 1,
                "link_username": "user-one@username",
                "link_user_is_active": True,
            },
            {
                "id": self.gallery_id,
                "title": self.gallery_title,
                "view_type": "grid",
                "description": None,
                "date_created": self.gallery_date_created,
                "created_by_id": 1,
                "user_id": 1,
                "username": "user-one@username",
                "user_is_active": True,
                "link_id": 34,
                "link_title": "Link 2 Title",
                "link_link": "ad404fbe-f8d3-41db-b510-8c3c330546d3",
                "link_expiration_date": None,
                "link_view_count": None,
                "link_date_created": get_random_datetime(),
                "link_is_active": None,
                "link_user_id": 2,
                "link_username": "user-two@username",
                "link_user_is_active": True,
            },
        ]
        response = client.get(f"/api/galleries/{self.gallery_id}/links")
        data = response.json()
        links = data["links"]

        assert response.status_code == 200
        assert len(links) == 2
        link_one_exists = bool(
            next(
                (x for x in links if x["id"] == 33),
                None,
            )
        )
        assert link_one_exists is True
        link_two_title = bool(
            next(
                (x for x in links if x["title"] == "Link 2 Title"),
                None,
            )
        )
        assert link_two_title is True


class TestGalleryLinkUpdate:
    gallery_id = 1
    gallery_link_id = 45

    def test_gallery_link_update(self, client, mock_db_insert):
        mock_db_insert.return_value = {"title": "updated title"}

        payload = {
            "id": self.gallery_link_id,
            "title": "Test Title",
            "link": "",
            "is_active": True,
            "expiration_date": None,
        }
        response = client.put(
            f"/api/galleries/{self.gallery_id}/links/{self.gallery_link_id}",
            json=payload,
        )
        assert response.status_code == 200

    def test_gallery_link_only_update(self, client, mock_db_insert):
        mock_db_insert.return_value = {"link": "updated-link"}

        payload = {
            "id": self.gallery_link_id,
            "link": "",
        }
        response = client.put(
            f"/api/galleries/{self.gallery_id}/links/{self.gallery_link_id}?link_only={True}",
            json=payload,
        )
        assert response.status_code == 200


class TestGalleryLinkDelete:
    gallery_id = 1
    gallery_link_id = 45

    def test_gallery_link_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = {}
        response = client.delete(
            f"/api/galleries/{self.gallery_id}/links/{self.gallery_link_id}"
        )
        data = response.json()

        assert response.status_code == 200
        assert data == self.gallery_link_id


class TestLinkAvailability:
    def test_link_availability(self, client, mock_db_select_one):
        mock_db_select_one.return_value = {"id": 100}

        link = "something-custom"
        response = client.get(f"/api/galleries/link-availability/{link}")
        data = response.json()

        assert response.status_code == 200
        assert data is True

    def test_link_availability_no_result(self, client, mock_db_select_one):
        mock_db_select_one.return_value = None

        link = "something-custom"
        response = client.get(f"/api/galleries/link-availability/{link}")
        data = response.json()

        assert response.status_code == 200
        assert data is False
