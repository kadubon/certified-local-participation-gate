# CLPG v0.1.1 Maintenance Plan

## Issues To Fix

- Bump software version metadata from `0.1.0` to `0.1.1`.
- Clarify that source-paper `continue` is mapped to operational `act` in
  v0.1.x with `continue_conditions_satisfied`.
- Improve README/docs reviewability without changing the theory or runtime
  behavior.
- Add Dependabot for GitHub Actions and Python dependency metadata.
- Clarify `CITATION.cff` so the source-paper DOI is not presented as a
  software DOI.
- Clarify that `schema_version` is a schema-family identifier, not the package
  version.
- Add a v0.1.1 release checklist and changelog.
- Delete `AGENTS.md` before committing.

## Files To Update

- `pyproject.toml`, `src/clpg/receipts.py`, `src/clpg/models.py`
- `README.md`, `CITATION.cff`, `CHANGELOG.md`
- `docs/decision-semantics.md`, `docs/theory-mapping.md`,
  `docs/glossary.md`, `docs/porting.md`, `docs/schemas.md`,
  `docs/release-v0.1.1-checklist.md`
- `.github/workflows/ci.yml`, `.github/dependabot.yml`
- `tests/test_cli.py`, `tests/test_decision_policy.py`,
  `tests/test_docs_metadata.py`

## Behavior That Must Not Change

- Public v0.1.x imports remain available.
- CLI commands remain available.
- `ParticipationDecision` does not gain `CONTINUE`.
- Valid source-paper `continue` claims still emit operational `act`.
- Existing conformance fixture expected decisions remain unchanged.
- Receipt digest semantics remain unchanged except that newly generated
  receipts bind `clpg_version="0.1.1"`.
- No runtime network, LLM, API-key, cloud, or external-service dependency is
  introduced.
- No PyPI publishing workflow is added.

## Tests To Run

```powershell
uv lock --check
uv sync --locked --dev
uv run ruff format .
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run clpg version
uv run clpg conformance run examples/conformance --json
uv run clpg schema export $env:TEMP\clpg-schemas --json
uv build
uv run --with .\dist\clpg-0.1.1-py3-none-any.whl clpg version --json
uv run pip-audit
```

## Deferred To v0.2.0

- First-class `ParticipationDecision.CONTINUE`.
- Namespaced `schema_version` values.
- Theorem-level certificate generation.
- Upstream service-signature verification.
- Robust controller LP.
- Shapley attribution.
- Local stability certificate synthesis.
- Covariance certificate validation.
- Optional CMGL/no-meta/OASG integrations.
- PyPI distribution, if desired later.
