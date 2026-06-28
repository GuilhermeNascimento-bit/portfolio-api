def test_root_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "portifolio-api"}


def test_root_content_type_is_json(client):
    response = client.get("/")
    assert "application/json" in response.headers["content-type"]
