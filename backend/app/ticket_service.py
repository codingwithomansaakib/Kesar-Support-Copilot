
import csv
import json
from datetime import datetime
from .config import OUTPUT_DIR

TICKETS_FILE = OUTPUT_DIR / "tickets.json"
CSV_FILE = OUTPUT_DIR / "tickets.csv"

FIELDS = [
    "ticket_id", "created_at", "updated_at", "order_id",
    "customer_email", "email_ids", "intent", "priority",
    "status", "summary", "notes"
]


def _ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load():
    _ensure_output_dir()

    if not TICKETS_FILE.exists():
        return []

    try:
        data = json.loads(TICKETS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items):
    _ensure_output_dir()

    TICKETS_FILE.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for item in items:
            writer.writerow({
                "ticket_id": item.get("ticket_id", ""),
                "created_at": item.get("created_at", ""),
                "updated_at": item.get("updated_at", ""),
                "order_id": item.get("order_id", ""),
                "customer_email": item.get("customer_email", ""),
                "email_ids": ";".join(item.get("email_ids", [])),
                "intent": item.get("intent", ""),
                "priority": item.get("priority", "Normal"),
                "status": item.get("status", "Open"),
                "summary": item.get("summary", ""),
                "notes": " | ".join(item.get("notes", []))
            })


def get_all_tickets():
    return _load()


def upsert_ticket(email, classification, order,
                  priority="Normal", note=""):

    items = _load()

    order_id = (
        order.get("order_id") if order
        else classification.get("order_id")
    )

    existing = next(
        (
            ticket for ticket in items
            if order_id
            and ticket.get("order_id") == order_id
            and ticket.get("status") != "Closed"
        ),
        None
    )

    now = datetime.now().astimezone().isoformat()

    if existing:
        existing["updated_at"] = now

        if email["id"] not in existing["email_ids"]:
            existing["email_ids"].append(email["id"])

        if note:
            existing["notes"].append(note)

        existing["llm_summary"] = classification.get("summary", "")
        existing["summary"] = classification.get("summary", "")[:200]
        existing["intent"] = classification.get("intent", "")

        if priority == "High":
            existing["priority"] = "High"

        ticket = existing

    else:
        next_number = max(
            [
                int(t["ticket_id"].split("-")[1])
                for t in items
                if t.get("ticket_id", "").startswith("TKT-")
                and t["ticket_id"].split("-")[1].isdigit()
            ],
            default=0
        ) + 1

        summary = classification.get("summary", "")

        ticket = {
            "ticket_id": f"TKT-{next_number:03d}",
            "created_at": now,
            "updated_at": now,
            "order_id": order_id or "",
            "customer_email": (
                (email.get("from") or {}).get("email", "")
            ),
            "intent": classification.get("intent", ""),
            "priority": priority,
            "status": "Open",
            "summary": summary[:200],
            "llm_summary": summary,
            "email_ids": [email["id"]],
            "notes": [note] if note else []
        }

        items.append(ticket)

    _save(items)
    return ticket
