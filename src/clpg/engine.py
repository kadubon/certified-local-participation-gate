"""Shared decision-engine primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from clpg.digest import sha256_digest
from clpg.enums import ClaimRole, ParticipationDecision, PolicyMode, ReasonCode
from clpg.models import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    CheckResult,
    CostBudget,
    EvidenceSnapshot,
    ParticipationPolicy,
    ParticipationReceipt,
    TaskSnapshot,
    UncertaintyEnvelope,
)
from clpg.receipts import create_receipt


@dataclass(frozen=True)
class DecisionOutcome:
    decision: ParticipationDecision
    reason_codes: list[ReasonCode]
    terminal_rule: str


class DecisionContext:
    def __init__(
        self,
        *,
        task: TaskSnapshot,
        agent: AgentSnapshot,
        authority: AuthoritySnapshot,
        evidence: EvidenceSnapshot,
        uncertainty: UncertaintyEnvelope,
        attribution: AttributionState,
        budget: CostBudget,
        policy: ParticipationPolicy,
        now: datetime,
    ) -> None:
        self.task = task
        self.agent = agent
        self.authority = authority
        self.evidence = evidence
        self.uncertainty = uncertainty
        self.attribution = attribution
        self.budget = budget
        self.policy = policy
        self.now = now
        self.checks: list[CheckResult] = []
        self.input_digests = {
            "task": sha256_digest(task),
            "agent": sha256_digest(agent),
            "authority": sha256_digest(authority),
            "evidence": sha256_digest(evidence),
            "uncertainty": sha256_digest(uncertainty),
            "attribution": sha256_digest(attribution),
            "budget": sha256_digest(budget),
            "policy": sha256_digest(policy),
        }

    @property
    def requested_role(self) -> ClaimRole:
        return self.task.claim.requested_role if self.task.claim else self.task.requested_role

    @property
    def requested_action(self) -> str:
        return self.task.claim.requested_action if self.task.claim else self.task.requested_action

    @property
    def protected_action(self) -> bool:
        claim_protected = self.task.claim.protected_action if self.task.claim else False
        return self.task.protected_action or claim_protected

    @property
    def external_effect(self) -> bool:
        return self.task.claim.external_effect if self.task.claim else False

    def add_check(
        self,
        name: str,
        passed: bool,
        reason_code: ReasonCode | None = None,
        observed: dict[str, Any] | None = None,
        threshold: dict[str, Any] | None = None,
    ) -> None:
        self.checks.append(
            CheckResult(
                name=name,
                passed=passed,
                reason_code=reason_code,
                observed=observed or {},
                threshold=threshold or {},
            )
        )

    def terminal(self, outcome: DecisionOutcome) -> ParticipationReceipt:
        return create_receipt(
            decision=outcome.decision,
            reason_codes=list(dict.fromkeys(outcome.reason_codes)),
            input_digests=self.input_digests,
            checks=self.checks,
            terminal_rule=outcome.terminal_rule,
            created_at=self.now,
        )

    def can_verify(self) -> tuple[bool, ReasonCode]:
        portfolio = self.evidence.verification_portfolio
        scalar_capacity = (
            self.agent.verification_capability
            or self.evidence.verification_available
            or self.evidence.verification_capacity > 0
        )
        if self.budget.verification_cost_upper_bound > self.budget.budget_remaining:
            return False, ReasonCode.VERIFICATION_COST_EXCEEDS_BUDGET
        if self.policy.mode == PolicyMode.STRICT:
            if portfolio is None:
                return False, ReasonCode.VERIFICATION_CAPACITY_MISSING
            if (
                not portfolio.ambient_target_classes
                or not portfolio.ambient_response_actions
                or not portfolio.ambient_verifier_families
            ):
                return False, ReasonCode.VERIFICATION_AMBIENT_MODEL_MISSING
            if portfolio.portfolio_certificate_digest is None:
                return False, ReasonCode.VERIFICATION_PORTFOLIO_CERTIFICATE_MISSING
            if not portfolio.ambiguity_nonempty:
                return False, ReasonCode.VERIFICATION_AMBIGUITY_EMPTY
            if not portfolio.safe_decision_set_nonempty:
                return False, ReasonCode.VERIFICATION_SAFE_SET_EMPTY
            if (
                portfolio.slot_budget <= 0
                or not portfolio.available_verifier_families
                or not portfolio.target_classes
                or not portfolio.response_actions
            ):
                return False, ReasonCode.VERIFICATION_CAPACITY_MISSING
            return True, ReasonCode.VERIFICATION_CAPACITY_AVAILABLE
        if scalar_capacity or (portfolio is not None and portfolio.slot_budget > 0):
            return True, ReasonCode.VERIFICATION_CAPACITY_AVAILABLE
        return False, ReasonCode.VERIFICATION_CAPACITY_MISSING

    def degrade(self, reason: ReasonCode, rule: str) -> DecisionOutcome:
        verify_possible, verify_reason = self.can_verify()
        self.add_check(
            "verification_available_for_degradation",
            verify_possible,
            verify_reason,
            observed={"verification_possible": verify_possible},
        )
        if self.policy.verify_on_ineligible_snapshot and verify_possible:
            return DecisionOutcome(
                ParticipationDecision.VERIFY,
                [reason, ReasonCode.VERIFICATION_CAPACITY_AVAILABLE],
                rule,
            )
        return DecisionOutcome(ParticipationDecision.WITHDRAW, [reason, verify_reason], rule)

    def can_assist(self) -> bool:
        if not self.policy.allow_assist:
            return False
        tokens = set(self.agent.assist_capabilities)
        return (
            "*" in tokens or self.requested_action in tokens or self.requested_role.value in tokens
        )

    def has_direct_capability(self) -> bool:
        tokens = set(self.agent.capabilities)
        return (
            "*" in tokens or self.requested_action in tokens or self.requested_role.value in tokens
        )


def coerce_now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now
