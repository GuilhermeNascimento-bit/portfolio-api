from unittest.mock import patch


def test_stats_returns_correct_structure(client, redis_empty):
    with patch("app.routes.stats.get_redis", return_value=redis_empty):
        response = client.get("/stats")

    assert response.status_code == 200
    data = response.json()
    assert "requests_24h" in data
    assert "avg_response_ms" in data


def test_stats_sums_hourly_buckets(client, redis_with_stats):
    with patch("app.routes.stats.get_redis", return_value=redis_with_stats):
        response = client.get("/stats")

    # mget returns ["10", "5", None, "3"] → total = 18
    assert response.json()["requests_24h"] == 18


def test_stats_calculates_avg_response_time(client, redis_with_stats):
    with patch("app.routes.stats.get_redis", return_value=redis_with_stats):
        response = client.get("/stats")

    # lrange returns ["12.5", "8.2", "20.0", "9.1"] → avg = 12.45
    assert response.json()["avg_response_ms"] == 12.5


def test_stats_returns_zeros_when_redis_is_down(client, redis_down):
    with patch("app.routes.stats.get_redis", return_value=redis_down):
        response = client.get("/stats")

    assert response.status_code == 200
    assert response.json() == {"requests_24h": 0, "avg_response_ms": 0}


def test_stats_returns_zero_avg_with_no_data(client, redis_empty):
    with patch("app.routes.stats.get_redis", return_value=redis_empty):
        response = client.get("/stats")

    assert response.json()["avg_response_ms"] == 0
