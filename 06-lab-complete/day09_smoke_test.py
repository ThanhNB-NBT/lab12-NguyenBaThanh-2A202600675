"""Smoke-test the embedded Day09 shopping assistant through FastAPI."""
from fastapi.testclient import TestClient

from app.main import app


CASES = [
    ("policy", "Chính sách hoàn trả hàng ra sao?"),
    ("order", "Đơn hàng 1971 bao giờ được giao?"),
    ("voucher", "Voucher của khách hàng C001 còn những mã nào dùng được?"),
    ("mixed", "Đơn hàng 1971 có được hoàn trả không?"),
    ("clarification", "Voucher của tôi còn dùng được không?"),
    ("not_found", "Kiểm tra đơn hàng 9999 giúp tôi"),
]


def main() -> None:
    headers = {"X-API-Key": "dev-key-change-me"}
    with TestClient(app) as client:
        for label, question in CASES:
            response = client.post(
                "/ask",
                headers=headers,
                json={"user_id": "day09-smoke", "question": question},
            )
            payload = response.json()
            first_line = payload.get("answer", "").splitlines()[0]
            route = payload.get("route", {})
            print(
                label,
                response.status_code,
                route.get("needs_policy"),
                route.get("needs_data"),
                route.get("status"),
                first_line,
            )


if __name__ == "__main__":
    main()
