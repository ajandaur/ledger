---
paths:
  - "**/*.py"
---

# Python

- Test with pytest against recorded LLM fixtures. Never make live API calls in tests.
- Use recorded sandbox responses as test fixtures. Mark live sandbox tests
  `@pytest.mark.live`, exclude them by default, and run them manually only.
- Keep `mypy --strict` clean. Type every public signature.
- Lint and format with `ruff`.
- Manage dependencies with `uv`. Commit the lockfile.
- Set an explicit retry, timeout, and backoff on every external call.
- Use structured logging.
- Read config from env. Commit a `.env.example`. Never put secrets in code.
- Change the schema only through Alembic migrations. Never hand-edit it.
- Before adding a dependency, state why the stdlib or an existing dependency will not do.
