# Kesar & Co. — AI Order-Support Copilot

A draft-only AI support copilot built for the fictional Kesar & Co. assignment. It processes the supplied 25 sample emails and mock orders; it does **not** connect to real customer mailboxes, Shopify, courier services or live customer data.

## What it does

1. Classifies customer emails with Groq and validates the JSON against the supplied schema.
2. Uses a Groq tool-calling agent with `get_order` and `search_faq` tools.
3. Looks up orders from the read-only `backend/data/orders.json` dataset.
4. Grounds product/policy answers in `backend/data/faq.md` and follows `brand_voice.md`.
5. Creates or updates tickets for refund/return requests and complaints, avoiding duplicate open tickets for the same order.
6. Routes low-confidence, privacy, medical/safety, complaint and ambiguous cases to human review.
7. Writes one audit row per processed email and optionally syncs the CSVs to Google Sheets.
8. Shows results in the React dashboard. Replies are drafts only; no email is sent.

## Project structure

```text
backend/       FastAPI, Groq classifier/agent, tools, policies, CSV outputs
frontend/      React + Vite dashboard
workflow/      n8n webhook workflow export (no credentials/secrets)
docs/          assignment setup, demo and submission guidance
templates/     official CSV and README/report templates
prompts/       classification and drafting prompts
screenshots/   dashboard screenshots
```

## Run locally (Windows PowerShell)

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your own `GROQ_API_KEY` to `backend/.env`. Keep this file private; it is ignored by Git. Confirm the configured `GROQ_MODEL` is available to your Groq account.

```powershell
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend (second terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally http://localhost:5173. The Vite proxy forwards `/api/*` requests to the FastAPI server on port 8000.

### 3. Run tests and the assignment batch

In the backend terminal (with the virtual environment active):

```powershell
pytest -q
python scripts/run_batch.py
```

`run_batch.py` runs the deterministic baseline on the first 10 emails as v1 and the final pipeline on all 25 emails as v2. If `GROQ_API_KEY` is absent, v2 explicitly runs in offline-demo mode; do not present that as a Groq evaluation. After a successful Groq run, inspect `backend/reports/v2/` and complete `backend/TEST_REPORT.md` using measured results.

## Google Sheets

Create a spreadsheet named **Kesar Support** with tabs named exactly `Audit Log` and `Tickets`. Import the matching CSV templates from `templates/`. Configure a Google service-account JSON file and spreadsheet ID in `backend/.env`:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

Share the spreadsheet with the service account's email. Never commit the JSON credentials. The backend writes local CSVs first and syncs them when credentials are configured. Before submission, set the sheet to **Anyone with the link can view** and paste the view URL into your submission README.

## n8n workflow

Import `workflow/kesar-support-copilot.n8n.json` into n8n. The included workflow exposes a webhook, calls the FastAPI `/process` endpoint, branches on `needs_human`, and returns the result. The included URL `http://api:8000/process` is intended for the provided Docker Compose network. If you use n8n Cloud or another host, replace it with your reachable FastAPI base URL. Configure credentials in n8n or environment variables, never in exported workflow JSON.

For the Docker Compose setup, run from `backend/` with Docker installed:

```powershell
docker compose up --build
```

Then open n8n at http://localhost:5678 and import the workflow. The webhook path is `kesar-support-email`; activate the workflow and use its production webhook URL when testing.

## Safety and limitations

- Uses only the supplied fictional data and scenario date (20 November 2026). Date rules use each email's `received_at`.
- No real mailbox, Shopify or courier integration is included.
- No customer email is sent automatically.
- Refund decisions remain manual; eligibility checks are not refund approvals.
- Medical/safety questions and unclear or risky cases require human review.
- Photo evidence cannot be inspected because the supplied dataset contains attachment names, not image files.
- Google Sheets and n8n require your own account setup and activation before they are operational.

## Before submission

Follow `docs/SUBMISSION.md`. The reviewer expects a GitHub repository, exported workflow, Google Sheet view link with all 25 audit rows and tickets, screenshots of workflow/tickets/audit log, completed v1/v2 `TEST_REPORT.md`, README with the five product-thinking answers and AI-tools note, and a 5-minute recording showing three end-to-end emails (including one ticket) plus one limitation.

**Current package status:** source code, frontend, n8n workflow export, templates and local tests are included. You still need to configure your own Groq key, run the final 25-email Groq batch, configure/share Google Sheets, import/activate the n8n workflow, complete measured test results, and record the demo.


## Product-thinking answers (required)

### 1. Auto-send vs. draft
This prototype sends nothing automatically. Verified order-status and FAQ answers may be prepared as drafts when confidence is at least 0.80 and the sender identity is confirmed. Refunds, complaints, privacy mismatches, medical/safety questions, ambiguous records and low-confidence classifications stay with a human. The 0.80 threshold is an initial safety setting and should be tuned using reviewed outcomes.

### 2. Cost
The cost estimate must use the actual Groq model price and measured token usage. The calculation is: `per-email cost = (input tokens × input price + output tokens × output price) / 1,000,000`. At 1,000 emails/day, monthly volume is approximately 30,000 emails, so `monthly cost = per-email cost × 30,000`. Token usage is not currently persisted by this prototype, so a numeric cost would be an unsupported estimate; instrument token counts before presenting a rupee figure.

### 3. Week-one success metric
Track the percentage of AI drafts approved by a human without edits, segmented by intent. This measures usefulness while keeping a human in control. Pause the copilot immediately if there is a privacy leak, unsupported policy claim, unsafe medical claim or a material increase in incorrect drafts.

### 4. Failure experience
The customer receives no automatic email because the system is draft-only. A risky or uncertain case is marked `needs_human`, and the audit log records the reason. This limits harm from incorrect refund promises, disclosure of another customer's order or unsupported product advice.

### 5. Don't automate
Final refund approval and policy exceptions should remain manual. They involve money, evidence (such as photos and product condition) and customer context that may not exist in the mock order data.

## AI tools used
ChatGPT was used as a development assistant for planning, code drafting, debugging and reviewing the assignment requirements. Groq is the runtime LLM provider used by the application when `GROQ_API_KEY` is configured. All generated code and test results should be reviewed and verified by the candidate before submission.

## Submission links (fill before sending)
- GitHub repository: **add your repository URL**
- Google Sheet (view access): **add your Kesar Support URL**
- 5-minute recording: **add your Loom / Drive / unlisted YouTube URL**
