---
paths:
  - "eval/**"
  - "ledger/metrics.py"
  - "ledger/evaluate.py"
  - "ledger/extract.py"
  - "ledger/confidence.py"
---

# Evals

- Labels are authored by the human only. Never generate, infer, or modify
  `expected_fields`, `difficulty`, or `label_confidence`.
- Never write the eval runner and the extraction or confidence logic in the same session.
- On every prompt, threshold, or model change: re-run the full eval and report
  per-metric deltas before commit. Never ship a change on a spot check.
- Report label uncertainty honestly. Where two readings are defensible, the
  human records both in the label's `notes` field.
- You may flag a possibly contestable label in your report. Never write it
  into the label.
