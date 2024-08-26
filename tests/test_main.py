# type: ignore


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"OSLI": "(Multiple) Object Storage Library Index"}

