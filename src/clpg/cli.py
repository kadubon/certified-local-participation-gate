"""Typer CLI for CLPG."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from clpg.canonical import canonical_json
from clpg.conformance import run_conformance
from clpg.decision import decide_participation
from clpg.ledger import AppendOnlyLedger, load_json_file
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
from clpg.receipts import CLPG_VERSION, verify_decision_digest, verify_receipt_digest
from clpg.schemas import export_json_schemas

app = typer.Typer(help="Certified Local Participation Gate.")
schema_app = typer.Typer(help="JSON Schema commands.")
ledger_app = typer.Typer(help="Ledger commands.")
conformance_app = typer.Typer(help="Conformance commands.")
app.add_typer(schema_app, name="schema")
app.add_typer(ledger_app, name="ledger")
app.add_typer(conformance_app, name="conformance")
console = Console()


def _print_json(value: Any) -> None:
    console.print(canonical_json(value))


def _load_model(model_type: type[Any], path: Path) -> Any:
    return model_type.model_validate(load_json_file(path))


@app.command()
def version(json_output: bool = typer.Option(False, "--json", help="Emit JSON.")) -> None:
    payload = {"name": "clpg", "version": CLPG_VERSION, "schema_version": "1.0"}
    if json_output:
        _print_json(payload)
    else:
        console.print(f"clpg {CLPG_VERSION}")


@app.command()
def decide(
    task: Path = typer.Option(..., "--task", exists=True, readable=True),
    agent: Path = typer.Option(..., "--agent", exists=True, readable=True),
    authority: Path = typer.Option(..., "--authority", exists=True, readable=True),
    evidence: Path = typer.Option(..., "--evidence", exists=True, readable=True),
    uncertainty: Path = typer.Option(..., "--uncertainty", exists=True, readable=True),
    attribution: Path = typer.Option(..., "--attribution", exists=True, readable=True),
    budget: Path = typer.Option(..., "--budget", exists=True, readable=True),
    policy: Path = typer.Option(..., "--policy", exists=True, readable=True),
    ledger: Path | None = typer.Option(None, "--ledger"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    try:
        receipt = decide_participation(
            task=_load_model(TaskSnapshot, task),
            agent=_load_model(AgentSnapshot, agent),
            authority=_load_model(AuthoritySnapshot, authority),
            evidence=_load_model(EvidenceSnapshot, evidence),
            uncertainty=_load_model(UncertaintyEnvelope, uncertainty),
            attribution=_load_model(AttributionState, attribution),
            budget=_load_model(CostBudget, budget),
            policy=_load_model(ParticipationPolicy, policy),
        )
        if ledger is not None:
            AppendOnlyLedger(ledger).append(receipt)
        if json_output:
            _print_json(receipt)
            return
        table = Table(title="CLPG Decision")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("decision", receipt.decision.value)
        table.add_row("reason_codes", ", ".join(code.value for code in receipt.reason_codes))
        table.add_row("decision_digest", receipt.decision_digest)
        table.add_row("receipt_digest", receipt.receipt_digest)
        console.print(table)
    except ValidationError as exc:
        console.print(f"input validation failed: {exc}", style="red")
        raise typer.Exit(2) from exc
    except Exception as exc:  # noqa: BLE001
        console.print(f"decision failed: {exc}", style="red")
        raise typer.Exit(1) from exc


@schema_app.command("export")
def schema_export(
    output_dir: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    try:
        manifest = export_json_schemas(output_dir)
        if json_output:
            _print_json({"ok": True, "schemas": manifest})
        else:
            console.print(f"exported {len(manifest)} schemas to {output_dir}")
    except Exception as exc:  # noqa: BLE001
        console.print(f"schema export failed: {exc}", style="red")
        raise typer.Exit(1) from exc


@ledger_app.command("verify")
def ledger_verify(
    ledger_path: Path,
    expect_head: str | None = typer.Option(None, "--expect-head"),
    expect_count: int | None = typer.Option(None, "--expect-count"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    result = AppendOnlyLedger(ledger_path).verify(
        expect_head=expect_head,
        expect_count=expect_count,
    )
    if json_output:
        _print_json(result)
    else:
        console.print(
            f"ok={result.ok} records_checked={result.records_checked} "
            f"last_record_digest={result.last_record_digest}"
        )
        for error in result.errors:
            console.print(error, style="red")
        for warning in result.warnings:
            console.print(warning, style="yellow")
    if not result.ok:
        raise typer.Exit(1)


@conformance_app.command("run")
def conformance_run(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    try:
        result = run_conformance(path)
        if json_output:
            _print_json(result)
        else:
            console.print(
                f"ok={result['ok']} passed={len(result['passed'])} failed={len(result['failed'])}"
            )
            for failure in result["failed"]:
                console.print(failure, style="red")
        if not result["ok"]:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        console.print(f"conformance failed: {exc}", style="red")
        raise typer.Exit(1) from exc


@app.command()
def explain(
    receipt: Path = typer.Option(..., "--receipt", exists=True, readable=True),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    try:
        loaded = ParticipationReceipt.model_validate(load_json_file(receipt))
        digest_status = {
            "decision_digest_valid": verify_decision_digest(loaded),
            "receipt_digest_valid": verify_receipt_digest(loaded),
        }
        if json_output:
            _print_json({"receipt": loaded, **digest_status})
            return
        console.print(f"decision: {loaded.decision.value}")
        console.print(f"terminal_rule: {loaded.decision_trace.terminal_rule}")
        console.print(f"decision_digest_valid: {digest_status['decision_digest_valid']}")
        console.print(f"receipt_digest_valid: {digest_status['receipt_digest_valid']}")
        for check in loaded.checks:
            status = "pass" if check.passed else "fail"
            reason = check.reason_code.value if check.reason_code else ""
            console.print(f"{status} {check.name} {reason}")
    except ValidationError as exc:
        console.print(f"receipt validation failed: {exc}", style="red")
        raise typer.Exit(2) from exc
    except Exception as exc:  # noqa: BLE001
        console.print(f"explain failed: {exc}", style="red")
        raise typer.Exit(1) from exc
