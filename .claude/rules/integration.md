---
paths:
  - "ledger/accounting_client.py"
  - "ledger/mcp_server.py"
---

# Integration

- Route all sandbox calls through `ledger/accounting_client.py` with explicit
  timeout, retry, and backoff.
- Log every non-2xx response with its request context.
- Never retry a write without an idempotency key.
- Read sandbox credentials from env only.
- When you discover a schema mismatch between our Pydantic model and the vendor
  payload, record it in `INTEGRATION.md` immediately. Never reconstruct it later.
- Verify endpoints, fields, and error codes against Intuit's QuickBooks Online
  API docs. Never recall them from memory.
