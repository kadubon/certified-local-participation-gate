from __future__ import annotations

from datetime import datetime, timezone

from clpg import (
    AgentSnapshot,
    AmbientActionModel,
    AttributionState,
    AuditedParticipationInterface,
    AuthoritySnapshot,
    ClaimSnapshot,
    ControllerCertificateSnapshot,
    CorroborationSnapshot,
    CostBudget,
    EvidenceSnapshot,
    ParticipationPolicy,
    PublicCoordinationState,
    TaskSnapshot,
    UncertaintyEnvelope,
    VerificationPortfolioSnapshot,
)
from clpg.enums import ClaimRole

DIGEST = "sha256:" + "0" * 64
FUTURE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def public_state() -> PublicCoordinationState:
    return PublicCoordinationState(
        budget_remaining=10,
        remaining_horizon=1,
        verification_reserve=2,
        trace_digest=DIGEST,
        queue_digest=DIGEST,
        role_ledger_digest=DIGEST,
        linkage_graph_digest=DIGEST,
        provenance_summary_digest=DIGEST,
    )


def ambient_model(action: str = "act") -> AmbientActionModel:
    roles = [
        ClaimRole.ACT,
        ClaimRole.ASSIST,
        ClaimRole.VERIFY,
        ClaimRole.WITHDRAW,
        ClaimRole.EXIT,
        ClaimRole.CONTINUE,
    ]
    return AmbientActionModel(
        ambient_actions=["act", "write_file", "delete_remote", "continue"],
        feasible_actions=[action],
        ambient_roles=roles,
        feasible_roles=roles,
        feasibility_mask_digest=DIGEST,
    )


def participation_interface() -> AuditedParticipationInterface:
    return AuditedParticipationInterface(
        protocol_state_id="q.local",
        interface_digest=DIGEST,
        certificate_digests=[DIGEST],
        comparison_class_digest=DIGEST,
        deviation_table_digest=DIGEST,
        proxy_gain_table_digest=DIGEST,
        baseline_interval_digest=DIGEST,
        coverage_certificate_digest=DIGEST,
        stability_certificate_digest=DIGEST,
        omitted_deviation_certificate_digest=DIGEST,
    )


def verification_portfolio() -> VerificationPortfolioSnapshot:
    return VerificationPortfolioSnapshot(
        ambient_target_classes=["complete", "incomplete"],
        ambient_response_actions=["request_evidence"],
        ambient_verifier_families=["local-checker"],
        target_classes=["complete", "incomplete"],
        response_actions=["request_evidence"],
        available_verifier_families=["local-checker"],
        slot_budget=1,
        ambiguity_nonempty=True,
        safe_decision_set_nonempty=True,
        portfolio_certificate_digest=DIGEST,
    )


def controller_certificate() -> ControllerCertificateSnapshot:
    return ControllerCertificateSnapshot(
        feasibility_mask_digest=DIGEST,
        controller_certificate_digest=DIGEST,
        loss_model_digest=DIGEST,
        safe_policy_set_nonempty=True,
    )


def corroboration() -> CorroborationSnapshot:
    return CorroborationSnapshot(
        covariance_certificate_digests=[DIGEST],
        active_block_count=1,
        effective_size_lower_bound=1,
        observable_separation_lower_bound=1,
    )


def full_task(action: str = "act", role: ClaimRole = ClaimRole.ACT) -> TaskSnapshot:
    target_roles = {ClaimRole.ASSIST, ClaimRole.VERIFY, ClaimRole.CONTINUE}
    target_refs = ["target.local"] if role in target_roles else []
    return TaskSnapshot(
        task_id="t1",
        requested_action=action,
        requested_role=role,
        service_envelope={
            "certificates_verified": True,
            "expires_at": FUTURE,
            "snapshot_staleness_seconds": 0,
            "posterior_family_nonempty": True,
            "derived_certificate_families_nonempty": True,
            "service_certificate_digests": [DIGEST],
        },
        public_state=public_state(),
        ambient_model=ambient_model(action),
        participation_interface=participation_interface(),
        controller_certificate=controller_certificate(),
        claim=ClaimSnapshot(
            requested_action=action,
            requested_role=role,
            target_refs=target_refs,
        ),
        submitted_profile_digest=DIGEST,
    )


def full_inputs() -> dict[str, object]:
    return {
        "task": full_task(),
        "agent": AgentSnapshot(agent_id="agent", capabilities=["act"], capability_lower_bound=1),
        "authority": AuthoritySnapshot(
            actor="agent",
            permitted_actions=["act"],
            valid=True,
            authority_digest=DIGEST,
        ),
        "evidence": EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
            stabilizability_certificate_digest=DIGEST,
            corroboration=corroboration(),
        ),
        "uncertainty": UncertaintyEnvelope(
            success_lower_bound=1,
            service_faults={"fault_profile_digest": DIGEST},
        ),
        "attribution": AttributionState(
            bundle_partition_digest=DIGEST,
            bundle_contractive_certified=True,
            attribution_complete=True,
        ),
        "budget": CostBudget(budget_remaining=10),
        "policy": ParticipationPolicy(),
    }
