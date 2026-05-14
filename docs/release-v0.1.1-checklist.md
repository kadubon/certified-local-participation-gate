# v0.1.1 Maintenance Release Checklist

## Local Checks

- Run `uv lock --check`.
- Run `uv sync --locked --dev`.
- Run `uv run ruff format .`.
- Run `uv run ruff format --check .`.
- Run `uv run ruff check .`.
- Run `uv run mypy src`.
- Run `uv run pytest`.
- Run `uv run clpg version`.
- Run `uv run clpg conformance run examples/conformance --json`.
- Run `uv run clpg schema export <temp-dir> --json`.
- Run `uv build`.
- Run local wheel smoke with `dist/clpg-0.1.1-py3-none-any.whl`.
- Run `uv run pip-audit`.

## Release Gates

- Confirm version metadata is `0.1.1`.
- Confirm no API-breaking enum change was made.
- Confirm source-paper `continue` maps to operational `act` with
  `continue_conditions_satisfied`.
- Confirm conformance fixtures still pass.
- Confirm docs are human-reviewable Markdown.
- Confirm Dependabot config exists.
- Confirm `CITATION.cff` separates the software artifact from the source paper
  DOI.
- Confirm `schema_version` is documented as schema-family metadata, not package
  version metadata.
- Confirm `schema_version` namespacing remains deferred.
- Confirm `SECURITY.md` still warns against posting secrets, authority records,
  task snapshots, ledgers, or operational receipts.
- Confirm no secrets or real operational data are committed.
- Confirm `AGENTS.md` is absent before commit.

## Distribution Boundary

- Do not publish to PyPI for v0.1.1.
- Do not add a PyPI publishing workflow.
- Do not create a git tag during the maintenance patch implementation.
- Do not create a GitHub Release during the maintenance patch implementation.
- Dependabot uses the `pip` ecosystem for Python dependency metadata because a
  uv-specific Dependabot ecosystem is not used here.

## Deferred To v0.2.0

- First-class `ParticipationDecision.CONTINUE`.
- Namespaced schema versions such as `clpg.participation_receipt.v1`.
- Theorem-level certificate generation.
- Upstream service-signature verification.
- Robust controller LP.
- Shapley attribution.
- Local stability certificate synthesis.
- Covariance certificate validation.
- Optional CMGL/no-meta/OASG integrations.
- PyPI distribution, if desired later.
