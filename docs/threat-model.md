# Threat Model

CLPG defends against ambiguity and inconsistency in local declared records.

It can detect:

- missing or conflicting claim records;
- attempts to weaken protected task flags through claim metadata;
- missing authority, actor mismatch, expired authority, or missing authority digest;
- stale, expired, or uncertified snapshots;
- missing public coordination state;
- budget or horizon mismatch between public and local records;
- missing audited participation interface;
- missing feasibility masks;
- missing controller certificate or empty safe controller set;
- certificate lineage mismatch against the service certificate family;
- missing evidence, contradiction flags, or non-replayable evidence;
- missing policy-required stabilizability or corroboration certificates;
- uncertified service-fault profiles;
- cost, deadline, harm, controller-loss, capability, or success threshold failures;
- receipt digest tampering;
- ledger mutation, insertion, or reordering.

It cannot detect:

- forged upstream certificates that already appear valid to the caller;
- compromised local operating systems or Python runtimes;
- hidden facts outside declared records;
- legal, moral, institutional, or organizational authorization not encoded in inputs;
- whole-ledger regeneration or tail deletion without an external expected head/count anchor;
- incorrect calibration of caller-declared uncertainty bounds.

Digest lineage is a local consistency check. It is not cryptographic signature verification.

Do not post the following in public GitHub issues, pull requests, logs, or screenshots:

- private task snapshots or user prompts;
- production authority scopes, external authority receipts, or actor identifiers;
- evidence records that name private systems, files, customers, incidents, or internal policies;
- receipt or ledger files from real operations;
- API keys, service tokens, session cookies, database paths, `.env` contents, or credentials;
- exploit details that would allow unauthorized use before a maintainer has a private report.

Use synthetic conformance fixtures when reporting bugs. If a real receipt or ledger is required to reproduce a vulnerability, provide only a minimized redacted shape publicly and coordinate private disclosure through GitHub Security Advisories or another maintainer-approved channel.
