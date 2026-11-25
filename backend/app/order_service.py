import json
from .config import ORDERS_FILE

def all_orders():
    return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))["orders"]

def get_order(order_id: str | None = None, customer_email: str | None = None):
    orders = all_orders()
    if order_id:
        return next((o for o in orders if o["order_id"].lower() == order_id.lower()), None)
    if customer_email:
        matches = [o for o in orders if o["customer_email"].lower() == customer_email.lower()]
        return matches[0] if len(matches) == 1 else None
    return None

def public_order_summary(order: dict) -> dict:
    return {k: order.get(k) for k in (
        "order_id", "items", "total", "payment_method", "status", "courier",
        "tracking_url", "shipped_date", "estimated_delivery", "delivered_date",
        "cancelled_date", "refund_status"
    )}
