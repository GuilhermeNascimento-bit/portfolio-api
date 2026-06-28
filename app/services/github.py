import json

import httpx

from app.config import settings
from app.services.cache import get_redis

CACHE_KEY = "github:data"


async def fetch_github_data() -> dict:
    r = await get_redis()
    cached = await r.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    headers = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        user_resp = await client.get(
            f"https://api.github.com/users/{settings.GITHUB_USERNAME}",
            headers=headers,
        )
        repos_resp = await client.get(
            f"https://api.github.com/users/{settings.GITHUB_USERNAME}/repos",
            headers=headers,
            params={"sort": "updated", "per_page": 10},
        )

    user = user_resp.json()
    repos = repos_resp.json() if isinstance(repos_resp.json(), list) else []

    data = {
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
            for r in repos
            if isinstance(r, dict) and not r.get("fork")
        ][:6],
    }

    await r.setex(CACHE_KEY, settings.CACHE_TTL, json.dumps(data))
    return data
