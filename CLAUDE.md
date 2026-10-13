# Ledger

Invoice-processing agent. Python 3.12, uv, FastAPI, Pydantic v2, Postgres.
Test: `uv run pytest`  Typecheck: `uv run mypy --strict .`  Lint: `uv run ruff check .`  Format: `uv run ruff format --check .`

## Routing
`.claude/rules/DECISIONS.md` and `.claude/rules/verify.md` have no `paths`
frontmatter, so they load automatically every session.
`python.md`, `evals.md`, and `integration.md` are path-scoped and load when a
matching file is *read*. Path-scoped rules don't reliably load on file *write*,
so these keep an explicit fallback trigger:
- Before writing any Python: read `.claude/rules/python.md`.
- Before touching `eval/`, `ledger/metrics.py`, `ledger/evaluate.py`,
  `ledger/extract.py`, or `ledger/confidence.py`: read `.claude/rules/evals.md`.
  Never generate, infer, or modify labels in the test set.
- Before touching `ledger/accounting_client.py` or `ledger/mcp_server.py`: read
  `.claude/rules/integration.md`, then verify against Intuit's QuickBooks
  Online API docs. Do not recall endpoints, fields, or error codes from memory.

## Hand-written
The human writes these files to build interview skill. You may read, run,
type-check, and review them, and explain concepts on request.
You may NOT edit them, create them, or paste a full implementation in chat.
When you find a bug, describe the bug and where it is. Do not write the fix.
Write tests for these files only when asked.
- `ledger/schema.py`
- `ledger/validate.py`
- `ledger/confidence.py`
- `ledger/metrics.py`

## Task completion
A task is done only when the active `CONTRACT_*.md` is satisfied.
Contracts are named `CONTRACT_<task>.md` at the repo root. Once satisfied, move it to `contracts/done/`.
Never edit a test to make it pass. If the contract is ambiguous, stop and ask.

## Reporting
Report all findings, including "no issues found."
Never manufacture a finding to satisfy a request.

## After compaction or /clear
Re-read this file, the active contract, and the files the contract names
before continuing.