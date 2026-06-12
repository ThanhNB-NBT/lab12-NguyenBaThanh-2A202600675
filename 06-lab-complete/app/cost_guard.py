"""Monthly LLM budget guard with Redis persistence and local fallback."""
import time
from dataclasses import dataclass

from fastapi import HTTPException

from app.config import settings


PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.00060


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS
    output_cost = output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS
    return input_cost + output_cost


@dataclass
class UsageSnapshot:
    month: str
    input_tokens: int
    output_tokens: int
    request_count: int
    cost_usd: float


class CostGuard:
    def __init__(self, monthly_budget_usd: float):
        self.monthly_budget_usd = monthly_budget_usd
        self._local: dict[str, dict[str, float | int]] = {}
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

    def check_budget(self, projected_cost_usd: float = 0.0) -> None:
        used = self.get_usage().cost_usd
        if used + projected_cost_usd > self.monthly_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Monthly budget exceeded",
                    "used_usd": round(used, 6),
                    "projected_usd": round(used + projected_cost_usd, 6),
                    "budget_usd": self.monthly_budget_usd,
                    "resets_at": "first day of next UTC month",
                },
            )

    def record_usage(self, input_tokens: int, output_tokens: int) -> UsageSnapshot:
        cost = estimate_cost_usd(input_tokens, output_tokens)
        month = time.strftime("%Y-%m")

        if self._redis:
            key = f"cost:{month}:global"
            pipe = self._redis.pipeline()
            pipe.hincrby(key, "input_tokens", input_tokens)
            pipe.hincrby(key, "output_tokens", output_tokens)
            pipe.hincrby(key, "request_count", 1)
            pipe.hincrbyfloat(key, "cost_usd", cost)
            pipe.expire(key, 60 * 60 * 24 * 45)
            pipe.execute()
        else:
            record = self._local.setdefault(
                month,
                {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "request_count": 0,
                    "cost_usd": 0.0,
                },
            )
            record["input_tokens"] += input_tokens
            record["output_tokens"] += output_tokens
            record["request_count"] += 1
            record["cost_usd"] += cost

        return self.get_usage()

    def get_usage(self) -> UsageSnapshot:
        month = time.strftime("%Y-%m")
        if self._redis:
            data = self._redis.hgetall(f"cost:{month}:global")
        else:
            data = self._local.get(month, {})

        return UsageSnapshot(
            month=month,
            input_tokens=int(float(data.get("input_tokens", 0))),
            output_tokens=int(float(data.get("output_tokens", 0))),
            request_count=int(float(data.get("request_count", 0))),
            cost_usd=float(data.get("cost_usd", 0.0)),
        )


cost_guard = CostGuard(monthly_budget_usd=settings.monthly_budget_usd)
