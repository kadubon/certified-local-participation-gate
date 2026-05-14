"""Conformance fixture runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clpg.decision import decide_participation
from clpg.exceptions import ConformanceError
from clpg.ledger import load_json_file
from clpg.models import ConformanceCase


def run_conformance(path: str | Path) -> dict[str, Any]:
    root = Path(path)
    if not root.exists():
        raise ConformanceError(f"conformance path does not exist: {root}")

    passed: list[str] = []
    failed: list[str] = []
    for fixture in sorted(root.glob("*.json")):
        is_invalid = fixture.name.endswith(".invalid.json")
        try:
            payload = load_json_file(fixture)
            case = ConformanceCase.model_validate(payload)
            if is_invalid:
                failed.append(f"{fixture.name}: expected invalid but parsed")
                continue
            receipt = decide_participation(
                task=case.task,
                agent=case.agent,
                authority=case.authority,
                evidence=case.evidence,
                uncertainty=case.uncertainty,
                attribution=case.attribution,
                budget=case.budget,
                policy=case.policy,
            )
            expected_reasons = set(case.expected_reason_codes)
            actual_reasons = set(receipt.reason_codes)
            if receipt.decision != case.expected_decision:
                failed.append(
                    f"{fixture.name}: expected {case.expected_decision}, got {receipt.decision}"
                )
            elif case.exact_reason_codes and receipt.reason_codes != case.expected_reason_codes:
                failed.append(
                    f"{fixture.name}: expected exact reasons "
                    f"{[item.value for item in case.expected_reason_codes]}, got "
                    f"{[item.value for item in receipt.reason_codes]}"
                )
            elif not expected_reasons.issubset(actual_reasons):
                failed.append(
                    f"{fixture.name}: missing expected reasons "
                    f"{sorted(item.value for item in expected_reasons - actual_reasons)}"
                )
            elif (
                case.expected_terminal_rule is not None
                and receipt.decision_trace.terminal_rule != case.expected_terminal_rule
            ):
                failed.append(
                    f"{fixture.name}: expected terminal rule {case.expected_terminal_rule}, "
                    f"got {receipt.decision_trace.terminal_rule}"
                )
            else:
                passed.append(fixture.name)
        except ValidationError:
            if is_invalid:
                passed.append(fixture.name)
            else:
                failed.append(f"{fixture.name}: validation failed")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{fixture.name}: {exc}")

    return {
        "ok": not failed,
        "passed": passed,
        "failed": failed,
        "total": len(passed) + len(failed),
    }
