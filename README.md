# Certified Local Participation Gate

Certified Local Participation Gate (`clpg`) is a deterministic local gate for deciding
whether an AI agent should `act`, `assist`, `verify`, `withdraw`, `exit`, `refuse`,
or explicitly `escalate` on one open task round.

It answers a narrow operational question:

> Given only declared observable task records, local capability, authority, evidence, uncertainty, attribution, cost, and policy thresholds, which participation mode is admissible right now?

CLPG is derived from K. Takahashi, "When Should a Local Agent Act, Assist, Verify,
Withdraw, or Exit? A Certified Local Micro-Theory of Open-Task Participation."
Source paper DOI: [10.5281/zenodo.19394600](https://doi.org/10.5281/zenodo.19394600).
v0.1.1 is a small reference kernel, not a full implementation of every theorem
in the paper.

## Start Here

Use CLPG when an agent runtime, workflow runner, or local automation needs a
repeatable answer before doing work:

1. collect declared JSON records for the task, claim, agent, authority,
   evidence, uncertainty, attribution, budget, and policy;
2. call the Python API or CLI;
3. inspect the `ParticipationReceipt`;
4. optionally append that receipt to a local JSONL ledger.

The important operational boundary is that CLPG checks the declared record set.
It does not discover missing facts, grant authority, or decide whether the task
is objectively correct. In strict mode, missing declared records cause the gate
to degrade instead of silently allowing `act`.

For a first run, use the demo quickstart. For behavior that matches the paper's
certified-snapshot premise, inspect the strict conformance fixture after that.

## What Problem This Solves

Agent systems often start work before the basic participation question has been made explicit:

- Is this agent authorized to touch this task?
- Is the snapshot current, certified, and replayable enough?
- Is the requested role feasible in the public action mask?
- Is verification safer than acting?
- Should the agent withdraw or exit rather than continue spending budget?

CLPG makes that first gate deterministic and reviewable. It produces a receipt that binds the inputs, checks, reason codes, and final decision by canonical JSON and SHA-256 digests.

## Why This Exists

The source paper treats participation as a one-round local decision over a
certified public snapshot. It does not treat public services as trusted
oracles. It requires declared envelopes, finite feasible masks, audited
participation interfaces, verification portfolios, service-fault bounds, and
certificate-derived public objects.

CLPG turns those theoretical requirements into a practical Python package:

- parse declared snapshots;
- check strict local admissibility;
- fail closed when declared records are missing or inconsistent;
- emit machine-readable reason codes;
- generate receipts and optional JSONL ledger records;
- export JSON Schemas for other implementations.

## What You Can Expect

CLPG can tell you:

- `act`: all strict local conditions passed;
- `assist`: acting directly is not admissible, but bounded assistance is admissible;
- `verify`: verification is the admissible next move;
- `withdraw`: the agent should stop participating in this round while preserving local continuity;
- `exit`: the local episode should be exited;
- `refuse`: policy or authority rejects the request;
- `escalate`: an explicit escalation policy chose a declared target.

Every valid decision, including `refuse`, exits normally from the CLI. A refusal is a successful gate decision, not a runtime error.

## Source-Paper Roles Vs. CLPG Decisions

The source paper distinguishes the semantic roles `continue`, `act`, `assist`,
`verify`, `withdraw`, and `exit`.

CLPG v0.1.x keeps a smaller operational decision enum:
`act`, `assist`, `verify`, `withdraw`, `exit`, `refuse`, and `escalate`.

For v0.1.x API and conformance compatibility, a valid source-paper `continue`
claim is represented as:

```json
{
  "decision": "act",
  "reason_codes": ["continue_conditions_satisfied"]
}
```

This is a quotient mapping, not a claim that `continue` and `act` are
theoretically identical. `refuse` and `escalate` are CLPG operational
non-admission and fallback outcomes, not source-paper semantic roles.

A first-class `ParticipationDecision.CONTINUE` is deferred to v0.2.0 because
it would change the public enum and conformance surface.

## What CLPG Does Not Certify

CLPG does not decide objective truth, morality, law, compliance, institutional authorization, or task success.

v0.1.1 consumes declared certificate digests and declared bounds. It does not:

- verify upstream service signatures;
- solve the robust controller LP;
- compute Shapley attribution;
- synthesize local stability certificates;
- validate covariance certificates;
- call an LLM, cloud service, API key, or network dependency.

Stronger paper-level claims require external certificates that CLPG v0.1.1 does not generate.

## How The Data Flows

```text
declared records
  -> Pydantic validation
  -> canonical JSON
  -> SHA-256 input digests
  -> ordered fail-closed decision evaluators
  -> ParticipationReceipt
  -> optional append-only JSONL ledger
```

Strict mode expects these declared records:

- `ClaimSnapshot`: the canonical requested role/action for strict mode;
- `ServiceEnvelope`: certificate validity, expiry, staleness, posterior/certificate family status;
- `PublicCoordinationState`: budget, horizon, trace, queue, role ledger, linkage, provenance digests;
- `AmbientActionModel`: finite ambient actions/roles and feasible masks;
- `AuditedParticipationInterface`: participation interface and coverage/stability/omission certificate digests;
- `ControllerCertificateSnapshot`: controller certificate or sketch digest and nonempty safe policy set;
- `VerificationPortfolioSnapshot`: target classes, response actions, verifier families, ambiguity, safe set;
- `CorroborationSnapshot`: covariance certificate digests and declared lower bounds when policy requires them.

Demo mode relaxes these requirements for examples and education. It is not the default operational mode.

## Install From Source

This v0.1.1 release is GitHub/source distribution only. There is no PyPI publish workflow.

```bash
uv sync --locked --dev
uv run clpg version
```

## Which Mode Should I Use?

Use demo mode only to learn the API or to write small examples. It relaxes
strict certificate and feasibility requirements.

Use strict mode for operational gate testing. Strict mode treats the
`ClaimSnapshot` as the canonical requested role/action, requires finite feasible
masks and certificate digests, checks authority identity, and fails closed when
records are missing or inconsistent.

## Demo Quickstart

Use demo mode for a minimal first run:

```python
from clpg import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    CostBudget,
    EvidenceSnapshot,
    TaskSnapshot,
    UncertaintyEnvelope,
    decide_participation,
)
from clpg.policy import demo_policy

receipt = decide_participation(
    task=TaskSnapshot(task_id="demo", requested_action="act"),
    agent=AgentSnapshot(agent_id="agent.local", capabilities=["act"]),
    authority=AuthoritySnapshot(actor="agent.local"),
    evidence=EvidenceSnapshot(),
    uncertainty=UncertaintyEnvelope(),
    attribution=AttributionState(),
    budget=CostBudget(budget_remaining=10),
    policy=demo_policy(),
)

print(receipt.decision.value)
print(receipt.receipt_digest)
```

Run bundled demos:

```bash
uv run python examples/basic_decision_demo.py
uv run python examples/verify_before_act_demo.py
uv run python examples/refuse_without_authority_demo.py
```

## Strict-Mode Quickstart

Strict mode is fail-closed. It requires the declared records above before `act` can be emitted.

The strict conformance fixture is the easiest complete example:

```bash
uv run clpg conformance run examples/conformance --json
```

Inspect `examples/conformance/act.valid.json` to see a minimal strict `act`
case. It includes the claim, service certificate family, public coordination
state, feasibility mask, audited interface, controller certificate, authority
binding, evidence state, service fault certificate digest, and policy.

## CLI

```bash
clpg version [--json]
clpg decide --task task.json --agent agent.json --authority authority.json \
  --evidence evidence.json --uncertainty uncertainty.json \
  --attribution attribution.json --budget budget.json --policy policy.json \
  [--ledger ledger.jsonl] [--json]
clpg schema export ./schemas [--json]
clpg ledger verify ./ledger.jsonl [--expect-head sha256:...] [--expect-count N] [--json]
clpg conformance run examples/conformance [--json]
clpg explain --receipt receipt.json [--json]
```

Input/schema errors exit `2`. Runtime and ledger verification errors exit `1`. Valid decisions, including `refuse`, exit `0`.

## Decision Table

| Condition | Default strict result |
|---|---|
| Task or policy disallows the task | `refuse` |
| Missing strict `ClaimSnapshot` | `verify` if possible, otherwise `withdraw` |
| `none` claim | `withdraw` |
| Protected flag conflict | `refuse` |
| Missing or mismatched authority | `refuse` |
| Snapshot certificates missing, stale, expired, or empty | `verify` if possible, otherwise `withdraw` |
| Public state disagrees with local budget/horizon | `verify` if possible, otherwise `withdraw` |
| Missing feasible mask or controller safe set | `verify` if possible, otherwise `withdraw` |
| Certificate lineage mismatch | `verify` if possible, otherwise `withdraw` |
| Requested `verify` with safe verification portfolio | `verify` |
| Requested `withdraw` after strict entry checks | `withdraw` |
| Requested `exit` after strict entry checks | `exit` |
| Requested `assist` with assist capability and no authority expansion | `assist` |
| Missing required evidence for `act` | `verify` if possible, otherwise `withdraw` |
| Harm bound exceeds policy | `exit` if enabled, otherwise `withdraw` |
| Direct capability missing for `act` | `assist`, then `verify`, then `withdraw` |
| All strict `act` conditions pass | `act` |

`continue` is a source-paper role. For v0.1.x API compatibility, a valid
continue claim is emitted as `act` with `continue_conditions_satisfied` in the
receipt trace.

## Receipts And Ledgers

Every `ParticipationReceipt` contains:

- input digests for the fixed input set;
- ordered check results;
- stable reason codes;
- a deterministic `decision_digest`;
- a full `receipt_digest`.

`clpg explain --receipt receipt.json --json` reports whether both digests verify.

`AppendOnlyLedger` stores receipts in JSONL records linked by previous-record digest. Ledger verification detects mutation, insertion, and reordering inside the observed file. Tail deletion and whole-ledger regeneration require an expected head digest or expected count:

```bash
uv run clpg ledger verify ledger.jsonl --expect-head sha256:... --expect-count 12 --json
```

## How To Port CLPG

Treat JSON Schema export and conformance fixtures as the portability boundary:

```bash
uv run clpg schema export ./schemas --json
uv run clpg conformance run examples/conformance --json
```

A port in another language should preserve:

- canonical JSON shape and enum strings;
- SHA-256 digest format `sha256:<64 lowercase hex>`;
- ordered evaluator semantics;
- stable reason codes;
- receipt and ledger digest rules;
- conformance fixture outcomes.

See `docs/porting.md` for the recommended porting checklist.

## Development Checks

```bash
uv lock
uv sync --locked --dev
uv run ruff format --check .
uv run pytest
uv run ruff check .
uv run mypy src
uv run clpg conformance run examples/conformance --json
uv run clpg schema export ./schemas --json
uv build
```

## Documentation

- `docs/architecture.md`: evaluator pipeline and module boundaries.
- `docs/decision-semantics.md`: ordered role-aware gate semantics.
- `docs/theory-mapping.md`: source-paper concepts mapped to CLPG artifacts.
- `docs/proof-obligations.md`: certificates and bounds CLPG consumes but does not generate.
- `docs/formal-invariants.md`: invariants covered by tests.
- `docs/schemas.md`: JSON Schema and conformance guidance.
- `docs/threat-model.md`: what CLPG detects and what remains out of scope.
- `docs/porting.md`: guidance for multi-language implementations.
- `docs/glossary.md`: short definitions of recurring terms.
- `docs/release-v0.1.1-checklist.md`: local and GitHub-only release gates.
- `CHANGELOG.md`: release history.

## Citation

If you use this package, cite both this software artifact and the source paper.
The software artifact does not yet have a separate DOI unless one is added
later. The source paper DOI is
[10.5281/zenodo.19394600](https://doi.org/10.5281/zenodo.19394600).
Machine-readable citation metadata is in `CITATION.cff`.

## License

Apache-2.0.
