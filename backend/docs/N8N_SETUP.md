# n8n setup

1. Start API + n8n using `docker compose up --build`.
2. Open n8n at `http://localhost:5678`.
3. Import `workflow/kesar-support-copilot.n8n.json`.
4. The HTTP Request node calls `http://api:8000/process` on the Docker Compose network. If using n8n Cloud, replace this with the publicly reachable HTTPS API endpoint. If n8n is in Docker but FastAPI runs on Windows host, use `http://host.docker.internal:8000/process`.
5. Save and activate the workflow. Use the webhook-test URL while listening for test events; use the production webhook URL for the sender script after activation.
6. First send a small subset: `python scripts/send_test_emails.py --url <WEBHOOK_URL> --only E01,E04,E21 --delay 5`.
7. For the full run, clear output files with `python scripts/reset_outputs.py`, then send all 25 emails with a five-second delay.
8. The API writes `output/audit_log.csv` and `output/tickets.csv`. Publish them to the Google Sheet using `python scripts/sync_google_sheets.py` after configuring the service account and sheet ID in `.env`.

The workflow contains no credentials. Store API keys and Google credentials in `.env` or n8n's credentials manager, never in exported node fields.
