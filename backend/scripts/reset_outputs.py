"""Clear local run outputs before posting the 25 test emails to the n8n webhook."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for name in ("audit_log.csv", "tickets.csv", "tickets.json"):
    path = ROOT / "output" / name
    if path.exists():
        path.unlink()
print("Cleared output audit/ticket files. Ready for a fresh webhook test run.")
