from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

SCENARIO_TODAY = "2026-11-20"
DATA_DIR = ROOT / "data"
ORDERS_FILE = DATA_DIR / "orders.json"
EMAILS_FILE = DATA_DIR / "test_emails.json"
FAQ_FILE = DATA_DIR / "faq.md"
BRAND_FILE = DATA_DIR / "brand_voice.md"
SCHEMA_FILE = ROOT / "schemas" / "llm_output.schema.json"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
