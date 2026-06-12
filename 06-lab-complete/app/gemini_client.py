"""Small Gemini REST client used to polish Day09 grounded answers."""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.config import settings


logger = logging.getLogger(__name__)


def _compact_json(value: Any, max_chars: int = 6000) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


class GeminiClient:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and settings.llm_provider.lower() == "gemini"

    def rewrite_day09_answer(
        self,
        question: str,
        draft_answer: str,
        route: dict[str, Any],
        policy: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> str | None:
        if not self.is_configured:
            return None

        prompt = f"""
Bạn là trợ lý chăm sóc khách hàng thương mại điện tử Day09.
Viết lại câu trả lời cuối bằng tiếng Việt tự nhiên, ngắn gọn, đúng trọng tâm.

Quy tắc bắt buộc:
- Chỉ dùng dữ liệu trong DRAFT_ANSWER và EVIDENCE.
- Không bịa chính sách, trạng thái đơn, voucher hoặc ngày tháng.
- Nếu thiếu dữ liệu, nói rõ cần thêm thông tin.
- Giữ phần Evidence ở cuối với các gạch đầu dòng quan trọng.

QUESTION:
{question}

DRAFT_ANSWER:
{draft_answer}

ROUTE:
{_compact_json(route)}

EVIDENCE:
{_compact_json({"policy": policy, "data": data})}
""".strip()

        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(self.model, safe='')}:generateContent"
            f"?key={urllib.parse.quote(self.api_key, safe='')}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 900,
            },
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            logger.warning(
                json.dumps(
                    {
                        "event": "gemini_http_error",
                        "status": exc.code,
                        "model": self.model,
                        "detail": detail[:800],
                    },
                    ensure_ascii=False,
                )
            )
            return None
        except Exception as exc:
            logger.warning(
                json.dumps(
                    {"event": "gemini_error", "model": self.model, "error": str(exc)},
                    ensure_ascii=False,
                )
            )
            return None

        candidates = body.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "\n".join(part.get("text", "") for part in parts).strip()
        return answer or None


gemini_client = GeminiClient()
