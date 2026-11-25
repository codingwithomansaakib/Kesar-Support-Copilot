"""Optional Google Sheets publisher for the generated CSV tabs."""
import csv
from pathlib import Path
from .config import OUTPUT_DIR, GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID


def sync_csv_tabs():
    if not GOOGLE_SERVICE_ACCOUNT_FILE or not GOOGLE_SHEET_ID:
        return {"synced": False, "reason": "Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_SHEET_ID first."}
    try:
        import gspread
    except ImportError as exc:
        return {"synced": False, "reason": f"Install gspread: {exc}"}
    gc = gspread.service_account(filename=GOOGLE_SERVICE_ACCOUNT_FILE)
    spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
    results = {}
    for filename, tab_name in [("audit_log.csv", "Audit Log"), ("tickets.csv", "Tickets")]:
        path = OUTPUT_DIR / filename
        if not path.exists():
            results[tab_name] = "skipped: CSV not found"
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        try:
            worksheet = spreadsheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=tab_name, rows=max(100, len(rows)+10), cols=max(12, len(rows[0]) if rows else 12))
        worksheet.clear()
        if rows:
            worksheet.update(range_name="A1", values=rows, value_input_option="RAW")
        results[tab_name] = f"uploaded {max(0, len(rows)-1)} rows"
    return {"synced": True, "tabs": results}
