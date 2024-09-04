class TestTags:
    def test_tags_with_mock_db(self, client, db_select_many):
        db_select_many.return_value = [
            {"id": 1, "title": "Tag1"},
            {"id": 2, "title": "Tag2"},
        ]
        response = client.get("/api/tags")
        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "title": "Tag1"},
            {"id": 2, "title": "Tag2"},
        ]
        db_select_many.assert_called_once_with("SELECT * FROM tag")
