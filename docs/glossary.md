# Glossary

`ClaimSnapshot`
: The declared atomic claim for strict mode. It carries the requested role, action, target references, metadata digest, budget demand, stake demand, and protected/external-effect flags.

`ClaimRole.CONTINUE`
: The source-paper `continue` role. In CLPG v0.1.x, a valid continue claim is
represented as operational `decision="act"` with
`continue_conditions_satisfied` in the receipt. This is a compatibility
quotient, not a theoretical identity between `continue` and `act`.

`ParticipationDecision`
: The operational decision emitted by CLPG. v0.1.x exposes `act`, `assist`,
`verify`, `withdraw`, `exit`, `refuse`, and `escalate`; it intentionally does
not expose a first-class `continue` decision.

`Decision-eligible snapshot`
: A snapshot whose service envelope is certified, unexpired, fresh enough, and backed by nonempty posterior and certificate families.

`AmbientActionModel`
: The fixed finite action/role universe for the round plus the feasible action/role masks for the current snapshot.

`AuditedParticipationInterface`
: The declared public interface from the certified snapshot into protocol state, including comparison class, deviation table, proxy gain, baseline, coverage, stability, and omission certificate digests.

`ControllerCertificateSnapshot`
: A declared summary of the controller certificate or operational sketch, including the feasibility mask digest, loss model digest, and whether a safe policy set is nonempty.

`VerificationPortfolioSnapshot`
: A declared verification portfolio summary with ambient target classes, response actions, verifier families, ambiguity status, and safe decision set status.

`CorroborationSnapshot`
: A declared corroboration summary with covariance certificate digests and lower bounds for effective size and observable separation.

`Certificate lineage`
: The local check that derived certificate digests are present in the service certificate family or explicitly allowed as external certificate digests by policy.

`ParticipationReceipt`
: The canonical decision record emitted by CLPG. It binds inputs, checks, reason codes, decision trace, and digests.

`Refuse` and `escalate`
: CLPG operational non-admission and fallback outcomes. They are not
source-paper semantic roles.
