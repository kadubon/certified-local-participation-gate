# Porting Guide

This guide is for implementing CLPG behavior in another language.

## Porting Boundary

The authoritative portability targets are:

- exported JSON Schemas;
- enum string values;
- canonical JSON serialization;
- SHA-256 digest format;
- ordered decision semantics;
- conformance fixtures;
- receipt and ledger digest verification.

Use `CITATION.cff` and the source paper DOI,
[10.5281/zenodo.19394600](https://doi.org/10.5281/zenodo.19394600), as the
citation reference set for ports. The DOI identifies the theory source, while
the conformance fixtures identify the v0.1.x executable behavior expected from
this repository.

## Required Steps

1. Export schemas from the Python package:

   ```bash
   uv run clpg schema export ./schemas --json
   ```

2. Implement model validation equivalent to the schemas.
3. Implement canonical JSON with sorted keys, compact separators, UTF-8, stable enum strings, and no NaN/Infinity.
4. Implement `sha256:<64 lowercase hex>` digests over canonical JSON bytes.
5. Implement evaluator ordering from `docs/decision-semantics.md`.
6. Run all fixtures under `examples/conformance`.
7. Verify receipt and ledger digest behavior.
8. Preserve citation metadata or equivalent documentation that distinguishes the source paper DOI from any software artifact DOI a port may later receive.

## Required Behavioral Matches

- Strict mode must fail closed when required declared records are missing.
- Demo mode may accept legacy task fields and implicit feasibility.
- Claim-level protected flags cannot weaken task-level protected flags.
- Role-specific terminal behavior for `verify`, `withdraw`, `exit`, and `assist` must happen before task evidence/capability/success checks.
- Certificate lineage must check declared digests against service certificate digests and policy external certificate digests.
- `continue` must emit `act` with `continue_conditions_satisfied` in v0.1.x.
- This is a quotient mapping for compatibility, not a claim that source-paper
  `continue` and `act` are theoretically identical.

## Non-Goals For Ports

Ports do not need to implement robust LP optimization, Shapley attribution,
signature validation, covariance proof checking, cloud integrations, or LLM
calls to conform to v0.1.x.
