import ssl
from urllib.parse import urlparse

import redis.asyncio as redis

from app.config import settings

_client: redis.Redis | None = None


def _make_client() -> redis.Redis:
    url = urlparse(settings.REDIS_URL)
    use_ssl = settings.REDIS_URL.startswith("rediss://")

    kwargs: dict = {
        "host": url.hostname,
        "port": url.port or 6379,
        "password": url.password,
        "username": url.username or "default",
        "decode_responses": True,
    }

    if use_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl"] = True
        kwargs["ssl_context"] = ctx

    return redis.Redis(**kwargs)


async def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = _make_client()
    return _client
