
import re

from .classifier import classify_email
from .order_service import get_order
from .agent import draft_with_agent
from .policy_engine import evaluate_return
from .ticket_service import upsert_ticket
from .audit_service import append_audit
from .config import CONFIDENCE_THRESHOLD


# Sensitive topics that must be escalated for human review.
RISK_TERMS = [
    "otp",
    "cvv",
    "password",
    "card pin",
    "threat",
    "legal notice",
    "police",
    "allergic reaction",
    "allergic",
    "eczema",
    "pregnancy",
    "side effect",
    "skin irritation",
]

ORDER_RELATED_INTENTS = {
    "order_status",
    "return_refund",
    "complaint",
}

TICKET_INTENTS = {
    "return_refund",
    "complaint",
}


def contains_risk_term(text: str) -> bool:
    """Check whether an email contains sensitive or safety-related terms."""
    text = (text or "").lower()

    for term in RISK_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text):
            return True

    return False


def get_sender_email(email: dict) -> str:
    """Safely extract the sender email address."""
    sender = email.get("from", {})

    if isinstance(sender, dict):
        return (sender.get("email") or "").strip().lower()

    if isinstance(sender, str):
        return sender.strip().lower()

    return ""


def process_email(email: dict, use_llm=True, version="v2"):
    """
    Process one customer email.

    Workflow:
    1. Classify customer intent.
    2. Find the relevant order.
    3. Verify sender ownership.
    4. Apply safety and return policies.
    5. Decide whether human review is required.
    6. Create or update support tickets.
    7. Generate a safe reply draft.
    8. Record the decision in the audit log.
    """

    email_id = email.get("id", "UNKNOWN")
    sender = get_sender_email(email)
    body = str(email.get("body", ""))
    body_lower = body.lower()

    # --------------------------------------------------
    # 1. CLASSIFICATION
    # --------------------------------------------------

    classification, mode = classify_email(
        email,
        use_llm=use_llm
    )

    intent = classification.get("intent", "other")
    confidence = float(classification.get("confidence", 0))

    reasons = []

    # --------------------------------------------------
    # 2. ORDER LOOKUP
    # --------------------------------------------------

    order = None
    order_id = classification.get("order_id")

    if order_id:
        order = get_order(order_id=order_id)

    elif intent in ORDER_RELATED_INTENTS and sender:
        order = get_order(customer_email=sender)

    # --------------------------------------------------
    # 3. CONFIDENCE CHECK
    # --------------------------------------------------

    if confidence < CONFIDENCE_THRESHOLD:
        reasons.append(
            f"Low classification confidence: "
            f"{confidence:.2f} < {CONFIDENCE_THRESHOLD:.2f}"
        )

    # --------------------------------------------------
    # 4. SENSITIVE CONTENT CHECK
    # --------------------------------------------------

    if contains_risk_term(body):
        reasons.append(
            "Sensitive safety, privacy, legal, or medical content"
        )

    # --------------------------------------------------
    # 5. ORDER VERIFICATION
    # --------------------------------------------------

    if intent in ORDER_RELATED_INTENTS and not order:
        reasons.append(
            "Order could not be verified using supplied order data"
        )

    # Verify that the sender owns the order.
    ownership_verified = True

    if order:
        order_customer = str(
            order.get("customer_email", "")
        ).strip().lower()

        if not sender or sender != order_customer:
            ownership_verified = False
            reasons.append(
                "Sender email does not match order customer; "
                "order privacy verification failed"
            )

    # --------------------------------------------------
    # 6. RETURN POLICY CHECK
    # --------------------------------------------------

    eligibility = None

    if intent == "return_refund":
        if order and ownership_verified:
            eligibility = evaluate_return(email, order)

            if eligibility.get("eligible") is not True:
                reasons.append(
                    eligibility.get(
                        "reason",
                        "Return or refund is not eligible under policy"
                    )
                )
        else:
            reasons.append(
                "Return/refund request requires verified order ownership"
            )

    # --------------------------------------------------
    # 7. COMPLAINT HANDLING
    # --------------------------------------------------

    if intent == "complaint":
        reasons.append(
            "Complaint requires human verification before remedy"
        )

    # --------------------------------------------------
    # 8. PRODUCT SAFETY QUESTIONS
    # --------------------------------------------------

    if intent == "product_query":
        medical_terms = [
            "eczema",
            "cure",
            "treat",
            "medical",
            "pregnan",
            "allerg",
            "side effect",
            "skin irritation",
        ]

        if any(term in body_lower for term in medical_terms):
            reasons.append(
                "Medical or product-safety question requires human review"
            )

    # --------------------------------------------------
    # 9. UNKNOWN / UNCLEAR EMAILS
    # --------------------------------------------------

    if intent == "other" and confidence < 0.80:
        reasons.append(
            "Unclear or non-standard customer enquiry"
        )

    # Spam and simple appreciation can be logged without
    # generating an unnecessary customer response.
    log_only = (
        intent == "other"
        and confidence >= 0.95
        and not reasons
    )

    # --------------------------------------------------
    # 10. HUMAN REVIEW DECISION
    # --------------------------------------------------

    needs_human = bool(reasons)

    # --------------------------------------------------
    # 11. CREATE OR UPDATE SUPPORT TICKET
    # --------------------------------------------------

    ticket = None

    if intent in TICKET_INTENTS:
        priority = (
            "High"
            if intent == "complaint"
            or classification.get("sentiment") == "angry"
            else "Normal"
        )

        ticket_note = "; ".join(reasons)

        if not ticket_note:
            ticket_note = (
                "Request requires policy verification "
                "before any customer remedy."
            )

        ticket = upsert_ticket(
            email,
            classification,
            order,
            priority=priority,
            note=ticket_note
        )

    # --------------------------------------------------
    # 12. SAFE ORDER DATA FOR AI AGENT
    # --------------------------------------------------

    safe_order = None

    if order and ownership_verified:
        safe_order = order

    # Never give unverified order information to the AI agent.
    draft, tools = draft_with_agent(
        email,
        classification,
        safe_order,
        needs_human
    )

    # --------------------------------------------------
    # 13. PRIVACY-SAFE RESPONSE
    # --------------------------------------------------

    if order and not ownership_verified:
        draft = (
            "Hi,\n\n"
            "For privacy and security reasons, we can share order "
            "details only with the email address used to place the "
            "order. Please ask the account holder to contact us "
            "from their registered email address.\n\n"
            "Warm regards,\n"
            "Team Kesar"
        )

    # Do not automatically promise a refund or replacement.
    if intent == "return_refund" and (
        not order
        or not ownership_verified
        or not eligibility
        or eligibility.get("eligible") is not True
    ):
        needs_human = True

    # Log-only messages do not need an unnecessary reply.
    if log_only:
        draft = ""

    # --------------------------------------------------
    # 14. DETERMINE FINAL ACTION
    # --------------------------------------------------

    if ticket:
        email_ids = ticket.get("email_ids", [])

        action_taken = (
            "ticket_updated"
            if len(email_ids) > 1
            else "ticket_created"
        )

    elif needs_human:
        action_taken = "needs_human"

    elif not draft:
        action_taken = "log_only"

    else:
        action_taken = "draft_reply"

    # --------------------------------------------------
    # 15. AUDIT LOG
    # --------------------------------------------------

    audit_record = {
        "email_id": email_id,
        "received_at": email.get("received_at", ""),
        "sender_email": sender,

        **classification,

        "needs_human": str(needs_human).lower(),
        "order_found": str(bool(order)).lower(),
        "ownership_verified": str(ownership_verified).lower(),

        "ticket_id": (
            ticket.get("ticket_id", "")
            if ticket else ""
        ),

        "action_taken": action_taken,
        "prompt_version": version,

        "notes": " | ".join(dict.fromkeys(reasons)),
        "draft_reply": draft or "",
    }

    append_audit(audit_record)

    # --------------------------------------------------
    # 16. RETURN RESULT TO API / FRONTEND
    # --------------------------------------------------

    return {
        "email_id": email_id,
        "classification": classification,
        "needs_human": needs_human,
        "human_reason": " | ".join(dict.fromkeys(reasons)),
        "order_found": bool(order),
        "ownership_verified": ownership_verified,
        "ticket": ticket,
        "draft_reply": draft or "",
        "action_taken": action_taken,
        "model_mode": mode,
    }

