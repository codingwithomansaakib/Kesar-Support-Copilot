# 5-minute screen-recording plan

Record the actual running setup. Do not claim a live LLM/Google Sheets run unless you have configured and demonstrated it.

| Time | Show | Suggested narration |
|---|---|---|
| 0:00–0:30 | Project folder and README | “This is a draft-only support copilot for the supplied fictional Kesar & Co. data.” |
| 0:30–1:20 | Full n8n canvas | Show webhook → FastAPI → human-review IF branch → webhook response branches. Explain that policy, tickets and audit logic run in FastAPI. |
| 1:20–2:10 | API docs and one order-status email (E01) | Run one email end-to-end and show the verified order status/tracking draft. |
| 2:10–3:00 | Product question (E09) and complaint (E04) | Show FAQ-grounded Guwahati/COD response and a complaint routed to human review with a ticket. |
| 3:00–3:45 | Prompt-injection case (E12) and follow-up (E21) | Show no refund auto-approval and the update of existing ticket TKT-002. |
| 3:45–4:30 | Google Sheet Audit Log and Tickets tabs | Show all 25 audit rows and ticket rows after a real sync. If not connected, say so honestly and show local CSVs instead. |
| 4:30–5:00 | TEST_REPORT and limitations | Explain that the offline run validates the deterministic pipeline; identify live LLM/Sheets integration as not yet verified if still true. |

Before recording, ensure the test data has been reset and that the run being shown is the run represented in `TEST_REPORT.md`. Keep API keys, service-account files and private credentials off screen.
