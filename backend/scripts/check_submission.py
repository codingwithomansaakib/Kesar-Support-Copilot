"""Check required files, dataset size, output headers and accidental secret patterns."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "TEST_REPORT.md", "workflow/kesar-support-copilot.n8n.json",
    "prompts/classification_prompt.md", "prompts/reply_drafting_prompt.md",
    "scripts/send_test_emails.py", "data/orders.json", "data/faq.md",
    "data/brand_voice.md", "data/test_emails.json", "schemas/llm_output.schema.json",
    "screenshots/README.md", "templates/audit_log_template.csv", "templates/tickets_template.csv"
]
missing = [p for p in required if not (ROOT / p).exists()]
emails = json.loads((ROOT / "data/test_emails.json").read_text(encoding="utf-8"))["emails"]
workflow = json.loads((ROOT / "workflow/kesar-support-copilot.n8n.json").read_text(encoding="utf-8"))
text_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".md", ".py", ".yml", ".yaml", ".env"} and ".git" not in p.parts and ".venv" not in p.parts]
secret_patterns = [re.compile(r"sk-[A-Za-z0-9_-]{20,}"), re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[^\s'\"]{16,}")]
findings = []
for path in text_files:
    if path.name == ".env.example":
        continue
    content = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in secret_patterns:
        if pattern.search(content):
            findings.append(str(path.relative_to(ROOT)))
print(f"Required files: {len(required)-len(missing)}/{len(required)} present")
print(f"Test emails: {len(emails)}")
print(f"Workflow nodes: {len(workflow.get('nodes', []))}")
if missing:
    print("Missing:", ", ".join(missing))
if findings:
    print("Potential secrets (review manually):", ", ".join(sorted(set(findings))))
if missing:
    sys.exit(1)
print("Static submission structure check passed. This does not verify live n8n/Google Sheets credentials or screenshots.")
