"""Pydantic models for declared CLPG inputs and outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clpg.enums import ClaimRole, ParticipationDecision, PolicyMode, ReasonCode

DigestStr = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
RECEIPT_INPUT_DIGEST_KEYS = {
    "task",
    "agent",
    "authority",
    "evidence",
    "uncertainty",
    "attribution",
    "budget",
    "policy",
}


class CLPGModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, use_enum_values=False)


class ServiceEnvelope(CLPGModel):
    certificates_verified: bool = False
    expires_at: datetime | None = None
    snapshot_staleness_seconds: float = Field(default=0.0, ge=0.0)
    posterior_family_nonempty: bool = False
    derived_certificate_families_nonempty: bool = False
    service_certificate_digests: list[DigestStr] = Field(default_factory=list)


class PublicCoordinationState(CLPGModel):
    budget_remaining: float = Field(ge=0.0)
    remaining_horizon: int = Field(ge=0)
    verification_reserve: float = Field(default=0.0, ge=0.0)
    trace_digest: DigestStr
    queue_digest: DigestStr
    role_ledger_digest: DigestStr
    linkage_graph_digest: DigestStr
    provenance_summary_digest: DigestStr


class AmbientActionModel(CLPGModel):
    ambient_actions: list[str] = Field(min_length=1)
    feasible_actions: list[str] = Field(min_length=1)
    ambient_roles: list[ClaimRole] = Field(min_length=1)
    feasible_roles: list[ClaimRole] = Field(min_length=1)
    feasibility_mask_digest: DigestStr

    @model_validator(mode="after")
    def model_is_finite_set_mask(self) -> AmbientActionModel:
        if len(set(self.ambient_actions)) != len(self.ambient_actions):
            raise ValueError("ambient_actions must not contain duplicates")
        if len(set(self.feasible_actions)) != len(self.feasible_actions):
            raise ValueError("feasible_actions must not contain duplicates")
        if len(set(self.ambient_roles)) != len(self.ambient_roles):
            raise ValueError("ambient_roles must not contain duplicates")
        if len(set(self.feasible_roles)) != len(self.feasible_roles):
            raise ValueError("feasible_roles must not contain duplicates")
        if ClaimRole.NONE in self.ambient_roles or ClaimRole.NONE in self.feasible_roles:
            raise ValueError("none is a null claim role and cannot be in role masks")
        ambient_actions = set(self.ambient_actions)
        if any(action not in ambient_actions for action in self.feasible_actions):
            raise ValueError("feasible_actions must be a subset of ambient_actions")
        ambient_roles = set(self.ambient_roles)
        if any(role not in ambient_roles for role in self.feasible_roles):
            raise ValueError("feasible_roles must be a subset of ambient_roles")
        return self


class AuditedParticipationInterface(CLPGModel):
    protocol_state_id: str = Field(min_length=1)
    interface_digest: DigestStr
    certificate_digests: list[DigestStr] = Field(min_length=1)
    comparison_class_digest: DigestStr
    deviation_table_digest: DigestStr
    proxy_gain_table_digest: DigestStr
    baseline_interval_digest: DigestStr
    coverage_certificate_digest: DigestStr | None = None
    stability_certificate_digest: DigestStr | None = None
    omitted_deviation_certificate_digest: DigestStr | None = None


class VerificationPortfolioSnapshot(CLPGModel):
    ambient_target_classes: list[str] = Field(default_factory=list)
    ambient_response_actions: list[str] = Field(default_factory=list)
    ambient_verifier_families: list[str] = Field(default_factory=list)
    target_classes: list[str] = Field(default_factory=list)
    response_actions: list[str] = Field(default_factory=list)
    available_verifier_families: list[str] = Field(default_factory=list)
    slot_budget: int = Field(default=0, ge=0)
    ambiguity_nonempty: bool = False
    safe_decision_set_nonempty: bool = False
    portfolio_certificate_digest: DigestStr | None = None

    @model_validator(mode="after")
    def finite_sets_must_be_ambient(self) -> VerificationPortfolioSnapshot:
        for name in (
            "ambient_target_classes",
            "ambient_response_actions",
            "ambient_verifier_families",
            "target_classes",
            "response_actions",
            "available_verifier_families",
        ):
            values = getattr(self, name)
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must not contain duplicates")
        ambient_targets = set(self.ambient_target_classes)
        if ambient_targets and any(item not in ambient_targets for item in self.target_classes):
            raise ValueError("target_classes must be a subset of ambient_target_classes")
        ambient_responses = set(self.ambient_response_actions)
        if ambient_responses and any(
            item not in ambient_responses for item in self.response_actions
        ):
            raise ValueError("response_actions must be a subset of ambient_response_actions")
        ambient_families = set(self.ambient_verifier_families)
        if ambient_families and any(
            item not in ambient_families for item in self.available_verifier_families
        ):
            raise ValueError(
                "available_verifier_families must be a subset of ambient_verifier_families"
            )
        return self


class ControllerCertificateSnapshot(CLPGModel):
    feasibility_mask_digest: DigestStr
    controller_certificate_digest: DigestStr | None = None
    controller_sketch_digest: DigestStr | None = None
    loss_model_digest: DigestStr
    safe_policy_set_nonempty: bool = False


class CorroborationSnapshot(CLPGModel):
    covariance_certificate_digests: list[DigestStr] = Field(default_factory=list)
    active_block_count: int = Field(default=0, ge=0)
    effective_size_lower_bound: float = Field(default=0.0, ge=0.0)
    observable_separation_lower_bound: float = Field(default=0.0, ge=0.0)


class ClaimSnapshot(CLPGModel):
    requested_role: ClaimRole = ClaimRole.ACT
    requested_action: str = Field(min_length=1)
    target_refs: list[str] = Field(default_factory=list)
    metadata_digest: DigestStr | None = None
    budget_demand: float = Field(default=0.0, ge=0.0)
    stake_demand: float = Field(default=0.0, ge=0.0)
    protected_action: bool = False
    external_effect: bool = False


class TaskSnapshot(CLPGModel):
    task_id: str = Field(min_length=1)
    round_id: str = Field(default="default", min_length=1)
    requested_role: ClaimRole = ClaimRole.ACT
    requested_action: str = Field(default="act", min_length=1)
    protected_action: bool = False
    disallowed: bool = False
    remaining_horizon: int = Field(default=1, ge=0)
    feasible_roles: list[ClaimRole] = Field(
        default_factory=lambda: [
            ClaimRole.ACT,
            ClaimRole.ASSIST,
            ClaimRole.VERIFY,
            ClaimRole.WITHDRAW,
            ClaimRole.EXIT,
            ClaimRole.CONTINUE,
        ]
    )
    feasible_actions: list[str] = Field(default_factory=list)
    unrecoverable_scope_failure: bool = False
    service_envelope: ServiceEnvelope = Field(default_factory=ServiceEnvelope)
    public_state: PublicCoordinationState | None = None
    ambient_model: AmbientActionModel | None = None
    participation_interface: AuditedParticipationInterface | None = None
    controller_certificate: ControllerCertificateSnapshot | None = None
    claim: ClaimSnapshot | None = None
    submitted_profile_digest: DigestStr | None = None


class AgentSnapshot(CLPGModel):
    agent_id: str = Field(min_length=1)
    capabilities: list[str] = Field(default_factory=list)
    capability_lower_bound: float = Field(default=1.0, ge=0.0, le=1.0)
    assist_capabilities: list[str] = Field(default_factory=list)
    verification_capability: bool = False
    can_withdraw: bool = True
    can_exit: bool = True


class AuthoritySnapshot(CLPGModel):
    actor: str = Field(min_length=1)
    scope_id: str | None = None
    permitted_actions: list[str] = Field(default_factory=list)
    valid: bool = False
    expires_at: datetime | None = None
    authority_digest: DigestStr | None = None
    external_receipts: list[DigestStr] = Field(default_factory=list)


class EvidenceBlock(CLPGModel):
    evidence_id: str = Field(min_length=1)
    digest: DigestStr
    status: str = Field(default="declared", min_length=1)


class EvidenceSnapshot(CLPGModel):
    evidence_blocks: list[EvidenceBlock] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    missing_required_evidence: list[str] = Field(default_factory=list)
    contradiction_active: bool = False
    replayable: bool = False
    certificates_nonempty: bool = False
    verification_available: bool = False
    stabilizable_certified: bool = False
    verification_capacity: int = Field(default=0, ge=0)
    verification_portfolio: VerificationPortfolioSnapshot | None = None
    corroboration_certificate_digest: DigestStr | None = None
    corroboration: CorroborationSnapshot | None = None
    stabilizability_certificate_digest: DigestStr | None = None


class ServiceFaultProfile(CLPGModel):
    fault_profile_digest: DigestStr | None = None
    epsilon_post: float = Field(default=0.0, ge=0.0)
    epsilon_score: float = Field(default=0.0, ge=0.0)
    epsilon_omit: float = Field(default=0.0, ge=0.0)
    epsilon_ver: float = Field(default=0.0, ge=0.0)
    epsilon_corr: float = Field(default=0.0, ge=0.0)

    def max_fault(self) -> float:
        return max(
            self.epsilon_post,
            self.epsilon_score,
            self.epsilon_omit,
            self.epsilon_ver,
            self.epsilon_corr,
        )


class UncertaintyEnvelope(CLPGModel):
    success_lower_bound: float = Field(default=0.0, ge=0.0, le=1.0)
    harm_upper_bound: float = Field(default=0.0, ge=0.0, le=1.0)
    controller_loss_upper_bound: float = Field(default=0.0, ge=0.0, le=1.0)
    service_faults: ServiceFaultProfile = Field(default_factory=ServiceFaultProfile)
    uncertainty_notes: list[str] = Field(default_factory=list)


class AttributionState(CLPGModel):
    bundle_partition_digest: DigestStr | None = None
    bundle_contractive_certified: bool = False
    attribution_complete: bool = False
    submission_harm_upper_bound: float = Field(default=0.0, ge=0.0, le=1.0)
    retained_margin_lower_bound: float | None = Field(default=None, ge=0.0)


class CostBudget(CLPGModel):
    budget_remaining: float = Field(default=0.0, ge=0.0)
    cost_upper_bound: float = Field(default=0.0, ge=0.0)
    verification_cost_upper_bound: float = Field(default=0.0, ge=0.0)
    deadline_feasible: bool = True


class ParticipationPolicy(CLPGModel):
    schema_version: str = "1.0"
    mode: PolicyMode = PolicyMode.STRICT
    disallow_task: bool = False
    strict_evidence: bool = True
    require_replayability: bool = True
    require_attribution: bool = False
    require_bundle_contractiveness: bool = False
    require_claim_snapshot: bool = True
    require_public_coordination_state: bool = True
    require_audited_participation_interface: bool = True
    require_controller_certificate: bool = True
    require_explicit_service_expiry: bool = True
    require_service_certificate_digests: bool = True
    require_service_fault_certificate: bool = True
    require_stabilizable: bool = False
    require_corroboration: bool = False
    min_success_lower_bound_for_act: float = Field(default=0.6, ge=0.0, le=1.0)
    min_capability_lower_bound_for_act: float = Field(default=0.6, ge=0.0, le=1.0)
    min_corroboration_effective_size: float = Field(default=0.0, ge=0.0)
    min_observable_separation: float = Field(default=0.0, ge=0.0)
    max_submission_harm_upper_bound: float = Field(default=0.2, ge=0.0, le=1.0)
    max_harm_upper_bound: float = Field(default=0.2, ge=0.0, le=1.0)
    max_controller_loss_upper_bound: float = Field(default=0.5, ge=0.0, le=1.0)
    max_service_fault: float = Field(default=0.5, ge=0.0)
    max_snapshot_staleness_seconds: float = Field(default=300.0, ge=0.0)
    max_stake_demand: float = Field(default=0.0, ge=0.0)
    allow_assist: bool = True
    allow_implicit_feasible_actions: bool = False
    allow_escalate: bool = False
    escalation_target: str | None = None
    exit_on_unrecoverable_risk: bool = True
    verify_on_ineligible_snapshot: bool = True
    strict_authority: bool = True
    external_certificate_digests: list[DigestStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def escalation_requires_target(self) -> ParticipationPolicy:
        if self.allow_escalate and not self.escalation_target:
            raise ValueError("allow_escalate requires escalation_target")
        return self


class CheckResult(CLPGModel):
    name: str = Field(min_length=1)
    passed: bool
    reason_code: ReasonCode | None = None
    observed: dict[str, Any] = Field(default_factory=dict)
    threshold: dict[str, Any] = Field(default_factory=dict)


class DecisionTrace(CLPGModel):
    terminal_rule: str = Field(min_length=1)
    steps: list[CheckResult] = Field(default_factory=list)


class ParticipationReceipt(CLPGModel):
    schema_version: str = "1.0"
    clpg_version: str = "0.1.0"
    created_at: datetime
    decision: ParticipationDecision
    reason_codes: list[ReasonCode]
    input_digests: dict[str, str]
    checks: list[CheckResult]
    decision_trace: DecisionTrace
    decision_digest: str
    receipt_digest: str

    @model_validator(mode="after")
    def receipt_is_publicly_verifiable(self) -> ParticipationReceipt:
        if set(self.input_digests) != RECEIPT_INPUT_DIGEST_KEYS:
            raise ValueError("input_digests must contain the fixed CLPG input key set")
        for key, digest in self.input_digests.items():
            hex_part = digest.removeprefix("sha256:")
            if (
                not digest.startswith("sha256:")
                or len(hex_part) != 64
                or any(char not in "0123456789abcdef" for char in hex_part)
            ):
                raise ValueError(f"input digest for {key} must use sha256:<hex>")
        if self.decision_trace.steps != self.checks:
            raise ValueError("decision_trace.steps must equal checks")
        return self


class LedgerRecord(CLPGModel):
    schema_version: str = "1.0"
    sequence: int = Field(ge=1)
    previous_record_digest: str | None = None
    receipt: ParticipationReceipt
    receipt_digest: str
    record_digest: str


class LedgerVerificationResult(CLPGModel):
    ok: bool
    records_checked: int = Field(ge=0)
    last_record_digest: str | None = None
    anchored: bool = False
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ConformanceCase(CLPGModel):
    name: str = Field(min_length=1)
    task: TaskSnapshot
    agent: AgentSnapshot
    authority: AuthoritySnapshot
    evidence: EvidenceSnapshot
    uncertainty: UncertaintyEnvelope
    attribution: AttributionState
    budget: CostBudget
    policy: ParticipationPolicy
    expected_decision: ParticipationDecision
    expected_reason_codes: list[ReasonCode] = Field(default_factory=list)
    exact_reason_codes: bool = False
    expected_terminal_rule: str | None = None
