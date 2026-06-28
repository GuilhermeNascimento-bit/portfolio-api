from unittest.mock import patch

from tests.conftest import FAKE_GITHUB_DATA


def test_github_returns_correct_structure(client, redis_empty):
    with patch("app.services.github.get_redis", return_value=redis_empty), \
         patch("app.services.github._sync_fetch", return_value=FAKE_GITHUB_DATA):
        response = client.get("/github")

    assert response.status_code == 200
    data = response.json()
    assert "public_repos" in data
    assert "followers" in data
    assert "repos" in data
    assert isinstance(data["repos"], list)


def test_github_repo_fields_are_present(client, redis_empty):
    with patch("app.services.github.get_redis", return_value=redis_empty), \
         patch("app.services.github._sync_fetch", return_value=FAKE_GITHUB_DATA):
        response = client.get("/github")

    repo = response.json()["repos"][0]
    for field in ("name", "description", "language", "stars", "url", "updated_at"):
        assert field in repo, f"Missing field: {field}"


def test_github_uses_cache_when_available(client, redis_with_cache):
    with patch("app.services.github.get_redis", return_value=redis_with_cache), \
         patch("app.services.github._sync_fetch") as mock_fetch:
        response = client.get("/github")

    assert response.status_code == 200
    mock_fetch.assert_not_called()  # GitHub was never hit


def test_github_fetches_when_cache_is_empty(client, redis_empty):
    with patch("app.services.github.get_redis", return_value=redis_empty), \
         patch("app.services.github._sync_fetch", return_value=FAKE_GITHUB_DATA) as mock_fetch:
        response = client.get("/github")

    assert response.status_code == 200
    mock_fetch.assert_called_once()


def test_github_works_when_redis_is_down(client, redis_down):
    with patch("app.services.github.get_redis", return_value=redis_down), \
         patch("app.services.github._sync_fetch", return_value=FAKE_GITHUB_DATA):
        response = client.get("/github")

    assert response.status_code == 200
    assert response.json()["public_repos"] == FAKE_GITHUB_DATA["public_repos"]


def test_github_returns_502_when_api_fails(client, redis_empty):
    with patch("app.services.github.get_redis", return_value=redis_empty), \
         patch("app.services.github._sync_fetch", side_effect=Exception("timeout")):
        response = client.get("/github")

    assert response.status_code == 502
    assert "GitHub API error" in response.json()["detail"]
