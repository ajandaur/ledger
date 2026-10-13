# Ledger: Spec

An invoice-processing agent that integrates with a real accounting system, is run by real users, takes a human-gated action, and reports its own error rate.

The system reads an invoice, extracts and validates structured data, posts a draft bill to a live QuickBooks Online sandbox for one-click human approval, and routes low-confidence cases to review. Around it sits an evaluation layer that measures how often and why the system is wrong, at both the output level and the trajectory level.

Locked decisions live in `.claude/rules/DECISIONS.md`. This file describes what to build.

---

## 1. Harness

### Files

- `CLAUDE.md`: an index of where to find context, under 40 lines.
- `.claude/rules/DECISIONS.md`: the locked decisions. Always loads.
- `.claude/rules/verify.md`: the review rubric. Always loads.
- `.claude/rules/python.md`: path-scoped to Python files.
- `.claude/rules/evals.md`: path-scoped to `eval/` and `ledger/metrics.py`.
- `.claude/rules/integration.md`: path-scoped to `ledger/accounting_client.py` and `ledger/mcp_server.py`.
- `CONTRACT.template.md`: copied once per task.

### `python.md` content

- pytest with recorded LLM fixtures. Never make live API calls in tests.
- `mypy --strict` clean, with every public signature typed.
- `ruff` for lint and format.
- `uv` with a committed lockfile.
- Explicit retry, timeout, and backoff on every external call.
- Structured logging.
- Env-based config with a committed `.env.example`. No secrets in code.
- Alembic migrations. Never hand-edit the schema.
- No new dependency without stating why the stdlib or an existing dependency will not do.

### `evals.md` content

- All labels are authored by the human. The agent never generates, infers, or modifies `expected_fields`, `difficulty`, or `label_confidence`.
- Never write the eval runner and the extraction or confidence logic in the same session.
- Every prompt, threshold, or model change re-runs the full eval and reports per-metric deltas before commit. No change ships on a spot check.
- Report label uncertainty honestly. Where two readings are defensible, record both.

### `integration.md` content

- All sandbox calls go through one client module with explicit timeout, retry, and backoff.
- Log every non-2xx response with its request context.
- Never retry a write without an idempotency key.
- Sandbox credentials come from env only.
- Record any schema mismatch between our Pydantic model and the vendor payload in `INTEGRATION.md` when it is discovered, not reconstructed later.
- Verify endpoints, fields, and error codes against Intuit's QuickBooks Online API docs. Do not recall them from memory.

### `verify.md` content

Score each dimension 0 to 5, cite specific lines, and list blocking issues separately from suggestions.

1. **Spec fidelity**: does this achieve the active contract? Must score 4 or higher.
2. Correctness and edge-case handling.
3. Test quality: would these tests actually fail if the behavior broke?
4. Typing, error handling, and external-call safety.
5. Scope discipline: no drive-by edits outside the contract.

### `CONTRACT.template.md`

```markdown
# CONTRACT: <task name>

## Done means
- [ ] <specific, checkable outcome>
- [ ] `uv run pytest` passes, N tests, none edited to pass
- [ ] `uv run mypy --strict .` clean
- [ ] `uv run ruff check .` clean

## Files in scope
<paths>

## Out of scope
<paths and behaviors the agent must not touch>

## Verification
Fresh session, `verify.md` rubric. Spec fidelity must score 4 or higher.
```

### Working loop

1. Research and implementation never share a context. Plan in plan mode, write the plan to a file, `/clear`, then implement from the plan in a clean session.
2. Verify in a fresh session, early and often.
3. Use neutral prompts: "Trace the logic of each component and report all findings."
4. Monthly cleanup pass: read every file in `.claude/rules/`, list contradictions and dead rules, and ask what to keep.

---

## 2. Scope caps

- One document type, one schema, one validation pass, one tool action.
- Test set capped at 30 documents.
- Three users, one round each.
- One accounting sandbox, with no provider abstraction.
- No vector DB or RAG. No fine-tuning. No polished frontend. No public launch.
- No agent tooling beyond section 1. If a real pain point appears, add one rule file, not a dependency.

---

## 3. The task

**Input:** a vendor invoice (PDF or image).

**Extraction schema:**

