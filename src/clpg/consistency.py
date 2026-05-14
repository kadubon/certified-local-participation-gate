"""Public-state consistency checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import PolicyMode, ReasonCode


def evaluate_public_state_consistency(ctx: DecisionContext) -> DecisionOutcome | None:
    if ctx.policy.mode == PolicyMode.DEMO or ctx.task.public_state is None:
        return None

    public_state = ctx.task.public_state
    if public_state.budget_remaining != ctx.budget.budget_remaining:
        ctx.add_check(
            "public_state_budget_matches_budget",
            False,
            ReasonCode.PUBLIC_STATE_BUDGET_MISMATCH,
            observed={
                "public_budget_remaining": public_state.budget_remaining,
                "budget_remaining": ctx.budget.budget_remaining,
            },
        )
        return ctx.degrade(
            ReasonCode.PUBLIC_STATE_BUDGET_MISMATCH,
            "public_state_budget_mismatch",
        )
    ctx.add_check("public_state_budget_matches_budget", True)

    if public_state.remaining_horizon != ctx.task.remaining_horizon:
        ctx.add_check(
            "public_state_horizon_matches_task",
            False,
            ReasonCode.PUBLIC_STATE_HORIZON_MISMATCH,
            observed={
                "public_remaining_horizon": public_state.remaining_horizon,
                "task_remaining_horizon": ctx.task.remaining_horizon,
            },
        )
        return ctx.degrade(
            ReasonCode.PUBLIC_STATE_HORIZON_MISMATCH,
            "public_state_horizon_mismatch",
        )
    ctx.add_check("public_state_horizon_matches_task", True)
    return None
