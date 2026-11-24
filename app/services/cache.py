from typing import Optional

import redis.asyncio as redis

from app.config import settings

_client: Optional[redis.Redis] = None


def _make_client() -> redis.Redis:
    # from_url understands both redis:// and rediss:// (TLS, used by Upstash),
    # and verifies the server certificate by default.
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = _make_client()
    return _client