| Field | Notes |
| --- | --- |
| `vendor_name` | Free text, high variation |
| `invoice_number` | Format varies widely by vendor |
| `invoice_date`, `due_date` | Ambiguous formats are a deliberate hard case |
| `currency` | Not always explicit |
| `line_items[]` | Description, quantity, unit price, line total |
| `subtotal`, `tax`, `total` | Must reconcile |
| `payment_terms` | Often absent. Absence is a valid answer |

**Validation rules (no model):**

- Dates parse, and `due_date >= invoice_date`.
- Amounts are numeric.
- Line items sum to the subtotal.
- Subtotal plus tax equals the total.
- Required fields are present.
- Currency is consistent across the document.

**The action:** create a draft bill in the QuickBooks Online sandbox, categorized to an expense account and queued for one-click human approval. Categorization is the step that needs a model.

**Documents:** public invoice template sites, open datasets of scanned invoices, and invoices generated from open-source accounting tools with deliberate formatting variation. No proprietary data.

---

## 4. Layers

### Layer 0: Deterministic baseline

1. Extract text with a PDF text-layer parser, falling back to OCR for scans.
2. Pull fields with regex and layout heuristics: labeled-field patterns for the invoice number and dates, table detection for line items, and keyword anchors for totals.
3. Apply the validation rules, starting with arithmetic reconciliation.
4. Score against the test set and record the number.

### Layer 1: The agent

**Pipeline:** ingest, extract structured fields (LLM with structured output), validate, assign confidence, then branch. High confidence drafts the bill and queues it for approval. Low confidence routes to human review.

**Confidence is composite, not a model self-report.** It combines four signals:

- Whether the arithmetic reconciled
- Whether the deterministic and model extractions agreed
- Whether the required fields were present
- Whether the model flagged ambiguity

**Tool layer, exposed as an MCP server:** `post_to_accounting`, `lookup_vendor`, `request_missing_field`.

**Vendor resolution is the agentic loop.** The agent looks up the vendor, fuzzy-matches it, decides whether to use an existing vendor or create a new one, and requests a missing field if needed.

**Approval queue:** a CLI or a one-page FastAPI app. No design work.

### Layer 2: Integration

`post_to_accounting` writes to the QuickBooks Online sandbox. The integration must handle:

- OAuth flow, token refresh, and credential rotation
- A vendor bill schema, line-item model, and account references that differ from ours
- Vendor entity resolution: map an extracted name to an existing vendor ID, or create the vendor first
- Rate limits and throttling
- Idempotency when a write times out
- Vendor error semantics

Write `INTEGRATION.md` as each mismatch is hit.

### Layer 3: Users

Three sessions of about 30 minutes each, with people who process bills they receive (a small business owner or a bookkeeper). Each person runs five of their own invoices while the human watches. Collect:

- Invoice formats the schema did not anticipate
- Extractions that were correct but useless
- Reactions to the confidence threshold
- Requests that were deliberately not built

Add any surfaced formats to the test set as rows marked `source: user_session`. Redact or discard user data after each session.

### Layer 4: Evaluation

**Output-level metrics:**

- Field-level accuracy
- **False-confidence rate**: confident and wrong. This is the headline metric.
- Escalation precision

**Trajectory-level metrics**, scored on the vendor-resolution loop:

- Tool selection correctness per step
- Argument correctness given the tool
- Recovery after a failed call
- Cases where the output was right but the path was wrong

If the trajectory turns out to be effectively linear, drop trajectory scoring and say so in `EVAL.md`.

**Threshold curve:** report auto-draft rate against false-action rate across thresholds, then state the chosen point and the reason for it.

**Regression mode:** every prompt, threshold, or model change re-runs the full eval and reports per-metric deltas.

### Layer 5: Adversarial testing (half a day)

The threat model is a vendor who controls the document content and wants an invoice auto-approved. Make three attempts:

- An instruction in a line-item description that tries to inflate the confidence score
- An instruction in the vendor name field that tries to redirect `post_to_accounting`
- An instruction rendered into a scanned image that tries to suppress escalation

Document what worked before fixing it.

### Layer 6: Artifacts

Write each artifact during the phase that produces it.

