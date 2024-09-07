from datetime import datetime
from fastapi import Response


class TestItemVimeoLinkCreate:
    item_id = 2000
    url = f"/api/items/vimeo/{item_id}/links?source_id=1"

    def test_item_link_create_missing_source_id(self, client):
        response = client.post(url=f"/api/items/vimeo/{self.item_id}/links")
        assert response.status_code == 422

    def test_item_link_create(self, client, mock_db_insert):
        date_created = datetime(2024, 1, 1)
        mock_db_insert.return_value = {"id": 888, "date_created": date_created}

        payload = {"title": "", "link": "", "expiration_date": None, "is_active": True}
        response = client.post(self.url, json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == 888
        assert data["date_created"] is not None
        mock_db_insert.assert_called_once()


class TestItemVimeoLinks:
    item_id = 100
    source_id = 1
    url = f"/api/items/vimeo/{item_id}/links"

    def test_get_item_links_no_results(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "id": self.item_id,
                "source_vimeo_id": self.source_id,
                "title": "Foobar",
                "video_id": "192837465",
                "thumbnail": "some-location-on-vimeo.jpg",
                "width": None,
                "height": None,
                "notes": None,
                "date_created": "2024-08-08T19:17:38.419580+00:00",
                "created_by_id": 1,
                "link_id": None,
                "link_title": None,
                "link_link": None,
                "link_expiration_date": None,
                "link_view_count": None,
                "link_date_created": None,
                "link_is_active": None,
                "user_id": None,
                "username": None,
                "user_is_active": None,
            },
        ]

        response = client.get(self.url)
        data = response.json()
        links = data["links"]

        assert response.status_code == 200
        assert len(links) == 0

    def test_get_item_links(self, client, mock_db_select_many):
        mock_db_select_many.return_value = [
            {
                "id": self.item_id,
                "source_vimeo_id": self.source_id,
                "title": "Foobar",
                "video_id": "192837465",
                "thumbnail": "some-location-on-vimeo.jpg",
                "width": None,
                "height": None,
                "notes": None,
                "date_created": "2024-08-08T19:17:38.419580+00:00",
                "created_by_id": 1,
                "link_id": 601,
                "link_title": "Link Alpha",
                "link_link": "some-random-link-one",
                "link_expiration_date": None,
                "link_view_count": 8,
                "link_date_created": "2024-08-09T18:15:40.960744+00:00",
                "link_is_active": True,
                "user_id": 1,
                "username": "username_alpha",
                "user_is_active": True,
            },
            {
                "id": self.item_id,
                "source_vimeo_id": self.source_id,
                "title": "Foobar",
                "video_id": "192837465",
                "thumbnail": "some-location-on-vimeo.jpg",
                "width": None,
                "height": None,
                "notes": None,
                "date_created": "2024-08-08T19:17:38.419580+00:00",
                "created_by_id": 1,
                "link_id": 602,
                "link_title": "Link Bravo",
                "link_link": "some-random-link-two",
                "link_expiration_date": None,
                "link_view_count": 1,
                "link_date_created": "2024-08-15T15:07:11.229937+00:00",
                "link_is_active": True,
                "user_id": 2,
                "username": "username_bravo",
                "user_is_active": True,
            },
        ]

        response = client.get(self.url)
        data = response.json()
        links = data["links"]

        assert response.status_code == 200
        assert len(links) == 2
        link_alpha_exists = bool(
            next(
                (x for x in links if x["id"] == 601),
                None,
            )
        )
        assert link_alpha_exists is True
        link_bravo_exists = bool(
            next(
                (x for x in links if x["id"] == 602),
                None,
            )
        )
        assert link_bravo_exists is True


class TestItemVimeoLinkDelete:
    item_id = 100
    item_link_id = 7777
    url = f"/api/items/vimeo/{item_id}/links/{item_link_id}"

    def test_item_link_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = Response()

        response = client.delete(self.url)
        data = response.json()

        assert response.status_code == 200
        assert data == self.item_link_id
