import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.schemas import validate_classification
from app.order_service import get_order
from app.policy_engine import evaluate_return

def test_order_lookup_by_id():
    assert get_order("KC-1041")["customer_email"] == "ananya.rao@example.com"

def test_order_lookup_by_email():
    assert get_order(customer_email="vikram.singh@example.com")["order_id"] == "KC-1044"

def test_schema_requires_all_required_fields():
    good = {"intent":"other","secondary_intent":None,"order_id":None,"sentiment":"neutral","language":"en","confidence":0.9,"summary":"Test"}
    assert validate_classification(good) == good

def test_unknown_email_return_requires_human():
    email = {"received_at":"2026-11-20T09:28:00+05:30","body":"Still sealed, unopened"}
    result = evaluate_return(email, None)
    assert result["eligible"] is None


def test_hindi_shipping_and_cod_question_is_product_query():
    from app.classifier import classify_email
    emails = json.loads((ROOT / "data" / "test_emails.json").read_text(encoding="utf-8"))["emails"]
    email = next(e for e in emails if e["id"] == "E09")
    classification, mode = classify_email(email, use_llm=False)
    assert classification["intent"] == "product_query"
    assert classification["language"] == "hi"
    assert mode == "offline_demo"


def test_prompt_injection_does_not_change_return_intent():
    from app.classifier import classify_email
    emails = json.loads((ROOT / "data" / "test_emails.json").read_text(encoding="utf-8"))["emails"]
    email = next(e for e in emails if e["id"] == "E12")
    classification, _ = classify_email(email, use_llm=False)
    assert classification["intent"] == "return_refund"
    assert classification["order_id"] == "KC-1055"


def test_medical_question_receives_non_cure_disclaimer():
    from app.classifier import classify_email
    from app.agent import draft_with_agent
    emails = json.loads((ROOT / "data" / "test_emails.json").read_text(encoding="utf-8"))["emails"]
    email = next(e for e in emails if e["id"] == "E20")
    classification, _ = classify_email(email, use_llm=False)
    draft, _ = draft_with_agent(email, classification, None, needs_human=True)
    assert "not intended to diagnose, treat or cure" in draft
    assert "consult a dermatologist or doctor" in draft


def test_follow_up_updates_existing_open_order_ticket(tmp_path, monkeypatch):
    from app import ticket_service
    monkeypatch.setattr(ticket_service, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(ticket_service, "TICKETS_FILE", tmp_path / "tickets.json")
    order = {"order_id": "KC-1052", "customer_email": "tanvi.desai@example.com"}
    classification = {"intent": "complaint", "sentiment": "negative", "summary": "Cracked jar"}
    first = {"id": "E04", "from": {"email": "tanvi.desai@example.com"}, "subject": "Damaged"}
    follow_up = {"id": "E21", "from": {"email": "tanvi.desai@example.com"}, "subject": "Follow-up"}
    created = ticket_service.upsert_ticket(first, classification, order, priority="High", note="Initial")
    updated = ticket_service.upsert_ticket(follow_up, classification, order, priority="High", note="Photos received")
    assert created["ticket_id"] == updated["ticket_id"] == "TKT-001"
    assert updated["email_ids"] == ["E04", "E21"]


def test_agent_order_tool_enforces_sender_ownership():
    from app.agent import _tool
    denied = _tool("get_order", {"order_id": "KC-1046", "customer_email": None}, "arjun.nair@example.com")
    allowed = _tool("get_order", {"order_id": "KC-1046", "customer_email": None}, "meera.iyer@example.com")
    assert denied["found"] is False
    assert allowed["found"] is True


def test_bridal_kit_return_requires_completeness_review():
    from app.policy_engine import evaluate_return
    emails = json.loads((ROOT / "data" / "test_emails.json").read_text(encoding="utf-8"))["emails"]
    email = next(e for e in emails if e["id"] == "E11")
    order = get_order("KC-1048")
    result = evaluate_return(email, order)
    assert result["eligible"] is None
    assert "complete set" in result["reason"]


def test_spouse_order_email_is_privacy_safe(monkeypatch):
    from app import processor
    emails = json.loads((ROOT / "data" / "test_emails.json").read_text(encoding="utf-8"))["emails"]
    email = next(e for e in emails if e["id"] == "E07")
    monkeypatch.setattr(processor, "append_audit", lambda row: None)
    result = processor.process_email(email, use_llm=False)
    assert result["needs_human"] is True
    assert "privacy" in result["draft_reply"].lower()
    assert "track.example.com" not in result["draft_reply"]
    assert "shipping_address" not in result["draft_reply"]


def test_missing_item_is_forced_to_complaint_even_if_model_says_refund(monkeypatch):
    from app import classifier
    monkeypatch.setattr(classifier, "GROQ_API_KEY", "")
    email = {"subject": "Missing item", "body": "The Aloe Calm Gel is missing from my order KC-1054. Please refund it.", "received_at": "2026-11-20T10:00:00+05:30", "from": {"email": "pooja.nair@example.com"}}
    result = classifier._apply_business_rule_guards(email, {"intent": "return_refund", "summary": "Missing product", "confidence": 0.85})
    assert result["intent"] == "complaint"


def test_offline_product_reply_uses_faq_source():
    from app.agent import deterministic_draft
    email = {"from": {"name": "Ishita"}, "subject": "Is serum vegan?", "body": "Is Saffron Glow serum vegan?"}
    classification = {"intent": "product_query"}
    draft = deterministic_draft(email, classification, None)
    assert "vegan" in draft.lower()
    assert "Saffron Glow" in draft
