# type: ignore


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"OSLI": "(Multiple) Object Storage Library Index"}


def test_tags(authenticated_client):
    response = authenticated_client.get("/api/tags")
    assert response.status_code == 200
