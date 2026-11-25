from ..order_service import get_order, public_order_summary

def get_order_tool(order_id: str | None = None, customer_email: str | None = None):
    """Look up one order by explicit order ID, or by sender email when no ID is given."""
    order = get_order(order_id=order_id, customer_email=customer_email)
    return public_order_summary(order) if order else {"found": False, "message": "No unique matching order found."}
