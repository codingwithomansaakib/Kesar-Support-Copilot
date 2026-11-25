# Kesar & Co. — AI Order-Support Copilot

A draft-only support automation built from the fictional assignment data. It classifies incoming support emails, checks orders and FAQ facts, creates/upserts tickets, and writes an audit CSV. It never sends customer emails.

## Quick start

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

Add `GROQ_API_KEY` to `.env` to enable LLM classification and the tool-calling AI agent. Without a key, the app uses an explicitly labelled offline-demo classifier and deterministic draft responses; this is for local testing, not evidence of an LLM run.

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. Useful endpoints:
- `GET /health`
- `POST /process` — one email JSON
- `POST /process-all` — process all 25 supplied fictional emails
- `GET /results` — read audit output

Run batch v1/v2 and tests:

```bash
python scripts/run_batch.py
pytest -q
```

Batch outputs are saved under `reports/v1/` and `reports/v2/`; latest runtime files are in `output/`.

## Architecture

1. FastAPI accepts a webhook payload or batch input.
2. `classifier.py` asks the LLM for schema-constrained classification. It validates the JSON against the provided JSON Schema and retries once; if the LLM still fails, it returns a safe `other`/zero-confidence fallback that triggers human review.
3. `agent.py` implements a Groq function-calling agent with two tools: `get_order` and `search_faq`. The agent decides when to call them. In offline-demo mode, local deterministic draft logic is used instead.
4. `processor.py` enforces identity, confidence and risk gates; order details are only included when sender email matches the order email.
5. `policy_engine.py` evaluates return timing using each email's `received_at`, not the machine clock.
6. `ticket_service.py` creates one open ticket per order and updates it for follow-up messages.
7. `audit_service.py` writes one audit row per processed email.

## Safety decisions

- Confidence threshold: 0.80. Below this, route to human review.
- Complaints always create High-priority tickets and require human review before a remedy.
- Return/refund requests create tickets. Eligibility is never treated as refund approval.
- A return must be within 7 days of delivery and the item must be unused, unopened and sealed. Ambiguous conditions go to a human.
- Damaged/wrong/missing goods use the separate 48-hour photo verification path.
- Sender email must match the order's `customer_email` before order details are disclosed.
- Product and policy facts are sourced only from `data/faq.md`.
- Medical/safety topics are escalated. No medical advice or cure claims.
- Email bodies are untrusted data. Embedded instructions cannot override system policy.
- All responses are drafts; no email is sent.

## Google Sheets

The project always writes local `output/audit_log.csv` and `output/tickets.csv`. If Google credentials and a spreadsheet ID are configured, `sheets_sync.py` publishes both CSVs to the `Audit Log` and `Tickets` tabs. Without credentials, the local CSVs remain available and the API reports that Sheets sync is not configured.

## v1 vs v2

`run_batch.py` runs a deliberately basic baseline (v1) and the final pipeline (v2). Without `GROQ_API_KEY`, both use offline-demo mode; this is useful for reproducible local checks but does not demonstrate LLM quality. For an authentic LLM comparison, configure the key and run each version with the LLM enabled. Do not claim offline-demo results as model performance.

## Known limitations

- Google Sheets publishing needs user-created credentials and a destination spreadsheet; this build produces import-ready CSVs.
- The provided dataset has no photo bytes, only attachment filenames. Human review is required for photo verification.
- Order status and courier details are mock data, not live Shopify/courier APIs.
- Return eligibility is a conservative pre-check, not an approval.

## Web dashboard (frontend)

The project includes a React + Vite dashboard in the sibling `frontend/` folder. Start the backend on port 8000 and the frontend on port 5173 (see the root README). The dashboard includes Overview, Email inbox, Tickets, Audit log, Knowledge base and Settings views. It reads the supplied test emails and local CSV ledgers through the API. You can process one email or run the 25-email batch from the dashboard. The batch action resets the local audit and ticket output files before processing, so confirm before running it. The dashboard creates draft replies only; it does not send customer emails.

API documentation remains available at http://127.0.0.1:8000/docs.


## Groq API configuration

Copy `.env.example` to `.env`, add your Groq API key, and keep `.env` out of Git. The default model is `llama-3.3-70b-versatile`; confirm that it is available in your Groq account before running the final evaluation, and change `GROQ_MODEL` if needed. The backend uses Groq chat completions for classification and tool-assisted reply drafting. If the key is missing, it deliberately falls back to offline-demo mode.
