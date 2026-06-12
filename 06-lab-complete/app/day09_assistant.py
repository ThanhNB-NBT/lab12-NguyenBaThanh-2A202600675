"""Lightweight Day09 shopping assistant for Railway deployment.

This module keeps the Day09 behavior deploy-friendly: it uses the real mock
policy and order/customer/voucher data, but avoids heavy LangGraph/Chroma
startup work inside the Day12 cloud service.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "day09_data"
ORDERS_PATH = DATA_DIR / "order_customer_mock_data.json"
POLICY_PATH = DATA_DIR / "policy_mock_vi.md"

ORDER_ID_RE = re.compile(r"\b(\d{3,6})\b")
CUSTOMER_ID_RE = re.compile(r"\b([Cc]\d{3})\b")


def _money(value: Any) -> str:
    try:
        return f"{int(value):,} VND".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def _short_items(order: dict) -> str:
    items = order.get("items") or []
    names = [str(item.get("product_name") or item.get("name") or "san pham") for item in items[:3]]
    return ", ".join(names) if names else "khong co danh sach san pham"


def _parse_policy_sections(markdown: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_h2 = ""
    current_h3 = ""
    lines: list[str] = []

    def flush() -> None:
        nonlocal lines
        content = "\n".join(lines).strip()
        if current_h2 and (content or current_h3):
            citation = f"{current_h2} > {current_h3}" if current_h3 else current_h2
            sections.append(
                {
                    "citation": citation,
                    "h2": current_h2,
                    "h3": current_h3,
                    "content": content,
                    "text": f"{current_h2}\n{current_h3}\n{content}".strip(),
                }
            )
        lines = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            current_h2 = line[3:].strip()
            current_h3 = ""
        elif line.startswith("### "):
            flush()
            current_h3 = line[4:].strip()
        elif line.startswith("# "):
            continue
        else:
            lines.append(raw_line)
    flush()
    return sections


@lru_cache(maxsize=1)
def get_day09_assistant() -> "Day09ShoppingAssistant":
    return Day09ShoppingAssistant()


class Day09ShoppingAssistant:
    def __init__(self) -> None:
        data = json.loads(ORDERS_PATH.read_text(encoding="utf-8"))
        self.metadata = data.get("metadata", {})
        self.customers = data.get("customers", [])
        self.orders = data.get("orders", [])
        self.vouchers = data.get("vouchers", [])
        self.customer_by_id = {str(c.get("customer_id")): c for c in self.customers}
        self.order_by_id = {str(o.get("order_id")): o for o in self.orders}
        self.orders_by_customer_id: dict[str, list[dict]] = {}
        for order in self.orders:
            self.orders_by_customer_id.setdefault(str(order.get("customer_id")), []).append(order)
        self.vouchers_by_customer_id: dict[str, list[dict]] = {}
        for voucher in self.vouchers:
            self.vouchers_by_customer_id.setdefault(str(voucher.get("customer_id")), []).append(voucher)

        markdown = POLICY_PATH.read_text(encoding="utf-8")
        self.policy_sections = _parse_policy_sections(markdown)

    def answer(self, question: str) -> dict[str, Any]:
        route = self._route(question)
        if route["status"] == "clarification_needed":
            return {
                "answer": f"Status: clarification_needed\nQuestion: {route['clarification_question']}",
                "route": route,
                "policy": None,
                "data": None,
                "mode": "day09-shopping-assistant",
            }

        data_result = self._lookup_data(route) if route["needs_data"] else None
        policy_result = self._lookup_policy(question, route, data_result) if route["needs_policy"] else None

        if data_result and data_result.get("status") == "not_found" and not route["needs_policy"]:
            missing = data_result.get("missing") or "du lieu yeu cau"
            return {
                "answer": f"Status: not_found\nMessage: Khong tim thay {missing}.",
                "route": route,
                "policy": policy_result,
                "data": data_result,
                "mode": "day09-shopping-assistant",
            }

        final = self._compose_answer(question, route, policy_result, data_result)
        return {
            "answer": final,
            "route": route,
            "policy": policy_result,
            "data": data_result,
            "mode": "day09-shopping-assistant",
        }

    def _route(self, question: str) -> dict[str, Any]:
        lower = question.lower()
        order_id = self._extract_order_id(question)
        customer_id = self._extract_customer_id(question)

        asks_voucher = "voucher" in lower or "ma giam" in lower or "mã giảm" in lower
        asks_order = any(token in lower for token in ["don hang", "đơn hàng", "order", "giao", "trang thai", "trạng thái"])
        asks_return = any(token in lower for token in ["hoan tra", "hoàn trả", "tra hang", "trả hàng", "doi y", "đổi ý"])
        asks_policy = any(
            token in lower
            for token in [
                "chinh sach",
                "chính sách",
                "bao lau",
                "bao lâu",
                "kiem hang",
                "kiểm hàng",
                "khong ho tro",
                "không hỗ trợ",
                "giao nhanh",
                "tieu chuan",
                "tiêu chuẩn",
                "huy don",
                "hủy đơn",
            ]
        )

        if asks_voucher and not customer_id and not order_id:
            return {
                "status": "clarification_needed",
                "needs_policy": False,
                "needs_data": False,
                "order_id": None,
                "customer_id": None,
                "clarification_question": "Anh/chị vui lòng cung cấp mã khách hàng, ví dụ C001, để em kiểm tra voucher chính xác.",
            }

        if asks_return and asks_order and not order_id:
            return {
                "status": "clarification_needed",
                "needs_policy": False,
                "needs_data": False,
                "order_id": None,
                "customer_id": customer_id,
                "clarification_question": "Anh/chị vui lòng cung cấp mã đơn hàng để em kiểm tra điều kiện hoàn trả.",
            }

        needs_data = bool(order_id or customer_id)
        needs_policy = asks_policy or (asks_return and bool(order_id))
        if not needs_data and not needs_policy:
            needs_policy = True

        return {
            "status": "ok",
            "needs_policy": needs_policy,
            "needs_data": needs_data,
            "order_id": order_id,
            "customer_id": customer_id,
            "clarification_question": None,
        }

    def _extract_order_id(self, question: str) -> str | None:
        match = ORDER_ID_RE.search(question)
        return match.group(1) if match else None

    def _extract_customer_id(self, question: str) -> str | None:
        match = CUSTOMER_ID_RE.search(question)
        return match.group(1).upper() if match else None

    def _lookup_data(self, route: dict[str, Any]) -> dict[str, Any]:
        order_id = route.get("order_id")
        customer_id = route.get("customer_id")
        if order_id:
            order = self.order_by_id.get(str(order_id))
            if not order:
                return {"status": "not_found", "missing": f"don hang {order_id}", "order_id": order_id}
            customer = self.customer_by_id.get(str(order.get("customer_id")))
            vouchers = self.vouchers_by_customer_id.get(str(order.get("customer_id")), [])
            return {"status": "ok", "order": order, "customer": customer, "vouchers": vouchers}

        if customer_id:
            customer = self.customer_by_id.get(str(customer_id))
            if not customer:
                return {"status": "not_found", "missing": f"khach hang {customer_id}", "customer_id": customer_id}
            orders = sorted(
                self.orders_by_customer_id.get(customer_id, []),
                key=lambda item: item.get("created_at", ""),
                reverse=True,
            )
            vouchers = self.vouchers_by_customer_id.get(customer_id, [])
            return {"status": "ok", "customer": customer, "orders": orders[:10], "vouchers": vouchers}

        return {"status": "not_found", "missing": "ma don hang hoac ma khach hang"}

    def _lookup_policy(
        self,
        question: str,
        route: dict[str, Any],
        data_result: dict[str, Any] | None,
    ) -> dict[str, Any]:
        lower = question.lower()
        keywords: list[str] = []
        if any(token in lower for token in ["hoan tra", "hoàn trả", "tra hang", "trả hàng", "doi y", "đổi ý"]):
            keywords.extend(["trả hàng", "hoàn tiền", "15 ngày", "eligible_for_return_until"])
        if any(token in lower for token in ["giao", "delivery", "tieu chuan", "tiêu chuẩn", "giao nhanh"]):
            keywords.extend(["giao hàng", "thời gian giao", "giao nhanh", "tiêu chuẩn"])
        if "voucher" in lower:
            keywords.extend(["voucher", "hoàn lại", "hạng khách hàng"])
        if any(token in lower for token in ["kiem hang", "kiểm hàng"]):
            keywords.extend(["kiểm hàng", "nhận"])
        if not keywords:
            keywords = lower.split()

        scored = []
        for section in self.policy_sections:
            haystack = section["text"].lower()
            score = sum(1 for keyword in keywords if keyword.lower() in haystack)
            if score:
                scored.append((score, section))
        scored.sort(key=lambda item: item[0], reverse=True)
        hits = [section for _, section in scored[:3]]
        if not hits:
            hits = self.policy_sections[:2]

        return {
            "status": "ok",
            "citations": [hit["citation"] for hit in hits],
            "snippets": [self._trim(hit["content"], 500) for hit in hits],
        }

    def _compose_answer(
        self,
        question: str,
        route: dict[str, Any],
        policy_result: dict[str, Any] | None,
        data_result: dict[str, Any] | None,
    ) -> str:
        lower = question.lower()
        lines = ["Answer:"]

        if data_result and data_result.get("status") == "ok":
            if order := data_result.get("order"):
                lines.extend(self._answer_order(question, lower, order))
            elif customer := data_result.get("customer"):
                lines.extend(self._answer_customer(question, lower, customer, data_result))

        if policy_result and not data_result:
            lines.append(self._answer_policy(lower, policy_result))

        if policy_result and data_result and data_result.get("order"):
            order = data_result["order"]
            if any(token in lower for token in ["hoan tra", "hoàn trả", "tra hang", "trả hàng", "doi y", "đổi ý"]):
                can_return = bool(order.get("can_return_now"))
                if can_return:
                    lines.append(
                        f"Đơn {order.get('order_id')} có thể còn đủ điều kiện hoàn/trả theo dữ liệu hiện tại; hạn hỗ trợ là {order.get('eligible_for_return_until')}."
                    )
                else:
                    lines.append(
                        f"Đơn {order.get('order_id')} chưa thể/không thể hoàn trả ngay theo dữ liệu hiện tại. Trạng thái đơn là {order.get('order_status')} và cờ can_return_now={order.get('can_return_now')}."
                    )

        if len(lines) == 1:
            lines.append("Em đã nhận câu hỏi và sẽ hỗ trợ theo dữ liệu mua sắm Day09.")

        lines.append("")
        lines.append("Evidence:")
        if policy_result:
            for citation in policy_result["citations"]:
                lines.append(f"- Policy: {citation}")
        if data_result:
            if order := data_result.get("order"):
                lines.append(
                    f"- Order data: order_id={order.get('order_id')}, status={order.get('order_status')}, estimated_delivery={order.get('estimated_delivery')}, can_return_now={order.get('can_return_now')}"
                )
            if customer := data_result.get("customer"):
                lines.append(
                    f"- Customer data: customer_id={customer.get('customer_id')}, tier={customer.get('tier')}, remaining_voucher_quota={customer.get('remaining_voucher_quota_this_month')}"
                )
            if "vouchers" in data_result:
                active = [v for v in data_result["vouchers"] if v.get("status") == "active" and int(v.get("remaining_uses", 0)) > 0]
                lines.append(f"- Voucher data: active_usable_vouchers={len(active)}")
        return "\n".join(lines)

    def _answer_order(self, question: str, lower: str, order: dict) -> list[str]:
        order_id = order.get("order_id")
        if any(token in lower for token in ["bao gio", "bao giờ", "giao", "delivery"]):
            return [
                f"Đơn hàng {order_id} đang ở trạng thái {order.get('order_status')}.",
                f"Ngày giao dự kiến: {order.get('estimated_delivery')}.",
                f"Sản phẩm chính: {_short_items(order)}.",
            ]
        if any(token in lower for token in ["trang thai", "trạng thái"]):
            return [f"Đơn hàng {order_id} hiện có trạng thái {order.get('order_status')}."]
        return [
            f"Đơn hàng {order_id}: trạng thái {order.get('order_status')}, tổng tiền {_money(order.get('final_total'))}, giao dự kiến {order.get('estimated_delivery')}."
        ]

    def _answer_customer(
        self,
        question: str,
        lower: str,
        customer: dict,
        data_result: dict[str, Any],
    ) -> list[str]:
        customer_id = customer.get("customer_id")
        if "voucher" in lower:
            vouchers = data_result.get("vouchers", [])
            active = [v for v in vouchers if v.get("status") == "active" and int(v.get("remaining_uses", 0)) > 0]
            codes = ", ".join(v.get("voucher_code", "") for v in active[:8]) or "không có mã active còn lượt dùng"
            return [
                f"Khách hàng {customer_id} thuộc hạng {customer.get('tier')}.",
                f"Quota voucher còn lại tháng này: {customer.get('remaining_voucher_quota_this_month')}/{customer.get('max_voucher_per_month')}.",
                f"Các voucher còn dùng được: {codes}.",
            ]
        orders = data_result.get("orders", [])
        order_ids = ", ".join(str(o.get("order_id")) for o in orders[:8]) or "không có đơn gần đây"
        return [
            f"Khách hàng {customer_id} thuộc hạng {customer.get('tier')}, tổng đơn {customer.get('total_orders')}.",
            f"Các đơn gần đây: {order_ids}.",
        ]

    def _answer_policy(self, lower: str, policy_result: dict[str, Any]) -> str:
        joined = "\n".join(policy_result.get("snippets", []))
        if any(token in lower for token in ["hoan tra", "hoàn trả", "tra hang", "trả hàng"]):
            return "Chính sách hoàn/trả cho phép gửi yêu cầu khi còn trong thời hạn hỗ trợ; thông thường tối đa 15 ngày từ khi đơn giao thành công, tùy ngành hàng và điều kiện sản phẩm."
        if any(token in lower for token in ["giao", "delivery", "tieu chuan", "tiêu chuẩn"]):
            return "Giao tiêu chuẩn thường phụ thuộc khu vực: nội thành 1-2 ngày, liên tỉnh 2-4 ngày, vùng xa 3-7 ngày; đơn có thể cộng thêm thời gian nếu hàng cồng kềnh hoặc cần kiểm tra."
        if "voucher" in lower:
            return "Voucher có thể có điều kiện về loại voucher, thời hạn, số lượt dùng, hạn mức theo hạng khách hàng và khả năng hoàn lại khi hủy đơn."
        if any(token in lower for token in ["kiem hang", "kiểm hàng"]):
            return "Khách được khuyến nghị kiểm tra ngoại quan gói hàng khi nhận và báo ngay nếu phát hiện móp, vỡ, thiếu phụ kiện hoặc sai sản phẩm."
        return self._trim(joined, 700)

    def _trim(self, text: str, max_chars: int) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."
