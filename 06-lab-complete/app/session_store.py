"""Small Redis-backed session store used to keep the app stateless."""
import json
import time

from app.config import settings


class SessionStore:
    def __init__(self):
        self._memory: dict[str, dict] = {}
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

    def ping(self) -> bool:
        if not self._redis:
            return self.storage == "memory"
        try:
            return bool(self._redis.ping())
        except Exception:
            return False

    def append_turn(self, session_id: str, question: str, answer: str) -> int:
        key = f"session:{session_id}"
        history = self.get_history(session_id)
        history.append(
            {
                "question": question,
                "answer": answer,
                "created_at": int(time.time()),
            }
        )
        history = history[-20:]

        if self._redis:
            self._redis.setex(key, settings.session_ttl_seconds, json.dumps(history))
        else:
            self._memory[key] = {"history": history}
        return len(history)

    def get_history(self, session_id: str) -> list[dict]:
        key = f"session:{session_id}"
        if self._redis:
            raw = self._redis.get(key)
            return json.loads(raw) if raw else []
        return self._memory.get(key, {}).get("history", [])


session_store = SessionStore()
