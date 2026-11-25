
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any
import csv
import json

from .processor import process_email
from .config import EMAILS_FILE, OUTPUT_DIR, GROQ_API_KEY
from .sheets_sync import sync_csv_tabs
from .ticket_service import get_all_tickets


app = FastAPI(
    title="Kesar & Co. AI Order-Support Copilot",
    version="1.2.0",
    description="Draft-only support automation using the supplied assignment data."
)


# -----------------------------
# Request Schema
# -----------------------------

class EmailPayload(BaseModel):
    id: str
    received_at: str
    from_: dict[str, Any] = Field(alias="from")
    subject: str
    body: str
    attachments: list[str] = Field(default_factory=list)


# -----------------------------
# Helper Functions
# -----------------------------

def sync_sheets_safely():
    try:
        return sync_csv_tabs()
    except Exception as exc:
        return {
            "synced": False,
            "reason": f"Google Sheets sync failed: {type(exc).__name__}"
        }


def read_csv_rows(filename: str):
    path = OUTPUT_DIR / filename

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except Exception:
        return []


def load_emails():
    try:
        data = json.loads(EMAILS_FILE.read_text(encoding="utf-8"))

        if isinstance(data, dict):
            return data.get("emails", [])

        if isinstance(data, list):
            return data

        return []

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load sample emails: {exc}"
        )


# -----------------------------
# Root & Health APIs
# -----------------------------

@app.get("/")
def root():
    return {
        "name": "Kesar & Co. AI Order-Support Copilot",
        "status": "running",
        "version": "1.2.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": "groq" if GROQ_API_KEY else "offline-demo",
        "data_source": "assignment_sample_data"
    }


# -----------------------------
# Emails API
# -----------------------------

@app.get("/emails")
def get_emails():
    emails = load_emails()

    return {
        "success": True,
        "count": len(emails),
        "emails": emails
    }


# -----------------------------
# Audit Results API
# -----------------------------

@app.get("/results")
def get_results():
    rows = read_csv_rows("audit_log.csv")

    return {
        "success": True,
        "processed": len(rows),
        "count": len(rows),
        "rows": rows
    }


# -----------------------------
# Tickets API
# -----------------------------

@app.get("/tickets")
def get_tickets():
    try:
        tickets = get_all_tickets()

        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets,
            "rows": tickets
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load tickets: {exc}"
        )


# -----------------------------
# Process Single Email
# -----------------------------

@app.post("/process")
def process_single_email(payload: EmailPayload):
    try:
        email = payload.model_dump(by_alias=True)

        result = process_email(email)

        sheet_sync = sync_sheets_safely()

        return {
            "success": True,
            "result": result,
            "sheets_sync": sheet_sync
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Email processing failed: {exc}"
        )


# -----------------------------
# Process All Emails
# -----------------------------

@app.post("/process-all")
def process_all_emails():
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Start a fresh, reproducible assignment run.
        for filename in (
            "audit_log.csv",
            "tickets.csv",
            "tickets.json"
        ):
            path = OUTPUT_DIR / filename

            if path.exists():
                path.unlink()

        emails = load_emails()
        results = []

        for email in emails:
            results.append(process_email(email))

        sheet_sync = sync_sheets_safely()

        tickets = get_all_tickets()
        audit_rows = read_csv_rows("audit_log.csv")

        return {
            "success": True,
            "processed": len(results),
            "results": results,
            "audit_records": len(audit_rows),
            "ticket_count": len(tickets),
            "tickets": tickets,
            "sheets_sync": sheet_sync
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {exc}"
        )
