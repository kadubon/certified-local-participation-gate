# Formal Invariants

Implemented invariants:

- canonical JSON is deterministic;
- input digests are SHA-256 commitments over canonical JSON;
- same normalized inputs and policy produce the same decision trace and decision digest;
- strict mode without a declared `ClaimSnapshot` cannot produce `act`;
- a task-level protected flag cannot be weakened by a claim-level unprotected flag;
- target roles require target references in strict mode;
- requested `withdraw` and `exit` are not blocked by task evidence/capability/success checks after strict entry checks pass;
- protected actions without authority cannot produce `act`;
- missing required evidence cannot produce `act` in strict mode;
- strict mode without declared feasibility masks cannot produce `act`;
- strict mode without an audited participation interface cannot produce `act`;
- strict mode without declared authority identity/certificate binding cannot produce `act`;
- strict mode without a controller certificate and nonempty safe policy set cannot produce `act`;
- derived certificate digests must match the service certificate family or declared external certificate digests;
- strict mode requires a service-fault profile digest before `act`;
- declared public budget and horizon records must agree with local budget/task records before `act`;
- `none` is a null claim and cannot produce `act`;
- policy-required stabilizability and corroboration require certificate digests before `act`;
- `assist` does not authorize protected action when protected-action authority is missing;
- receipts bind all input digests;
- receipt verification includes both decision digest and receipt digest;
- append-only ledgers detect tampering.
- anchored ledger verification detects tail deletion when expected head/count are supplied.

Restricted monotonicity is tested only for scalar strict thresholds supported by the implementation. No theory-wide monotonicity claim is made.
