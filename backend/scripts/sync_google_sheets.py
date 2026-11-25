import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.sheets_sync import sync_csv_tabs
print(sync_csv_tabs())
