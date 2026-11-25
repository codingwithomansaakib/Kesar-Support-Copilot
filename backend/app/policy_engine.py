from datetime import datetime, date

def _received_date(email):
    return datetime.fromisoformat(email["received_at"]).date()

def _within_days(delivered_date, received_date, days=7):
    delivered = date.fromisoformat(delivered_date)
    return 0 <= (received_date - delivered).days <= days

def evaluate_return(email: dict, order: dict | None) -> dict:
    if not order:
        return {"eligible": None, "reason": "Order not found; human review required."}
    if order["status"] != "delivered" or not order.get("delivered_date"):
        return {"eligible": None, "reason": "Delivery status/date unavailable; human review required."}
    if not _within_days(order["delivered_date"], _received_date(email), 7):
        return {"eligible": False, "reason": "Outside the 7-day return window."}
    body = email.get("body", "").lower()
    if any(x in body for x in ["damaged", "cracked", "leaked", "wrong item", "missing item", "missing from", "spilled"]):
        return {"eligible": None, "reason": "Damaged/wrong/missing item follows the 48-hour photo verification process; human review required."}
    if any(x in body for x in ["used", "using", "didn't suit", "did not suit", "no difference", "didn't see results", "did not see results"]):
        return {"eligible": False, "reason": "Used/opened products or did-not-suit/did-not-see-results cases are not returnable."}
    is_kit = any("kit" in (item.get("name", "").lower()) for item in order.get("items", []))
    if is_kit:
        return {"eligible": None, "reason": "Combo/kit returns must include the complete set; human review is required to verify completeness."}
    if any(x in body for x in ["unopened", "sealed", "never opened", "seal intact"]):
        return {"eligible": True, "reason": "Within 7 days of delivery and customer states item is unopened/sealed; item condition must still be checked at pickup."}
    return {"eligible": None, "reason": "Usage/seal condition is not clear; human review required."}
