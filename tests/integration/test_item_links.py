class TestItemLinks:
    def test_item_link_update(self, client, mock_db_insert):
        item_link_id = 6543
        mock_db_insert.return_value = {"link": "updated-link"}
        payload = {"link": "updated-link"}
        response = client.put(f"/api/items/item-links/{item_link_id}", json=payload)
        assert response.status_code == 200

    def test_link_availability_check(self, client, mock_db_select_one):
        mock_db_select_one.return_value = {"id": 100}

        link = "custom-item-link"
        response = client.get(f"/api/items/item-links/availability/{link}")
        data = response.json()

        assert response.status_code == 200
        assert data is True

    def test_link_availability_no_result(self, client, mock_db_select_one):
        mock_db_select_one.return_value = None

        link = "custom-item-link"
        response = client.get(f"/api/items/item-links/availability/{link}")
        data = response.json()

        assert response.status_code == 200
        assert data is False
