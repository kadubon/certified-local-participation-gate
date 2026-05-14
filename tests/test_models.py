import pytest
from pydantic import ValidationError

from clpg import (
    AmbientActionModel,
    ClaimRole,
    ParticipationPolicy,
    TaskSnapshot,
    UncertaintyEnvelope,
    VerificationPortfolioSnapshot,
)


def test_task_snapshot_defaults() -> None:
    task = TaskSnapshot(task_id="t1")
    assert task.requested_role.value == "act"
    assert task.service_envelope.certificates_verified is False


def test_policy_escalation_requires_target() -> None:
    with pytest.raises(ValidationError):
        ParticipationPolicy(allow_escalate=True)


def test_uncertainty_bounds_validate() -> None:
    with pytest.raises(ValidationError):
        UncertaintyEnvelope(success_lower_bound=1.1)


def test_ambient_model_rejects_duplicates() -> None:
    with pytest.raises(ValidationError):
        AmbientActionModel(
            ambient_actions=["act", "act"],
            feasible_actions=["act"],
            ambient_roles=[ClaimRole.ACT],
            feasible_roles=[ClaimRole.ACT],
            feasibility_mask_digest="sha256:" + "0" * 64,
        )


def test_ambient_model_rejects_null_claim_role() -> None:
    with pytest.raises(ValidationError):
        AmbientActionModel(
            ambient_actions=["act"],
            feasible_actions=["act"],
            ambient_roles=[ClaimRole.ACT, ClaimRole.NONE],
            feasible_roles=[ClaimRole.ACT],
            feasibility_mask_digest="sha256:" + "0" * 64,
        )


def test_verification_portfolio_rejects_non_ambient_family() -> None:
    with pytest.raises(ValidationError):
        VerificationPortfolioSnapshot(
            ambient_target_classes=["complete"],
            ambient_response_actions=["request_evidence"],
            ambient_verifier_families=["local-checker"],
            target_classes=["complete"],
            response_actions=["request_evidence"],
            available_verifier_families=["unknown-checker"],
        )
