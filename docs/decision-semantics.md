# Decision Semantics

The gate is ordered, deterministic, and fail-closed. Earlier terminal rules stop later checks. This makes the receipt trace portable across implementations.

## Ordered Pipeline

1. Refuse task-level or policy-level disallowance.
2. Validate the submitted claim.
3. Validate authority scope, actor binding, and authority certificate binding.
4. Validate snapshot eligibility.
5. Check public-state budget and horizon consistency.
6. Check ambient action/role feasibility.
7. Check certificate lineage against the service certificate family.
8. Check the controller certificate or sketch.
9. Apply role-specific early terminals for `verify`, `withdraw`, `exit`, and explicit `assist`.
10. For roles that can become `act`, check evidence, corroboration, risk, cost, capability, and success thresholds.
11. Emit `act` only when every required strict condition passes.

## Source-Paper Roles Vs. Operational Decisions

The source paper distinguishes `continue`, `act`, `assist`, `verify`,
`withdraw`, and `exit` as semantic roles.

CLPG v0.1.x exposes the operational decisions `act`, `assist`, `verify`,
`withdraw`, `exit`, `refuse`, and `escalate`. For compatibility, a valid
source-paper `continue` claim is represented as `decision="act"` with the
reason and terminal trace code `continue_conditions_satisfied`.

This is a quotient mapping. It does not assert that `continue` and `act` are
theoretically identical. `refuse` and `escalate` are operational
non-admission/fallback outcomes, not source-paper semantic roles.

A first-class `ParticipationDecision.CONTINUE` is deferred to v0.2.0 because it
would change the public enum and conformance surface.

## Role Semantics

| Role | v0.1.x behavior |
|---|---|
| `none` | Null claim. Always `withdraw`. |
| `verify` | Requires target refs and a safe/nonempty verification portfolio. Emits `verify` when available, otherwise `withdraw`. |
| `withdraw` | After strict entry checks, emits `withdraw` without task evidence/capability/success checks. |
| `exit` | After strict entry checks, emits `exit` without task evidence/capability/success checks. |
| `assist` | Requires target refs and assist capability. Emits `assist` only when it does not expand authority. |
| `continue` | Requires target refs. Emits `act` with `continue_conditions_satisfied` for v0.1.x API compatibility. |
| `act` | Requires evidence, replayability, risk/cost/capability/success thresholds, and all strict certificates. |

## Strict And Demo Modes

Strict mode is the default. It requires `ClaimSnapshot`, service certificate digests, controller certificate summaries, service-fault profile digest, and certificate lineage consistency.

Demo mode is an explicit relaxation for examples. It allows legacy task fields, implicit feasibility, and missing certificate digests. Demo receipts are useful for learning the API, not for strict operational claims.

## Reading A Trace

`DecisionTrace.steps` is the ordered list of checks that led to the terminal
rule. `ParticipationReceipt.checks` carries the same check sequence in the
receipt payload. The final `terminal_rule` names the first rule that decided the
outcome.

For example, a valid source-paper `continue` claim reaches the terminal rule
`continue_conditions_satisfied`. The receipt decision is still `act` in
v0.1.x, so consumers that need to distinguish this case should inspect the
reason code or terminal rule.

## Escalation

`escalate` is emitted only when `allow_escalate=True` and `escalation_target` is declared. It is an implementation fallback, not a source-paper role.

## Limitations

v0.1.1 consumes declared certificate digests and bounds. It does not validate
signatures, solve the robust controller program, compute Shapley attribution,
synthesize stability certificates, or prove covariance certificates.

## Deferred To v0.2.0

- first-class `ParticipationDecision.CONTINUE`;
- stronger source-paper theorem coverage;
- upstream service-signature verification;
- robust controller LP;
- Shapley attribution;
- local stability certificate synthesis;
- covariance certificate validation;
- optional CMGL/no-meta/OASG integrations;
- PyPI distribution, if desired later.
