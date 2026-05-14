# Contributing

Contributions should preserve the v0.1.x scope:

- deterministic local checks;
- no runtime LLM calls;
- no required network services;
- no hidden evaluators;
- no permissive strict-mode defaults that allow `act` without declared certificates;
- no PyPI publishing workflow for GitHub-only releases;
- no committed generated artifacts such as `dist/`, caches, temporary schemas, local receipts, or local ledgers;
- no network dependency in core tests;
- no real task data, production authority records, private evidence, secrets, tokens, or user data in fixtures.

Use synthetic examples for tests and documentation. Authority, evidence,
receipt, and ledger files should be treated as sensitive unless they were
created only for public conformance testing.

Before proposing a change, run:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

For release-readiness changes, also run the conformance suite, schema export
smoke, local build, wheel smoke, and `pip-audit` as listed in the current
release checklist under `docs/`.
