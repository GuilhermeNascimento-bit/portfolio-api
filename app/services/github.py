import asyncio
import json
from functools import partial

import requests

from app.config import settings
from app.services.cache import get_redis

CACHE_KEY = "github:data"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "portifolio-api/1.0",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _sync_fetch(username: str, token: str) -> dict:
    headers = {**HEADERS}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with requests.Session() as s:
        s.headers.update(headers)
        user = s.get(f"https://api.github.com/users/{username}", timeout=10).json()
        repos = s.get(
            f"https://api.github.com/users/{username}/repos",
            params={"sort": "updated", "per_page": 10},
            timeout=10,
        ).json()

    return {
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "repos": [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "language": r.get("language"),
                "stars": r["stargazers_count"],
                "url": r["html_url"],
                "updated_at": r["updated_at"],
            }
            for r in (repos if isinstance(repos, list) else [])
            if not r.get("fork")
        ][:6],
    }


async def fetch_github_data() -> dict:
    r = await get_redis()
    cached = await r.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, partial(_sync_fetch, settings.GITHUB_USERNAME, settings.GITHUB_TOKEN)
    )

    await r.setex(CACHE_KEY, settings.CACHE_TTL, json.dumps(data))
    return data
