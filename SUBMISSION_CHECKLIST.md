# Submission checklist

## Included in this package
- [x] React frontend (Overview, Inbox, Tickets, Audit Log, Knowledge Base, Settings)
- [x] FastAPI backend with Groq classifier and tool-calling agent
- [x] `get_order` and `search_faq` tools
- [x] Mock orders, FAQ, brand voice and 25 sample emails
- [x] CSV templates and local audit/ticket output implementation
- [x] n8n workflow JSON export (no secrets)
- [x] Backend regression tests
- [x] Four UI screenshots supplied during the conversation

## Must be completed on your accounts/machine before submission
- [ ] Add Groq key to `backend/.env`; verify `/health` returns `mode: groq`
- [ ] Run v1 on at least 10 emails and v2 on all 25 with Groq; inspect every output
- [ ] Complete `backend/TEST_REPORT.md` with measured per-email outcomes and metrics
- [ ] Create/share Google Sheet with exact `Audit Log` and `Tickets` tabs; verify all 25 audit rows
- [ ] Import and activate the n8n workflow; configure its FastAPI URL for your n8n hosting mode
- [ ] Capture `workflow.png`, `tickets.png`, and `audit_log.png` after final run
- [ ] Complete submission README details, including GitHub and Google Sheet links
- [ ] Record the 5-minute demo showing three emails end-to-end and one limitation
- [ ] Search repository and workflow export for secrets before pushing to GitHub
