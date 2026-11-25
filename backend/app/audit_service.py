import csv
from datetime import datetime
from .config import OUTPUT_DIR

# Exact column order from the assignment's audit_log_template.csv.
FIELDS = [
    "email_id", "received_at", "from_email", "intent", "secondary_intent", "order_id",
    "language", "sentiment", "confidence", "order_found", "action_taken", "needs_human",
    "ticket_id", "reply_draft", "prompt_version", "processed_at", "error", "notes"
]


def append_audit(row):
    path = OUTPUT_DIR / "audit_log.csv"
    exists = path.exists() and path.stat().st_size > 0
    normalized = {
        "email_id": row.get("email_id", ""),
        "received_at": row.get("received_at", ""),
        "from_email": row.get("sender_email", ""),
        "intent": row.get("intent", ""),
        "secondary_intent": row.get("secondary_intent", ""),
        "order_id": row.get("order_id", "") or "",
        "language": row.get("language", ""),
        "sentiment": row.get("sentiment", ""),
        "confidence": row.get("confidence", ""),
        "order_found": row.get("order_found", "false"),
        "action_taken": row.get("action_taken", ""),
        "needs_human": row.get("needs_human", "false"),
        "ticket_id": row.get("ticket_id", ""),
        "reply_draft": row.get("draft_reply", ""),
        "prompt_version": row.get("prompt_version", "v2"),
        "processed_at": datetime.now().astimezone().isoformat(),
        "error": row.get("error", ""),
        "notes": row.get("notes", "")
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(normalized)
