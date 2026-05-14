"""Deterministic participation decision orchestrator."""

from __future__ import annotations

from datetime import datetime

from clpg.authority import evaluate_authority
from clpg.claim import evaluate_claim
from clpg.consistency import evaluate_public_state_consistency
from clpg.controller import evaluate_controller_certificate
from clpg.corroboration import evaluate_corroboration
from clpg.eligibility import evaluate_eligibility
from clpg.engine import DecisionContext, DecisionOutcome, coerce_now
from clpg.enums import ClaimRole, ParticipationDecision, ReasonCode
from clpg.evidence import evaluate_evidence
from clpg.feasibility import evaluate_feasibility
from clpg.lineage import evaluate_certificate_lineage
from clpg.models import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    CostBudget,
    EvidenceSnapshot,
    ParticipationPolicy,
    ParticipationReceipt,
    TaskSnapshot,
    UncertaintyEnvelope,
)
from clpg.risk import evaluate_risk
from clpg.verification import requested_verify_outcome


def decide_participation(
    *,
    task: TaskSnapshot,
    agent: AgentSnapshot,
    authority: AuthoritySnapshot,
    evidence: EvidenceSnapshot,
    uncertainty: UncertaintyEnvelope,
    attribution: AttributionState,
    budget: CostBudget,
    policy: ParticipationPolicy,
    now: datetime | None = None,
) -> ParticipationReceipt:
    """Evaluate the fail-closed local participation gate over declared inputs."""

    ctx = DecisionContext(
        task=task,
        agent=agent,
        authority=authority,
        evidence=evidence,
        uncertainty=uncertainty,
        attribution=attribution,
        budget=budget,
        policy=policy,
        now=coerce_now(now),
    )

    if policy.disallow_task:
        ctx.add_check(
            "policy_allows_task",
            False,
            ReasonCode.POLICY_DISALLOWS_TASK,
            observed={"policy_disallow_task": True},
        )
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.REFUSE,
                [ReasonCode.POLICY_DISALLOWS_TASK],
                "policy_disallows_task",
            )
        )
    ctx.add_check("policy_allows_task", True, observed={"policy_disallow_task": False})

    if task.disallowed:
        ctx.add_check(
            "task_not_marked_disallowed",
            False,
            ReasonCode.TASK_MARKED_DISALLOWED,
            observed={"task_disallowed": True},
        )
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.REFUSE,
                [ReasonCode.TASK_MARKED_DISALLOWED, ReasonCode.POLICY_DISALLOWS_TASK],
                "task_marked_disallowed",
            )
        )
    ctx.add_check("task_not_marked_disallowed", True, observed={"task_disallowed": False})

    for evaluator in (
        evaluate_claim,
        evaluate_authority,
        evaluate_eligibility,
        evaluate_public_state_consistency,
        evaluate_feasibility,
        evaluate_certificate_lineage,
        evaluate_controller_certificate,
    ):
        outcome = evaluator(ctx)
        if outcome is not None:
            return ctx.terminal(outcome)

    if ctx.requested_role == ClaimRole.VERIFY:
        return ctx.terminal(requested_verify_outcome(ctx))

    if ctx.requested_role == ClaimRole.WITHDRAW:
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.WITHDRAW,
                [ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
                "requested_withdraw",
            )
        )

    if ctx.requested_role == ClaimRole.EXIT:
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.EXIT,
                [ReasonCode.EXIT_CONDITIONS_SATISFIED],
                "requested_exit",
            )
        )

    assist_possible = ctx.can_assist()
    if ctx.requested_role == ClaimRole.ASSIST:
        ctx.add_check(
            "requested_assist_possible",
            assist_possible,
            ReasonCode.CAPABILITY_PARTIAL_ASSIST_POSSIBLE
            if assist_possible
            else ReasonCode.CAPABILITY_MISSING,
            observed={"assist_possible": assist_possible},
        )
        if assist_possible:
            return ctx.terminal(
                DecisionOutcome(
                    ParticipationDecision.ASSIST,
                    [
                        ReasonCode.CAPABILITY_PARTIAL_ASSIST_POSSIBLE,
                        ReasonCode.ASSIST_AUTHORITY_NOT_EXPANDED,
                    ],
                    "requested_assist",
                )
            )
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.WITHDRAW,
                [ReasonCode.CAPABILITY_MISSING, ReasonCode.WITHDRAW_CONDITIONS_SATISFIED],
                "requested_assist_unavailable",
            )
        )

    if ctx.requested_role == ClaimRole.CONTINUE:
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.ACT,
                [ReasonCode.CONTINUE_CONDITIONS_SATISFIED],
                "continue_conditions_satisfied",
            )
        )

    for evaluator in (evaluate_evidence, evaluate_corroboration, evaluate_risk):
        outcome = evaluator(ctx)
        if outcome is not None:
            return ctx.terminal(outcome)

    if not ctx.has_direct_capability():
        ctx.add_check(
            "direct_capability_available",
            False,
            ReasonCode.CAPABILITY_MISSING,
            observed={
                "capabilities": agent.capabilities,
                "requested_action": ctx.requested_action,
            },
        )
        if assist_possible:
            return ctx.terminal(
                DecisionOutcome(
                    ParticipationDecision.ASSIST,
                    [
                        ReasonCode.CAPABILITY_MISSING,
                        ReasonCode.CAPABILITY_PARTIAL_ASSIST_POSSIBLE,
                        ReasonCode.ASSIST_AUTHORITY_NOT_EXPANDED,
                    ],
                    "capability_missing_assist_possible",
                )
            )
        verify_possible, verify_reason = ctx.can_verify()
        if verify_possible:
            return ctx.terminal(
                DecisionOutcome(
                    ParticipationDecision.VERIFY,
                    [ReasonCode.CAPABILITY_MISSING, ReasonCode.VERIFICATION_CAPACITY_AVAILABLE],
                    "capability_missing_verify_possible",
                )
            )
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.WITHDRAW,
                [ReasonCode.CAPABILITY_MISSING, verify_reason],
                "capability_missing",
            )
        )
    ctx.add_check("direct_capability_available", True)

    if uncertainty.success_lower_bound < policy.min_success_lower_bound_for_act:
        ctx.add_check(
            "success_lower_bound_sufficient",
            False,
            ReasonCode.SUCCESS_LOWER_BOUND_INSUFFICIENT,
            observed={"success_lower_bound": uncertainty.success_lower_bound},
            threshold={
                "min_success_lower_bound_for_act": policy.min_success_lower_bound_for_act
            },
        )
        verify_possible, _verify_reason = ctx.can_verify()
        if verify_possible:
            return ctx.terminal(
                DecisionOutcome(
                    ParticipationDecision.VERIFY,
                    [
                        ReasonCode.SUCCESS_LOWER_BOUND_INSUFFICIENT,
                        ReasonCode.VERIFICATION_CAPACITY_AVAILABLE,
                    ],
                    "success_lower_bound_insufficient",
                )
            )
        if assist_possible:
            return ctx.terminal(
                DecisionOutcome(
                    ParticipationDecision.ASSIST,
                    [
                        ReasonCode.SUCCESS_LOWER_BOUND_INSUFFICIENT,
                        ReasonCode.CAPABILITY_PARTIAL_ASSIST_POSSIBLE,
                        ReasonCode.ASSIST_AUTHORITY_NOT_EXPANDED,
                    ],
                    "success_lower_bound_insufficient_assist",
                )
            )
        return ctx.terminal(
            DecisionOutcome(
                ParticipationDecision.WITHDRAW,
                [
                    ReasonCode.SUCCESS_LOWER_BOUND_INSUFFICIENT,
                    ReasonCode.WITHDRAW_CONDITIONS_SATISFIED,
                ],
                "success_lower_bound_insufficient_withdraw",
            )
        )
    ctx.add_check("success_lower_bound_sufficient", True)

    return ctx.terminal(
        DecisionOutcome(
            ParticipationDecision.ACT,
            [ReasonCode.ACT_CONDITIONS_SATISFIED],
            "act_conditions_satisfied",
        )
    )
