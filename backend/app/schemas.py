import json
from jsonschema import Draft202012Validator
from .config import SCHEMA_FILE

_SCHEMA = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
_VALIDATOR = Draft202012Validator(_SCHEMA)

def validate_classification(data: dict) -> dict:
    errors = sorted(_VALIDATOR.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(f"{'.'.join(map(str, e.path))}: {e.message}" for e in errors)
        raise ValueError(details)
    return data

def safe_fallback() -> dict:
    return {
        "intent": "other",
        "secondary_intent": None,
        "order_id": None,
        "sentiment": "neutral",
        "language": "en",
        "confidence": 0.0,
        "summary": "Classification failed; human review required."
    }
