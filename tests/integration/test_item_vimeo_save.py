class TestItemVimeoSave:
    item_id = 98765

    def test_save_vimeo_item(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 9113}

        response = client.post(f"/api/items/vimeo/{self.item_id}/save")
        data = response.json()

        assert response.status_code == 200
        assert data is None

    def test_delete_saved_vimeo_item(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = {}

        response = client.delete(f"/api/items/vimeo/{self.item_id}/save")
        data = response.json()

        assert response.status_code == 200
        assert data is None
