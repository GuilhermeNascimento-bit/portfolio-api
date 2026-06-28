import datetime

from fastapi import APIRouter

from app.services.cache import get_redis

router = APIRouter()


@router.get("/stats")
async def get_stats():
    try:
        r = await get_redis()
        now = datetime.datetime.utcnow()
        keys = [
            f"stats:req:{(now - datetime.timedelta(hours=i)).strftime('%Y%m%d%H')}"
            for i in range(24)
        ]
        counts = await r.mget(keys)
        total_24h = sum(int(c) for c in counts if c)

        times = await r.lrange("stats:response_times", 0, -1)
        avg_ms = round(sum(float(t) for t in times) / len(times), 1) if times else 0

        return {"requests_24h": total_24h, "avg_response_ms": avg_ms}
    except Exception:
        return {"requests_24h": 0, "avg_response_ms": 0}
