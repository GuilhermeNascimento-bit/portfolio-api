import datetime
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.services.cache import get_redis


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        try:
            r = await get_redis()
            bucket = datetime.datetime.utcnow().strftime("%Y%m%d%H")
            pipe = r.pipeline()
            pipe.incr(f"stats:req:{bucket}")
            pipe.expire(f"stats:req:{bucket}", 90000)  # 25h TTL
            pipe.lpush("stats:response_times", duration_ms)
            pipe.ltrim("stats:response_times", 0, 199)
            await pipe.execute()
        except Exception:
            pass

        return response
