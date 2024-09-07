from fastapi import Response


class TestItemVimeoTagCreate:
    item_id = 100
    url = f"/api/items/vimeo/{item_id}/tags?source_id=1"

    def test_tag_create_missing_source_id(self, client):
        response = client.post(f"/api/items/vimeo/{self.item_id}/tags")
        assert response.status_code == 422

    def test_tag_create(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 123}

        payload = {"id": None, "tag": {"id": 1000, "title": "Tag Title"}}
        response = client.post(self.url, json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == 123
        mock_db_insert.assert_called_once()


class TestItemVimeoTagDelete:
    item_id = 100
    tag_item_vimeo_id = 9123
    url = f"/api/items/vimeo/{item_id}/tags/{tag_item_vimeo_id}?source_id=1"

    def test_tag_delete_missing_source_id(self, client):
        response = client.delete(
            f"/api/items/vimeo/{self.item_id}/tags/{self.tag_item_vimeo_id}"
        )
        assert response.status_code == 422

    def test_tag_delete(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = Response()
        response = client.delete(self.url)
        assert response.status_code == 200
        mock_db_delete_one.assert_called_once()
