"""Receipt construction and digest verification."""

from __future__ import annotations

from datetime import datetime, timezone

from clpg.digest import sha256_digest
from clpg.enums import ParticipationDecision, ReasonCode
from clpg.models import CheckResult, DecisionTrace, ParticipationReceipt

CLPG_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def compute_decision_digest(
    *,
    decision: ParticipationDecision,
    reason_codes: list[ReasonCode],
    input_digests: dict[str, str],
    checks: list[CheckResult],
    decision_trace: DecisionTrace,
    schema_version: str = SCHEMA_VERSION,
    clpg_version: str = CLPG_VERSION,
) -> str:
    return sha256_digest(
        {
            "schema_version": schema_version,
            "clpg_version": clpg_version,
            "decision": decision,
            "reason_codes": reason_codes,
            "input_digests": input_digests,
            "checks": checks,
            "decision_trace": decision_trace,
        }
    )


def compute_receipt_digest(receipt: ParticipationReceipt) -> str:
    payload = receipt.model_dump(mode="json", exclude={"receipt_digest"})
    return sha256_digest(payload)


def verify_decision_digest(receipt: ParticipationReceipt) -> bool:
    expected = compute_decision_digest(
        decision=receipt.decision,
        reason_codes=receipt.reason_codes,
        input_digests=receipt.input_digests,
        checks=receipt.checks,
        decision_trace=receipt.decision_trace,
        schema_version=receipt.schema_version,
        clpg_version=receipt.clpg_version,
    )
    return expected == receipt.decision_digest


def create_receipt(
    *,
    decision: ParticipationDecision,
    reason_codes: list[ReasonCode],
    input_digests: dict[str, str],
    checks: list[CheckResult],
    terminal_rule: str,
    created_at: datetime | None = None,
) -> ParticipationReceipt:
    trace = DecisionTrace(terminal_rule=terminal_rule, steps=checks)
    decision_digest = compute_decision_digest(
        decision=decision,
        reason_codes=reason_codes,
        input_digests=input_digests,
        checks=checks,
        decision_trace=trace,
    )
    receipt = ParticipationReceipt(
        schema_version=SCHEMA_VERSION,
        clpg_version=CLPG_VERSION,
        created_at=created_at or now_utc(),
        decision=decision,
        reason_codes=reason_codes,
        input_digests=input_digests,
        checks=checks,
        decision_trace=trace,
        decision_digest=decision_digest,
        receipt_digest="",
    )
    return receipt.model_copy(update={"receipt_digest": compute_receipt_digest(receipt)})


def verify_receipt_digest(receipt: ParticipationReceipt) -> bool:
    return compute_receipt_digest(receipt) == receipt.receipt_digest