- `INTEGRATION.md`: schema mismatches, undocumented behavior, broken assumptions
- `SCOPING.md`: what the users surfaced, what was built, what was not, and why
- `/failure_cases/`: 5 to 8 real failures. Each case covers the input, the output, why it failed, the fix, and the regression test that now catches it.
- `EVAL.md`: dataset construction, labeling decisions, contestable labels, metric definitions, the deterministic-versus-agentic delta, and the threshold curve
- `SAFETY.md`: injection findings and fixes, user data handling, never-auto actions, escalation policy, and the bar for autonomous execution
- `DEPLOYMENT.md`: rollout inside a regulated organization, covering permissions, audit logging, human gates, monitoring, v1 cuts, and what breaks at 100x volume

---

## 5. Architecture

```
invoice (PDF / image)
   |
   v
ingest.py               <- text layer, OCR fallback
   |
   +---------------------------+
   |                           |
   v                           v
baseline_extract.py      extract.py          <- deterministic and model paths,
(regex + layout)         (LLM, structured)      scored separately
   |                           |
   +------------+--------------+
                |
                v
         validate.py           <- arithmetic reconciliation and rule checks
                |
                v
         confidence.py         <- composite score
                |
                v
         agent.py              <- branch, MCP tool calls, approval queue
                |
   +------------+------------+
   |                         |
high confidence          low confidence
   |                         |
draft bill in            review queue
QBO sandbox
   |
human approval --> execute
```

### Supporting modules

All modules live in `ledger/`.

- `schema.py`: Pydantic models shared by the extractor and the labels
- `accounting_client.py`: OAuth, token refresh, retry, backoff, idempotency keys, vendor resolution
- `mcp_server.py`: `post_to_accounting`, `lookup_vendor`, `request_missing_field`
- `metrics.py`: metric computation (hand-written)
- `evaluate.py`: the eval runner, which loads the set, calls the pipeline, calls `metrics.py`, and reports deltas
- `trace.py`: span capture for trajectory evaluation
- `cli.py`: `run`, `eval`, `approve`, `redteam`

### Hand-written files

The human writes these files. See `CLAUDE.md` for the rules.

- `schema.py`
- `validate.py`
- `confidence.py`
- `metrics.py`

---

## 6. Test set

- Public sources only.
- About half clean digital PDFs and half scanned or photographed documents.
- 20 to 30 documents, all labeled by the human.
- Deliberate hard cases:
  - An ambiguous date format (03/04/2026)
  - A currency that is implied but never stated
  - Line items that do not sum to the subtotal because the invoice itself is wrong
  - A discount or credit line with a negative amount
  - A multi-page invoice whose line items continue across the page break
  - A handwritten annotation on a scan
  - A field where two readings are both defensible
- Record where labels are contestable.
- Store each document as JSON with these keys: `document_id`, `input_path`, `expected_fields`, `difficulty`, `label_confidence`, `notes`, `source`.

---

## 7. README structure

1. The problem, quantified
2. Headline results table: field accuracy, false-confidence rate at the chosen threshold, and the deterministic-versus-agentic delta
3. The integration and the hardest thing about it
4. Architecture diagram
5. What the three users changed
6. How the eval works, with the threshold curve
7. The number that justified the agent
8. Links to `/failure_cases/`, `INTEGRATION.md`, `SCOPING.md`, `EVAL.md`, `SAFETY.md`, and `DEPLOYMENT.md`
9. What was cut and what comes next
10. Setup that works in under five minutes

---

## 8. Build order

1. **Phase 1, deterministic baseline:** freeze the schema. Build ingest, baseline extraction, validation, and the approval queue end to end on a single clean invoice. Register the QBO sandbox.
2. **Phase 2, test set and first numbers:** collect and hand-label the 20 to 30 invoices. Build the eval runner in a separate session. Score the baseline.
3. **Phase 3, model layer:** LLM extraction with structured output. Re-score. Add agentic planning only where the pipeline measurably fails, and record the delta. Build the MCP tool layer against a stub.
4. **Phase 4, integration:** swap the stub for the live sandbox. Write `INTEGRATION.md` along the way.
5. **Phase 5, users:** run three sessions, update the test set, and write `SCOPING.md`.
6. **Phase 6, trajectory eval:** add span capture and trajectory scoring, write `EVAL.md`, and start `/failure_cases/`.
7. **Phase 7, red-team and safety:** run the half-day red-team, finish `/failure_cases/`, and write `SAFETY.md`.
8. **Phase 8, final artifacts:** `DEPLOYMENT.md` and the README.