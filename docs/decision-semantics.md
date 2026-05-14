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

## Role Semantics

| Role | v0.1.0 behavior |
|---|---|
| `none` | Null claim. Always `withdraw`. |
| `verify` | Requires target refs and a safe/nonempty verification portfolio. Emits `verify` when available, otherwise `withdraw`. |
| `withdraw` | After strict entry checks, emits `withdraw` without task evidence/capability/success checks. |
| `exit` | After strict entry checks, emits `exit` without task evidence/capability/success checks. |
| `assist` | Requires target refs and assist capability. Emits `assist` only when it does not expand authority. |
| `continue` | Requires target refs. Emits `act` with `continue_conditions_satisfied` for v0.1.0 API compatibility. |
| `act` | Requires evidence, replayability, risk/cost/capability/success thresholds, and all strict certificates. |

## Strict And Demo Modes

Strict mode is the default. It requires `ClaimSnapshot`, service certificate digests, controller certificate summaries, service-fault profile digest, and certificate lineage consistency.

Demo mode is an explicit relaxation for examples. It allows legacy task fields, implicit feasibility, and missing certificate digests. Demo receipts are useful for learning the API, not for strict operational claims.

## Escalation

`escalate` is emitted only when `allow_escalate=True` and `escalation_target` is declared. It is an implementation fallback, not a source-paper role.

## Limitations

v0.1.0 consumes declared certificate digests and bounds. It does not validate signatures, solve the robust controller program, compute Shapley attribution, synthesize stability certificates, or prove covariance certificates.
