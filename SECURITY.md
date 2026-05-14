# Security Policy

CLPG is local-first and deterministic. Core tests and examples must not require network access, API keys, cloud accounts, hosted services, cookies, or real user data.

Do not post secrets, real authority records, private task evidence, production ledgers, private receipts, or private user data in public issues. Treat authority records, evidence records, task snapshots, receipts, and ledgers as potentially sensitive operational records unless they were created specifically as synthetic examples.

CLPG receipts are procedural records. They do not prove factual truth, moral permissibility, legal compliance, production safety, or institutional authorization.

Digest lineage is a local consistency check over declared certificate digests. It is not signature verification, key management, witness validation, or a substitute for upstream certificate verification.

Before publishing a receipt, ledger, fixture, or issue reproduction:

- remove private task content, private actor identifiers, production authority scopes, and internal evidence references;
- confirm no API keys, provider tokens, session cookies, credentials, or database paths are included;
- confirm the example is synthetic or explicitly approved for public disclosure.

Report vulnerabilities through GitHub Security Advisories when available. If a private contact channel is not configured yet, open a minimal public issue that describes the affected component without secrets, private ledgers, authority records, or exploit details.
