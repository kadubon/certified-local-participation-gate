"""Append-only JSONL ledger for CLPG receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clpg.canonical import canonical_json
from clpg.digest import sha256_digest
from clpg.exceptions import LedgerError
from clpg.models import LedgerRecord, LedgerVerificationResult, ParticipationReceipt
from clpg.receipts import verify_decision_digest, verify_receipt_digest


def _record_digest_payload(record: LedgerRecord) -> dict[str, Any]:
    return record.model_dump(mode="json", exclude={"record_digest"})


def compute_record_digest(record: LedgerRecord) -> str:
    return sha256_digest(_record_digest_payload(record))


class AppendOnlyLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read_records(self) -> list[LedgerRecord]:
        if not self.path.exists():
            return []
        records: list[LedgerRecord] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(LedgerRecord.model_validate_json(stripped))
                except Exception as exc:  # noqa: BLE001
                    message = f"invalid ledger record at line {line_number}: {exc}"
                    raise LedgerError(message) from exc
        return records

    def append(self, receipt: ParticipationReceipt) -> LedgerRecord:
        if not verify_decision_digest(receipt):
            raise LedgerError("decision digest mismatch")
        if not verify_receipt_digest(receipt):
            raise LedgerError("receipt digest mismatch")
        verification = self.verify()
        if not verification.ok:
            raise LedgerError("; ".join(verification.errors))
        sequence = verification.records_checked + 1
        record = LedgerRecord(
            sequence=sequence,
            previous_record_digest=verification.last_record_digest,
            receipt=receipt,
            receipt_digest=receipt.receipt_digest,
            record_digest="",
        )
        record = record.model_copy(update={"record_digest": compute_record_digest(record)})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json(record))
            handle.write("\n")
        return record

    def verify(
        self, *, expect_head: str | None = None, expect_count: int | None = None
    ) -> LedgerVerificationResult:
        errors: list[str] = []
        warnings: list[str] = []
        last_digest: str | None = None
        records_checked = 0
        if not self.path.exists():
            if expect_count not in (None, 0):
                errors.append("ledger is missing but expected count is nonzero")
            if expect_head is not None:
                errors.append("ledger is missing but expected head was supplied")
            return LedgerVerificationResult(
                ok=not errors,
                records_checked=0,
                anchored=expect_head is not None or expect_count is not None,
                errors=errors,
                warnings=[] if errors else ["ledger is empty and unanchored"],
            )
        try:
            records = self._read_records()
        except LedgerError as exc:
            return LedgerVerificationResult(ok=False, records_checked=0, errors=[str(exc)])
        for index, record in enumerate(records, start=1):
            records_checked += 1
            if record.sequence != index:
                errors.append(f"line {index}: sequence {record.sequence} does not match {index}")
            if record.previous_record_digest != last_digest:
                errors.append(f"line {index}: previous_record_digest mismatch")
            if record.receipt_digest != record.receipt.receipt_digest:
                errors.append(f"line {index}: receipt_digest field mismatch")
            if not verify_decision_digest(record.receipt):
                errors.append(f"line {index}: decision digest mismatch")
            if not verify_receipt_digest(record.receipt):
                errors.append(f"line {index}: receipt digest mismatch")
            expected_record_digest = compute_record_digest(record)
            if expected_record_digest != record.record_digest:
                errors.append(f"line {index}: record digest mismatch")
            last_digest = record.record_digest
        if expect_count is not None and expect_count != records_checked:
            errors.append(f"expected count {expect_count} but found {records_checked}")
        if expect_head is not None and expect_head != last_digest:
            errors.append("expected head digest mismatch")
        anchored = expect_count is not None or expect_head is not None
        if not anchored:
            warnings.append(
                "ledger verification is unanchored; whole-ledger regeneration or tail "
                "deletion requires an expected head or count to detect"
            )
        return LedgerVerificationResult(
            ok=not errors,
            records_checked=records_checked,
            last_record_digest=last_digest,
            anchored=anchored,
            errors=errors,
            warnings=warnings,
        )


def load_json_file(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)
