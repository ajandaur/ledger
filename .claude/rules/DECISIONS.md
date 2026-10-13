# DECISIONS

These are locked. Do not revise them. If you believe one is wrong, stop and
raise it as an option. Do not implement around it.

## Imperative (locked)

1. **Deterministic first, agent second, with a measured delta.** Build the
   rule-based pipeline, score it, then introduce model-based extraction and
   planning only where the rules fail. Record the before and after. Never reach
   for an agent to look sophisticated; reach for it when you have a number
   showing the pipeline lost.

2. **The action lands in a real system.** Draft-for-approval against a live
   QuickBooks Online developer sandbox, not a mock API. Real auth, real rate
   limits, real error semantics, and a schema we did not design. One sandbox.
   No provider abstraction.

3. **Three real users, one round each, before the artifacts are written.** Not a
   product, not retention, not a signup flow. Three people run their own
   invoices while the human watches. `SCOPING.md` is written from what they
   surface.

4. **The eval layer is the centerpiece.** Golden dataset, false-confidence rate
   as the headline metric, regression mode on every change.

5. **Small, hand-labeled test set: 20 to 30 documents, all labeled by the
   human.** The agent never generates, infers, or modifies labels.

6. **Draft-for-approval, never autonomous execution.** The path to autonomy is
   documented in `SAFETY.md`, not walked.

7. **Ship the thin version, then write.** When choosing between another agent
   feature and a better writeup, choose the writeup.

**Document type: invoices. Locked.** One document type, one schema, one
validation pass, one tool action.

## Declarative (agent's call)

File layout within a module, naming, internal helper structure, PDF/OCR library
choice, regex strategy, prompt wording.

Standing clause for every session: if you find a design that better achieves
the contract than the one specified, raise it as an option before implementing
it.