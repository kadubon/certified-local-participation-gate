import pytest
from clpg_test_helpers import full_inputs
from pydantic import ValidationError

from clpg import ParticipationReceipt, decide_participation
from clpg.receipts import verify_decision_digest, verify_receipt_digest


def test_receipt_digest_verifies() -> None:
    receipt = decide_participation(
        **full_inputs()  # type: ignore[arg-type]
    )
    assert verify_receipt_digest(receipt)
    assert verify_decision_digest(receipt)
    assert set(receipt.input_digests) == {
        "task",
        "agent",
        "authority",
        "evidence",
        "uncertainty",
        "attribution",
        "budget",
        "policy",
    }


def test_decision_digest_stable_for_same_created_at() -> None:
    kwargs = full_inputs()
    first = decide_participation(**kwargs)
    second = decide_participation(**kwargs)
    assert first.decision_digest == second.decision_digest


def test_decision_digest_verification_detects_tamper() -> None:
    receipt = decide_participation(**full_inputs())  # type: ignore[arg-type]
    tampered = receipt.model_copy(update={"decision_digest": "sha256:" + "1" * 64})
    assert not verify_decision_digest(tampered)


def test_receipt_rejects_missing_input_digest_key() -> None:
    receipt = decide_participation(**full_inputs())  # type: ignore[arg-type]
    payload = receipt.model_dump(mode="json")
    payload["input_digests"].pop("task")
    with pytest.raises(ValidationError):
        ParticipationReceipt.model_validate(payload)


def test_receipt_rejects_trace_check_mismatch() -> None:
    receipt = decide_participation(**full_inputs())  # type: ignore[arg-type]
    payload = receipt.model_dump(mode="json")
    payload["decision_trace"]["steps"] = []
    with pytest.raises(ValidationError):
        ParticipationReceipt.model_validate(payload)
