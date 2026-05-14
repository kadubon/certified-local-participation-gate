"""Risk, cost, and capability-bound checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ParticipationDecision, ReasonCode


def _risk_outcome(
    ctx: DecisionContext, reason: ReasonCode, rule: str, *, exit_allowed: bool
) -> DecisionOutcome:
    if exit_allowed and ctx.policy.exit_on_unrecoverable_risk and ctx.agent.can_exit:
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


def evaluate_risk(ctx: DecisionContext) -> DecisionOutcome | None:
    if ctx.attribution.submission_harm_upper_bound > ctx.policy.max_submission_harm_upper_bound:
        ctx.add_check(
            "submission_harm_within_limit",
            False,
            ReasonCode.SUBMISSION_HARM_EXCEEDS_LIMIT,
            observed={"submission_harm_upper_bound": ctx.attribution.submission_harm_upper_bound},
            threshold={
                "max_submission_harm_upper_bound": ctx.policy.max_submission_harm_upper_bound
            },
        )
        return _risk_outcome(
            ctx,
            ReasonCode.SUBMISSION_HARM_EXCEEDS_LIMIT,
            "submission_harm_exceeds_limit",
            exit_allowed=False,
        )
    ctx.add_check("submission_harm_within_limit", True)

    if ctx.uncertainty.harm_upper_bound > ctx.policy.max_harm_upper_bound:
        ctx.add_check(
            "harm_upper_bound_within_limit",
            False,
            ReasonCode.HARM_UPPER_BOUND_EXCEEDS_LIMIT,
            observed={"harm_upper_bound": ctx.uncertainty.harm_upper_bound},
            threshold={"max_harm_upper_bound": ctx.policy.max_harm_upper_bound},
        )
        return _risk_outcome(
            ctx,
            ReasonCode.HARM_UPPER_BOUND_EXCEEDS_LIMIT,
            "harm_upper_bound_exceeds_limit",
            exit_allowed=True,
        )
    ctx.add_check("harm_upper_bound_within_limit", True)

    if ctx.uncertainty.controller_loss_upper_bound > ctx.policy.max_controller_loss_upper_bound:
        ctx.add_check(
            "controller_loss_within_limit",
            False,
            ReasonCode.CONTROLLER_LOSS_EXCEEDS_LIMIT,
            observed={"controller_loss_upper_bound": ctx.uncertainty.controller_loss_upper_bound},
            threshold={
                "max_controller_loss_upper_bound": ctx.policy.max_controller_loss_upper_bound
            },
        )
        return ctx.degrade(
            ReasonCode.CONTROLLER_LOSS_EXCEEDS_LIMIT,
            "controller_loss_exceeds_limit",
        )
    ctx.add_check("controller_loss_within_limit", True)

    service_fault = ctx.uncertainty.service_faults.max_fault()
    if (
        ctx.policy.require_service_fault_certificate
        and ctx.uncertainty.service_faults.fault_profile_digest is None
    ):
        ctx.add_check(
            "service_fault_profile_certificate_declared",
            False,
            ReasonCode.SERVICE_FAULT_CERTIFICATE_MISSING,
            observed={"max_service_fault": service_fault},
        )
        return ctx.degrade(
            ReasonCode.SERVICE_FAULT_CERTIFICATE_MISSING,
            "service_fault_certificate_missing",
        )
    ctx.add_check("service_fault_profile_certificate_declared", True)

    if service_fault > ctx.policy.max_service_fault:
        ctx.add_check(
            "service_fault_within_budget",
            False,
            ReasonCode.SERVICE_FAULT_BUDGET_EXCEEDED,
            observed={"max_service_fault": service_fault},
            threshold={"max_service_fault": ctx.policy.max_service_fault},
        )
        return ctx.degrade(
            ReasonCode.SERVICE_FAULT_BUDGET_EXCEEDED,
            "service_fault_budget_exceeded",
        )
    ctx.add_check("service_fault_within_budget", True)

    if ctx.agent.capability_lower_bound < ctx.policy.min_capability_lower_bound_for_act:
        ctx.add_check(
            "capability_lower_bound_sufficient",
            False,
            ReasonCode.CAPABILITY_LOWER_BOUND_INSUFFICIENT,
            observed={"capability_lower_bound": ctx.agent.capability_lower_bound},
            threshold={
                "min_capability_lower_bound_for_act": (
                    ctx.policy.min_capability_lower_bound_for_act
                )
            },
        )
        return ctx.degrade(
            ReasonCode.CAPABILITY_LOWER_BOUND_INSUFFICIENT,
            "capability_lower_bound_insufficient",
        )
    ctx.add_check("capability_lower_bound_sufficient", True)

    if ctx.budget.cost_upper_bound > ctx.budget.budget_remaining:
        ctx.add_check(
            "cost_within_budget",
            False,
            ReasonCode.COST_BUDGET_EXCEEDED,
            observed={
                "cost_upper_bound": ctx.budget.cost_upper_bound,
                "budget_remaining": ctx.budget.budget_remaining,
            },
        )
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.COST_BUDGET_EXCEEDED, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "cost_budget_exceeded",
        )
    ctx.add_check("cost_within_budget", True)

    if not ctx.budget.deadline_feasible:
        ctx.add_check("deadline_feasible", False, ReasonCode.DEADLINE_INFEASIBLE)
        return DecisionOutcome(
            ParticipationDecision.WITHDRAW,
            [ReasonCode.DEADLINE_INFEASIBLE, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
            "deadline_infeasible",
        )
    ctx.add_check("deadline_feasible", True)
    return None
