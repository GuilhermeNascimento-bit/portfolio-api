import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app

FAKE_GITHUB_DATA = {
    "public_repos": 8,
    "followers": 12,
    "repos": [
        {
            "name": "portifolio-api",
            "description": "My portfolio backend",
            "language": "Python",
            "stars": 3,
            "url": "https://github.com/GuilhermeNascimento-bit/portifolio-api",
            "updated_at": "2026-06-28T00:00:00Z",
        },
        {
            "name": "finance-app",
            "description": "Personal finance manager",
            "language": "JavaScript",
            "stars": 1,
            "url": "https://github.com/GuilhermeNascimento-bit/finance-app",
            "updated_at": "2026-06-20T00:00:00Z",
        },
    ],
}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def redis_empty():
    """Redis online but cache is empty (cache miss)."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.mget.return_value = []
    mock.lrange.return_value = []
    pipe = MagicMock()
    pipe.incr = MagicMock()
    pipe.expire = MagicMock()
    pipe.lpush = MagicMock()
    pipe.ltrim = MagicMock()
    pipe.execute = AsyncMock(return_value=[1, True, 1, 1])
    mock.pipeline.return_value = pipe
    return mock


@pytest.fixture
def redis_with_cache(redis_empty):
    """Redis online with GitHub data already cached."""
    redis_empty.get.return_value = json.dumps(FAKE_GITHUB_DATA)
    return redis_empty


@pytest.fixture
def redis_with_stats(redis_empty):
    """Redis online with request metrics stored."""
    redis_empty.mget.return_value = ["10", "5", None, "3"]
    redis_empty.lrange.return_value = ["12.5", "8.2", "20.0", "9.1"]
    return redis_empty


@pytest.fixture
def redis_down():
    """Redis offline — every call raises ConnectionError."""
    mock = AsyncMock()
    mock.get.side_effect = ConnectionError("Redis unavailable")
    mock.setex.side_effect = ConnectionError("Redis unavailable")
    mock.mget.side_effect = ConnectionError("Redis unavailable")
    mock.lrange.side_effect = ConnectionError("Redis unavailable")
    return mock
