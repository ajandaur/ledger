# Verify

Score each dimension 0 to 5. Cite specific lines. List blocking issues
separately from suggestions.

1. **Spec fidelity**: does this achieve the active contract? Must score 4 or higher.
2. Correctness and edge-case handling.
3. Test quality: would these tests actually fail if the behavior broke?
4. Typing, error handling, and external-call safety.
5. Scope discipline: no drive-by edits outside the contract.

Spec fidelity below 4 is blocking. Rework, then re-verify in a fresh session.
