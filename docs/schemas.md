# Schemas

JSON Schema export is the v0.1.x interoperability boundary for tools and ports.

```bash
uv run clpg schema export ./schemas --json
```

The schema set includes:

- `TaskSnapshot`
- `ClaimSnapshot`
- `PublicCoordinationState`
- `AmbientActionModel`
- `AuditedParticipationInterface`
- `ControllerCertificateSnapshot`
- `VerificationPortfolioSnapshot`
- `CorroborationSnapshot`
- `AgentSnapshot`
- `AuthoritySnapshot`
- `EvidenceSnapshot`
- `UncertaintyEnvelope`
- `AttributionState`
- `CostBudget`
- `ParticipationPolicy`
- `ParticipationReceipt`
- `LedgerRecord`
- `ConformanceCase`

## Multi-Language Use

A non-Python implementation should:

1. validate input JSON against the exported schemas;
2. preserve enum string values exactly;
3. implement the same canonical JSON rules;
4. produce SHA-256 digests as `sha256:<64 lowercase hex>`;
5. run the bundled conformance fixtures;
6. verify receipt and ledger digest semantics.

The schemas describe data shape. The conformance fixtures describe expected behavior.

## Schema Version Naming

`schema_version` identifies a schema family/version, not the package release
version. For v0.1.1, existing values such as `"1.0"` are intentionally
preserved because they are part of receipt and conformance surfaces.

Namespaced schema identifiers such as `clpg.participation_receipt.v1` are
deferred to v0.2.0 or a later compatibility-reviewed release.
