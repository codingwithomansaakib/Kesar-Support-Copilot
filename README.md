# Kesar & Co. — AI Order-Support Copilot

A draft-only AI support copilot built for the fictional Kesar & Co. assignment. It processes the supplied 25 sample emails and mock orders. It does **not** connect to real customer mailboxes, Shopify, courier services, or live customer data.

## 🎥 Project Demo Video

[▶ Watch Kesar & Co. AI Order-Support Copilot Demo](https://drive.google.com/file/d/1BR0Ss8EujQxm4BfxuaZEyymow00RPXpb/view?usp=drive_link)

## 🚀 What It Does

1. Classifies customer emails with Groq and validates JSON against the supplied schema.
2. Uses a Groq tool-calling agent with `get_order` and `search_faq` tools.
3. Looks up orders from the read-only `backend/data/orders.json` dataset.
4. Grounds product and policy answers in `backend/data/faq.md` and follows `brand_voice.md`.
5. Creates or updates tickets for refund/return requests and complaints, avoiding duplicate open tickets for the same order.
6. Routes low-confidence, privacy, medical/safety, complaint, and ambiguous cases to human review.
7. Writes one audit row per processed email and optionally syncs CSV files to Google Sheets.
8. Displays results in a React dashboard. Replies are drafts only; no email is sent.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| AI / LLM | Groq API |
| AI Agent | Tool Calling |
| Database / Mock Data | JSON |
| Data Logging | CSV |
| Spreadsheet Integration | Google Sheets |
| Workflow Automation | n8n |
| Testing | Pytest |
| Version Control | Git, GitHub |

## 📁 Project Structure

```text
Kesar-Support-Copilot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent.py
│   │   ├── classifier.py
│   │   ├── processor.py
│   │   ├── policy_engine.py
│   │   ├── order_service.py
│   │   ├── ticket_service.py
│   │   ├── audit_service.py
│   │   └── tools/
│   │
│   ├── data/
│   │   ├── orders.json
│   │   ├── faq.md
│   │   ├── brand_voice.md
│   │   └── test_emails.json
│   │
│   ├── prompts/
│   ├── schemas/
│   ├── scripts/
│   ├── tests/
│   ├── output/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
│
├── workflow/
│   └── kesar-support-copilot.n8n.json
│
├── docs/
├── templates/
├── screenshots/
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js and npm
- Git
- Groq API key
- VS Code (recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/codingwithomansaakib/Kesar-Support-Copilot.git
cd Kesar-Support-Copilot
```

### 2. Backend Setup

Open a terminal:

```powershell
cd backend

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
```

Add your Groq API key to `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
CONFIDENCE_THRESHOLD=0.75
```

Keep your `.env` file private. Never upload API keys or credentials to GitHub.

Start the FastAPI backend:

```powershell
uvicorn app.main:app --reload
```

Backend API:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### 3. Frontend Setup

Open a second terminal:

```powershell
cd frontend

npm install

npm run dev
```

Open the frontend:

http://localhost:5173

The Vite proxy forwards `/api/*` requests to the FastAPI backend running on port 8000.

### 4. Run Tests and Process Emails

From the backend directory, with the virtual environment activated:

```powershell
pytest -q
```

Run the assignment batch:

```powershell
python scripts/run_batch.py
```

The batch script runs the deterministic baseline on the first 10 emails as v1 and the final pipeline on all 25 emails as v2.

If the Groq API key is missing, v2 runs in offline-demo mode. Do not present offline-demo results as a Groq evaluation.

## 📊 Google Sheets Integration

Create a Google spreadsheet named **Kesar Support**.

Create two tabs with these exact names:

1. `Audit Log`
2. `Tickets`

Configure the following variables in `backend/.env`:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

Share the spreadsheet with your service account email.

The backend writes local CSV files first and syncs them when Google Sheets credentials are configured.

Never commit service-account credentials to GitHub.

## 🔄 n8n Workflow Integration

The project includes an n8n workflow export:

```text
workflow/kesar-support-copilot.n8n.json
```

The workflow:

1. Receives incoming email data through a webhook.
2. Calls the FastAPI `/process` endpoint.
3. Checks the `needs_human` field.
4. Routes the result according to the processing outcome.
5. Returns the processing result.

Import the workflow into your n8n instance.

The included `http://api:8000/process` URL is intended for the provided Docker Compose network. For n8n Cloud or another host, replace it with your reachable FastAPI URL.

The webhook path is:

```text
kesar-support-email
```

Configure credentials securely in n8n or environment variables.

## 🛡️ Safety and Limitations

- Uses only the supplied fictional assignment data and scenario date (20 November 2026).
- Does not connect to real customer mailboxes, Shopify, or courier services.
- Does not automatically send customer emails.
- Refund decisions remain manual.
- Eligibility checks are not refund approvals.
- Medical and safety-related questions require human review.
- Low-confidence and ambiguous cases are escalated.
- Privacy verification is applied before sharing order information.
- Photo evidence cannot be inspected because the supplied dataset contains attachment names, not image files.
- Google Sheets and n8n require separate account configuration and activation.

## 🧠 Product-Thinking Answers

### 1. Auto-Send vs. Draft

This prototype sends nothing automatically.

Verified order-status and FAQ answers may be prepared as drafts when confidence is at least 0.80 and the sender identity is confirmed.

Refunds, complaints, privacy mismatches, medical/safety questions, ambiguous records, and low-confidence classifications stay with a human.

The 0.80 threshold is an initial safety setting and should be tuned using reviewed outcomes.

### 2. Cost Estimation

The cost estimate must use the actual Groq model price and measured token usage.

Formula:

```text
Per-email cost =
(input tokens × input price + output tokens × output price)
÷ 1,000,000
```

At 1,000 emails per day:

```text
Monthly volume = 1,000 × 30 = 30,000 emails

Monthly cost = Per-email cost × 30,000
```

Token usage is not currently persisted by this prototype, so a numeric cost would be an unsupported estimate. Instrument token counts before presenting a rupee figure.

### 3. Week-One Success Metric

Track the percentage of AI drafts approved by a human without edits, segmented by intent.

This measures usefulness while keeping a human in control.

Pause the copilot immediately if there is a privacy leak, unsupported policy claim, unsafe medical claim, or a material increase in incorrect drafts.

### 4. Failure Experience

The customer receives no automatic email because the system is draft-only.

A risky or uncertain case is marked `needs_human`, and the audit log records the reason.

This limits harm from incorrect refund promises, disclosure of another customer's order, or unsupported product advice.

### 5. What Should Not Be Automated?

Final refund approval and policy exceptions should remain manual.

They involve money, evidence such as photos and product condition, and customer context that may not exist in the mock order data.

## 🤖 AI Tools Used

- **ChatGPT:** Used as a development assistant for project planning, code drafting, debugging, and reviewing assignment requirements.
- **Groq API:** Runtime LLM provider used by the application when `GROQ_API_KEY` is configured.

All generated code and test results should be reviewed and verified before submission.

## 📋 Before Submission

Follow `docs/SUBMISSION.md`.

The reviewer expects:

- [ ] GitHub repository
- [ ] Exported n8n workflow
- [ ] Google Sheet view link with all 25 audit rows and tickets
- [ ] Workflow screenshot
- [ ] Tickets screenshot
- [ ] Audit log screenshot
- [ ] Completed v1/v2 `TEST_REPORT.md`
- [ ] Five product-thinking answers
- [ ] AI tools used note
- [ ] Five-minute demo recording showing three end-to-end emails, including one ticket, and one limitation

## 🔗 Submission Links

**GitHub Repository:**

https://github.com/codingwithomansaakib/Kesar-Support-Copilot

**Project Demo Video:**

https://drive.google.com/file/d/1BR0Ss8EujQxm4BfxuaZEyymow00RPXpb/view?usp=drive_link

**Google Sheets (View Access):**

Add your Kesar Support spreadsheet URL here.

## 📌 Current Package Status

Source code, frontend, n8n workflow export, templates, and local tests are included.

Remaining tasks:

- Configure your own Groq API key.
- Run the final 25-email Groq batch.
- Configure and share Google Sheets.
- Import and activate the n8n workflow.
- Complete measured test results.
- Verify the demo recording and submission links.
