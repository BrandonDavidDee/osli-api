from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest

from app.items.bucket.controllers.item_upload import BatchUploadController


@pytest.fixture
def mock_s3_api_controller():
    with patch.object(
        BatchUploadController, "s3_batch_upload", new_callable=AsyncMock
    ) as mock_s3_api_controller:
        yield mock_s3_api_controller


def test_item_batch_upload(client, mock_s3_api_controller):
    mock_s3_api_controller.return_value = {"new_keys": ["key1", "key2"]}
    files = [
        ("files", ("file1.txt", BytesIO(b"file1 content"), "text/plain")),
        ("files", ("file2.txt", BytesIO(b"file2 content"), "text/plain")),
    ]
    data = {"source_id": 123, "encryption_key": "my-secret-key"}
    response = client.post("/api/items/bucket", params=data, files=files)
    assert response.status_code == 200
    assert response.json() == {"new_keys": ["key1", "key2"]}
