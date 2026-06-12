"""Redis-backed sliding-window rate limiter with local fallback."""
import time
import uuid
from collections import defaultdict, deque

from fastapi import HTTPException

from app.config import settings


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._local_windows: dict[str, deque[float]] = defaultdict(deque)
        self._redis = None
        self.storage = "memory"

        if settings.redis_url:
            try:
                import redis

                client = redis.from_url(settings.redis_url, decode_responses=True)
                client.ping()
                self._redis = client
                self.storage = "redis"
            except Exception:
                self._redis = None

    def check(self, bucket: str) -> dict:
        if self._redis:
            return self._check_redis(bucket)
        return self._check_memory(bucket)

    def _check_redis(self, bucket: str) -> dict:
        now = time.time()
        window_start = now - self.window_seconds
        key = f"rate:{bucket}"
        member = f"{now}:{uuid.uuid4().hex}"

        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {member: now})
        pipe.zcard(key)
        pipe.expire(key, self.window_seconds * 2)
        _, _, count, _ = pipe.execute()

        if count > self.limit:
            self._redis.zrem(key, member)
            retry_after = self._retry_after_redis(key, now)
            raise self._limit_error(retry_after)

        return {
            "limit": self.limit,
            "remaining": max(0, self.limit - count),
            "reset_after_seconds": self.window_seconds,
            "storage": self.storage,
        }

    def _retry_after_redis(self, key: str, now: float) -> int:
        oldest = self._redis.zrange(key, 0, 0, withscores=True)
        if not oldest:
            return self.window_seconds
        return max(1, int(oldest[0][1] + self.window_seconds - now) + 1)

    def _check_memory(self, bucket: str) -> dict:
        now = time.time()
        window = self._local_windows[bucket]

        while window and window[0] < now - self.window_seconds:
            window.popleft()

        if len(window) >= self.limit:
            retry_after = max(1, int(window[0] + self.window_seconds - now) + 1)
            raise self._limit_error(retry_after)

        window.append(now)
        return {
            "limit": self.limit,
            "remaining": max(0, self.limit - len(window)),
            "reset_after_seconds": self.window_seconds,
            "storage": self.storage,
        }

    def _limit_error(self, retry_after: int) -> HTTPException:
        return HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": self.limit,
                "window_seconds": self.window_seconds,
                "retry_after_seconds": retry_after,
            },
            headers={
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(retry_after),
            },
        )


rate_limiter = SlidingWindowRateLimiter(
    limit=settings.rate_limit_per_minute,
    window_seconds=60,
)
