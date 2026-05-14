"""Authority scope checks."""

from __future__ import annotations

from datetime import timezone

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ParticipationDecision, ReasonCode


def authority_failure_reason(ctx: DecisionContext) -> ReasonCode | None:
    authority = ctx.authority
    if authority.actor != ctx.agent.agent_id:
        return ReasonCode.AUTHORITY_ACTOR_MISMATCH
    if not authority.valid:
        return ReasonCode.AUTHORITY_MISSING
    if authority.authority_digest is None and not authority.external_receipts:
        return ReasonCode.AUTHORITY_CERTIFICATE_MISSING
    if authority.expires_at is not None:
        expires_at = authority.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= ctx.now:
            return ReasonCode.AUTHORITY_EXPIRED
    if (
        ctx.requested_action not in authority.permitted_actions
        and "*" not in authority.permitted_actions
    ):
        return ReasonCode.AUTHORITY_SCOPE_MISMATCH
    return None


def evaluate_authority(ctx: DecisionContext) -> DecisionOutcome | None:
    authority_required = ctx.policy.strict_authority or ctx.protected_action or ctx.external_effect
    reason = authority_failure_reason(ctx)
    if authority_required and reason is not None:
        ctx.add_check(
            "requested_action_authorized",
            False,
            reason,
            observed={
                "strict_authority": ctx.policy.strict_authority,
                "protected_action": ctx.protected_action,
                "external_effect": ctx.external_effect,
                "requested_action": ctx.requested_action,
                "agent_id": ctx.agent.agent_id,
                "authority_actor": ctx.authority.actor,
                "authority_valid": ctx.authority.valid,
                "authority_digest": ctx.authority.authority_digest,
                "external_receipts": ctx.authority.external_receipts,
                "permitted_actions": ctx.authority.permitted_actions,
            },
        )
        reasons = [reason]
        if ctx.protected_action or ctx.external_effect:
            reasons.insert(0, ReasonCode.PROTECTED_ACTION_WITHOUT_AUTHORITY)
        if ctx.policy.allow_escalate and ctx.policy.escalation_target:
            reasons.append(ReasonCode.ESCALATION_POLICY_SELECTED)
            return DecisionOutcome(
                ParticipationDecision.ESCALATE,
                reasons,
                "authority_escalation",
            )
        return DecisionOutcome(ParticipationDecision.REFUSE, reasons, "authority_missing")
    ctx.add_check(
        "requested_action_authorized",
        True,
        observed={
            "strict_authority": ctx.policy.strict_authority,
            "protected_action": ctx.protected_action,
        },
    )
    return None
