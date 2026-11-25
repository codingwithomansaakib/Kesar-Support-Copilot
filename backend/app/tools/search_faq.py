from ..config import FAQ_FILE

def search_faq_tool(query: str) -> str:
    """Search the approved Kesar & Co. FAQ/policy source. This is the only policy/product source of truth."""
    text = FAQ_FILE.read_text(encoding="utf-8")
    terms = [t.lower() for t in query.split() if len(t) > 2]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    matches = []
    for p in paragraphs:
        score = sum(1 for t in terms if t in p.lower())
        if score:
            matches.append((score, p))
    matches.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join(p for _, p in matches[:5]) or "No matching FAQ information. Escalate to a human; do not guess."
