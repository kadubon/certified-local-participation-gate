"""Feasibility-mask checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ClaimRole, ParticipationDecision, ReasonCode


def _scope_failure_outcome(ctx: DecisionContext, reason: ReasonCode, rule: str) -> DecisionOutcome:
    if ctx.task.unrecoverable_scope_failure and ctx.agent.can_exit:
        return DecisionOutcome(
            ParticipationDecision.EXIT,
            [reason, ReasonCode.EXIT_CONDITIONS_SATISFIED],
            rule,
        )
    return DecisionOutcome(
        ParticipationDecision.WITHDRAW,
        [reason, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
        rule,
    )


def _legacy_roles(ctx: DecisionContext) -> list[ClaimRole]:
    return ctx.task.feasible_roles


def _legacy_actions(ctx: DecisionContext) -> list[str]:
    return ctx.task.feasible_actions or [ctx.requested_action]


def evaluate_feasibility(ctx: DecisionContext) -> DecisionOutcome | None:
    model = ctx.task.ambient_model
    if model is None and not ctx.policy.allow_implicit_feasible_actions:
        ctx.add_check(
            "ambient_action_model_declared",
            False,
            ReasonCode.AMBIENT_ACTION_MODEL_MISSING,
        )
        return ctx.degrade(
            ReasonCode.AMBIENT_ACTION_MODEL_MISSING,
            "ambient_action_model_missing",
        )
    ctx.add_check("ambient_action_model_declared", True)

    feasible_roles = model.feasible_roles if model else _legacy_roles(ctx)
    feasible_actions = model.feasible_actions if model else _legacy_actions(ctx)
    if not feasible_roles or not feasible_actions:
        ctx.add_check(
            "feasibility_mask_declared",
            False,
            ReasonCode.FEASIBILITY_MASK_MISSING,
        )
        return ctx.degrade(ReasonCode.FEASIBILITY_MASK_MISSING, "feasibility_mask_missing")
    ctx.add_check("feasibility_mask_declared", True)

    if ctx.requested_role not in feasible_roles:
        ctx.add_check(
            "requested_role_feasible",
            False,
            ReasonCode.ROLE_NOT_FEASIBLE,
            observed={"requested_role": ctx.requested_role},
        )
        return _scope_failure_outcome(ctx, ReasonCode.ROLE_NOT_FEASIBLE, "role_not_feasible")
    ctx.add_check("requested_role_feasible", True)

    if ctx.requested_action not in feasible_actions:
        ctx.add_check(
            "requested_action_feasible",
            False,
            ReasonCode.ACTION_NOT_FEASIBLE,
            observed={"requested_action": ctx.requested_action},
        )
        return _scope_failure_outcome(
            ctx, ReasonCode.ACTION_NOT_FEASIBLE, "action_not_feasible"
        )
    ctx.add_check("requested_action_feasible", True)
    return None
