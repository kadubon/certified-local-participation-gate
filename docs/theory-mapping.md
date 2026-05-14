# Theory Mapping

CLPG v0.1.1 is a declared-record implementation of the paper's local
participation layer. It does not implement the full optimization theory. It
checks whether the records required by that theory are present, internally
consistent, and within declared policy thresholds.

Source paper: K. Takahashi, "When Should a Local Agent Act, Assist, Verify, Withdraw, or Exit? A Certified Local Micro-Theory of Open-Task Participation", DOI [10.5281/zenodo.19394600](https://doi.org/10.5281/zenodo.19394600).

v0.1.1 consumes declared certificates, digests, finite-set records, and bounds.
It does not generate theorem-level certificates from the paper, validate
upstream signatures, or prove that declared certificates are substantively
correct.

| Paper concept | CLPG artifact | Strict check | v0.1.1 limitation |
|---|---|---|---|
| one authenticated local review round | one `decide_participation(...)` call | all decisions are one-shot and deterministic | no global equilibrium or long-horizon control |
| public coordination state `s_t` | `PublicCoordinationState` | budget/horizon/trace/queue/ledger/linkage/provenance digests are declared | digests are consumed, not independently reconstructed |
| certified service envelope `Gamma_t` | `ServiceEnvelope` | certificates verified flag, expiry, staleness, nonempty posterior/certificate families, service certificate digests | signature validation is external |
| decision-eligible snapshot | `eligibility.py` | missing/stale/expired/empty snapshot records degrade | no theorem-level proof generation |
| submitted atomic claim | `ClaimSnapshot` | strict mode requires a claim, target refs for target roles, budget/stake bounds | full multi-agent submitted profile optimization is not computed |
| silent option `\varnothing` | `ClaimRole.NONE` | always maps to `withdraw` | no allocation tree is generated |
| semantic roles | `ClaimRole` | role-aware terminal handling for `verify`, `withdraw`, `exit`, `assist`, `continue`, `act` | public `ParticipationDecision` keeps no separate `continue` value in v0.1.x |
| source-paper `continue` role | `ClaimRole.CONTINUE` mapped to operational `ParticipationDecision.ACT` | valid continue claims emit `continue_conditions_satisfied` | quotient mapping for v0.1.x compatibility, not theoretical identity |
| operational non-admission/fallback outcomes | `ParticipationDecision.REFUSE`, `ParticipationDecision.ESCALATE` | policy/authority refusal and explicit escalation fallback | not source-paper semantic roles |
| finite ambient action universe and feasibility mask | `AmbientActionModel` | finite no-duplicate action/role masks, feasible subset checks | no randomized policy optimization |
| controller certificate `CtrlCert_t` / sketch `CtrlSketch_t` | `ControllerCertificateSnapshot` | certificate/sketch digest, loss model digest, feasibility digest, nonempty safe policy set | no robust LP or moment-polytope solver |
| audited participation interface `rho_t`, `kappa_t` | `AuditedParticipationInterface` | interface, comparison class, deviation table, proxy gain, baseline, coverage/stability/omission digests | no local stability synthesis |
| certificate extraction from service envelope | `lineage.py` | derived certificate digests must appear in service certificate family or policy external digests | digest lineage only, not cryptographic validation |
| robust uncertainty/posterior envelope | `UncertaintyEnvelope` | success, harm, controller loss, and service-fault thresholds | bounds are caller-declared |
| primitive certified service-fault profile | `ServiceFaultProfile` | strict mode requires a fault profile digest even for zero faults | continuity moduli are not evaluated |
| verification portfolio and ambiguity set | `VerificationPortfolioSnapshot` | ambient target/response/family sets, portfolio digest, nonempty ambiguity and safe decision set | robust verification value is not optimized |
| public covariance certificates | `CorroborationSnapshot` | covariance certificate digests and lower bounds when policy requires corroboration | covariance matrices are not checked |
| submission/admission separation | `AttributionState.submission_harm_upper_bound` | submission harm threshold is enforced before `act` | Shapley attribution is not computed |
| certified public objects | `ParticipationReceipt`, `LedgerRecord` | input digests, decision digest, receipt digest, ledger chain | external anchoring is required for tail deletion detection |
