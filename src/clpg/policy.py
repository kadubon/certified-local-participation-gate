"""Policy defaults and small policy helpers."""

from __future__ import annotations

from clpg.enums import PolicyMode
from clpg.models import ParticipationPolicy


def strict_policy() -> ParticipationPolicy:
    return ParticipationPolicy()


def demo_policy() -> ParticipationPolicy:
    return ParticipationPolicy(
        mode=PolicyMode.DEMO,
        strict_authority=False,
        strict_evidence=False,
        require_claim_snapshot=False,
        require_replayability=False,
        require_public_coordination_state=False,
        require_audited_participation_interface=False,
        require_controller_certificate=False,
        require_explicit_service_expiry=False,
        require_service_certificate_digests=False,
        require_service_fault_certificate=False,
        allow_implicit_feasible_actions=True,
        min_capability_lower_bound_for_act=0.0,
        min_success_lower_bound_for_act=0.0,
        max_harm_upper_bound=0.4,
        max_submission_harm_upper_bound=0.4,
        max_controller_loss_upper_bound=0.7,
        require_attribution=False,
    )
