# Kesar & Co. Support Copilot — Frontend

A React + Vite dashboard for the Kesar & Co. FastAPI support-copilot backend. It uses only the fictional assignment sample emails and mock orders; it does not connect to real customers or a live Shopify store. This package contains **frontend files only**; it does not duplicate or modify backend code.

## Features
- Overview with live metrics from the backend
- Email inbox with search, filters, per-email processing, classification and reply draft preview
- Batch processing of all 25 sample emails
- Tickets table
- Audit log table
- Knowledge base guidance and backend settings/status
- Responsive desktop and mobile layout
- Draft-only UI: no customer emails are sent from this frontend

## Requirements
- Node.js 20+ (recommended for current Vite releases)
- Existing Kesar backend running at `http://127.0.0.1:8000`

## Install and run

Open a terminal in this `frontend` folder:

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

In a second terminal, run the existing backend from the project root:

```bash
# Windows PowerShell
.venv\Scripts\activate
uvicorn app.main:app --reload
```

The Vite development server proxies `/api/*` to `http://127.0.0.1:8000/*`. No CORS changes are required for local development.

## Backend endpoints used
- `GET /health`
- `GET /emails`
- `GET /results`
- `GET /tickets`
- `POST /process`
- `POST /process-all`

## Notes
- The dashboard displays the real response data returned by the existing backend. Before processing, counts and tables remain empty rather than showing fabricated results.
- The **Process all emails** action calls the backend's `/process-all` endpoint. The backend clears its local audit/ticket output files before the batch run, as implemented in the supplied backend.
- API keys and Google credentials belong in the backend `.env` file only. Never place secrets in Vite environment variables or frontend source.
- `npm run build` creates a production bundle in `dist/`. The existing backend root route currently serves `frontend/index.html` directly; it does not yet mount Vite's `dist/assets` for production. Use the Vite dev server for local preview, or configure static serving when deploying.
