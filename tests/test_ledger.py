from pathlib import Path

import pytest
from clpg_test_helpers import full_inputs

from clpg import AppendOnlyLedger, decide_participation
from clpg.exceptions import LedgerError


def make_receipt(task_id: str):
    kwargs = full_inputs()
    kwargs["task"] = kwargs["task"].model_copy(update={"task_id": task_id})  # type: ignore[union-attr]
    return decide_participation(**kwargs)  # type: ignore[arg-type]


def test_ledger_append_and_verify(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    ledger.append(make_receipt("t1"))
    ledger.append(make_receipt("t2"))
    result = ledger.verify()
    assert result.ok
    assert result.records_checked == 2
    assert not result.anchored
    assert result.warnings


def test_ledger_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(path)
    ledger.append(make_receipt("t1"))
    path.write_text(path.read_text(encoding="utf-8").replace("act", "verify", 1), encoding="utf-8")
    result = ledger.verify()
    assert not result.ok
    assert result.errors


def test_ledger_anchor_detects_tail_deletion(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(path)
    ledger.append(make_receipt("t1"))
    second = ledger.append(make_receipt("t2"))
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(lines[0] + "\n", encoding="utf-8")
    result = ledger.verify(expect_head=second.record_digest, expect_count=2)
    assert not result.ok


def test_ledger_append_rejects_tampered_receipt(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    receipt = make_receipt("t1")
    tampered = receipt.model_copy(update={"decision_digest": "sha256:" + "1" * 64})
    with pytest.raises(LedgerError):
        ledger.append(tampered)
