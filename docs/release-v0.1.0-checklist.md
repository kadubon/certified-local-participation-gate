# v0.1.0 GitHub-Only Release Checklist

## Local Verification

- Run `uv lock`.
- Run `uv sync --locked --dev`.
- Run `uv run pytest`.
- Run `uv run ruff check .`.
- Run `uv run mypy src`.
- Run `clpg conformance run examples/conformance --json`.
- Run `clpg schema export <temp-dir> --json`.
- Run `uv build`.
- Install the local wheel in a temporary environment.
- Run `clpg version --json` from the installed wheel.
- Run `uv run pip-audit`.

## Repository Hygiene

- Confirm `NOTICE` is absent.
- Confirm `dist/`, `build/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, and `__pycache__/` are absent before publication.
- Confirm `.gitignore` excludes `.env`, `.venv/`, `.clpg/`, logs, build artifacts, SQLite/database files, coverage files, and Python caches.
- Confirm generated schemas, build artifacts, local ledgers, and temporary receipt files are not committed unless they are intentional examples.

## Security Review

- Confirm examples and conformance fixtures contain no secrets, API keys, provider tokens, session cookies, private task data, production ledgers, real authority records, or real evidence records.
- Confirm public issues and release notes do not include private receipts, ledgers, authority scopes, task snapshots, or evidence references.
- Confirm digest lineage is described as declaration consistency, not signature verification.
- Confirm `SECURITY.md` explains how to report vulnerabilities without posting sensitive data.

## GitHub Workflows

- Confirm CI runs ruff, mypy, pytest, conformance, schema export smoke, build, and local wheel smoke.
- Confirm CodeQL workflow is present.
- Confirm dependency-review workflow is present.
- Confirm `pip-audit` is present in CI or explicitly required as a local release check.
- Confirm workflow permissions are least-privilege for the job purpose.
- Confirm no workflow requests `id-token: write`, `contents: write`, or package publishing permissions.

## Distribution Boundary

- Confirm no PyPI publishing workflow exists.
- Confirm no `twine`, PyPI token, Trusted Publishing, or package-name reservation step is part of v0.1.0.
- Confirm README states that v0.1.0 is GitHub/source distribution only.
- Confirm `pyproject.toml` project URLs point to source, docs, and issues.

## Citation

- Confirm `CITATION.cff` includes the source paper under `preferred-citation`.
- Confirm the source paper DOI is present: `10.5281/zenodo.19394600`.
- Confirm README links the DOI as the source paper DOI, not as a software artifact DOI.
