class TestItemBucketSave:
    item_id = 102030

    def test_save_bucket_item(self, client, mock_db_insert):
        mock_db_insert.return_value = {"id": 899}

        response = client.post(f"/api/items/bucket/{self.item_id}/save")
        data = response.json()

        assert response.status_code == 200
        assert data is None

    def test_delete_saved_bucket_item(self, client, mock_db_delete_one):
        mock_db_delete_one.return_value = {}

        response = client.delete(f"/api/items/bucket/{self.item_id}/save")
        data = response.json()

        assert response.status_code == 200
        assert data is None
