"""Verification feasibility checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ParticipationDecision, ReasonCode


def requested_verify_outcome(ctx: DecisionContext) -> DecisionOutcome:
    verify_possible, verify_reason = ctx.can_verify()
    ctx.add_check(
        "requested_verify_capacity",
        verify_possible,
        verify_reason,
        observed={"verification_possible": verify_possible},
    )
    if verify_possible:
        return DecisionOutcome(
            ParticipationDecision.VERIFY,
            [ReasonCode.VERIFICATION_CAPACITY_AVAILABLE],
            "requested_verify",
        )
    return DecisionOutcome(ParticipationDecision.WITHDRAW, [verify_reason], "requested_verify")
