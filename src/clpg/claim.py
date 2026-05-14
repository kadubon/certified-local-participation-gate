"""Claim-level participation checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ClaimRole, ParticipationDecision, PolicyMode, ReasonCode

TARGET_REQUIRED_ROLES = {ClaimRole.ASSIST, ClaimRole.VERIFY, ClaimRole.CONTINUE}


def evaluate_claim(ctx: DecisionContext) -> DecisionOutcome | None:
    claim = ctx.task.claim
    if (
        ctx.policy.mode == PolicyMode.STRICT
        and ctx.policy.require_claim_snapshot
        and claim is None
    ):
        ctx.add_check(
            "claim_snapshot_declared",
            False,
            ReasonCode.CLAIM_SNAPSHOT_MISSING,
        )
        return ctx.degrade(ReasonCode.CLAIM_SNAPSHOT_MISSING, "claim_snapshot_missing")
    ctx.add_check(
        "claim_snapshot_declared",
        True,
        observed={"claim_snapshot_declared": claim is not None},
    )

    if ctx.requested_role == ClaimRole.NONE:
        ctx.add_check(
            "non_null_claim_submitted",
            False,
            ReasonCode.NULL_CLAIM_WITHDRAWN,
            observed={"requested_role": ctx.requested_role},
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.NULL_CLAIM_WITHDRAWN, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "null_claim_withdrawn",
        )
    ctx.add_check("non_null_claim_submitted", True)

    if claim is None:
        return None

    action_conflicts = (
        ctx.task.requested_action != "act"
        and ctx.task.requested_action != claim.requested_action
    )
    role_conflicts = (
        ctx.task.requested_role != ClaimRole.ACT
        and ctx.task.requested_role != claim.requested_role
    )
    if action_conflicts or role_conflicts:
        ctx.add_check(
            "claim_matches_legacy_task_fields",
            False,
            ReasonCode.CLAIM_LEGACY_FIELD_CONFLICT,
            observed={
                "task_requested_action": ctx.task.requested_action,
                "claim_requested_action": claim.requested_action,
                "task_requested_role": ctx.task.requested_role,
                "claim_requested_role": claim.requested_role,
            },
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [
                ReasonCode.CLAIM_LEGACY_FIELD_CONFLICT,
                ReasonCode.WITHDRAW_CONDITIONS_SATISFIED,
            ],
            "claim_legacy_field_conflict",
        )
    ctx.add_check("claim_matches_legacy_task_fields", True)

    if ctx.task.protected_action and not claim.protected_action:
        ctx.add_check(
            "claim_does_not_weaken_protected_flag",
            False,
            ReasonCode.PROTECTED_FLAG_CONFLICT,
            observed={
                "task_protected_action": ctx.task.protected_action,
                "claim_protected_action": claim.protected_action,
            },
        )
        return DecisionOutcome(
            ParticipationDecision.REFUSE,
            [ReasonCode.PROTECTED_FLAG_CONFLICT],
            "protected_flag_conflict",
        )
    ctx.add_check("claim_does_not_weaken_protected_flag", True)

    if claim.requested_role in TARGET_REQUIRED_ROLES and not claim.target_refs:
        ctx.add_check(
            "claim_target_refs_declared",
            False,
            ReasonCode.CLAIM_TARGET_MISSING,
            observed={"requested_role": claim.requested_role},
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.CLAIM_TARGET_MISSING, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "claim_target_missing",
        )
    ctx.add_check("claim_target_refs_declared", True)

    if claim.budget_demand > ctx.budget.budget_remaining:
        ctx.add_check(
            "claim_budget_within_budget",
            False,
            ReasonCode.CLAIM_BUDGET_EXCEEDS_BUDGET,
            observed={
                "claim_budget_demand": claim.budget_demand,
                "budget_remaining": ctx.budget.budget_remaining,
            },
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.CLAIM_BUDGET_EXCEEDS_BUDGET, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "claim_budget_exceeds_budget",
        )
    ctx.add_check("claim_budget_within_budget", True)

    if claim.stake_demand > ctx.policy.max_stake_demand:
        ctx.add_check(
            "claim_stake_within_policy",
            False,
            ReasonCode.CLAIM_STAKE_EXCEEDS_POLICY,
            observed={"claim_stake_demand": claim.stake_demand},
            threshold={"max_stake_demand": ctx.policy.max_stake_demand},
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.CLAIM_STAKE_EXCEEDS_POLICY, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "claim_stake_exceeds_policy",
        )
    ctx.add_check("claim_stake_within_policy", True)
    return None
