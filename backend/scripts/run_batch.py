import json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.processor import process_email
from app.config import EMAILS_FILE, OUTPUT_DIR, GROQ_API_KEY

def reset_outputs():
    for name in ["audit_log.csv", "tickets.csv", "tickets.json"]:
        p = OUTPUT_DIR / name
        if p.exists():
            p.unlink()

def run(version, use_llm, limit=None):
    reset_outputs()
    emails = json.loads(EMAILS_FILE.read_text(encoding="utf-8"))["emails"]
    if limit is not None:
        emails = emails[:limit]
    results = [process_email(e, use_llm=use_llm, version=version) for e in emails]
    dest = ROOT / "reports" / version
    dest.mkdir(parents=True, exist_ok=True)
    for name in ["audit_log.csv", "tickets.csv", "tickets.json"]:
        p = OUTPUT_DIR / name
        if p.exists():
            shutil.copy2(p, dest / name)
    (dest / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return results

if __name__ == "__main__":
    # v1 is a 10-email deterministic baseline; v2 is the full 25-email final run.
    # With GROQ_API_KEY set, v2 uses Groq. Without it, v2 is explicitly offline-demo mode.
    v1 = run("v1", use_llm=False, limit=10)
    v2 = run("v2", use_llm=True, limit=None)
    print(f"v1 processed {len(v1)} emails; v2 processed {len(v2)} emails.")
    print(f"Groq configured: {bool(GROQ_API_KEY)}")
    print("Artifacts: reports/v1 and reports/v2")
