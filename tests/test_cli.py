from pathlib import Path

from clpg_test_helpers import full_inputs
from typer.testing import CliRunner

from clpg.canonical import canonical_json
from clpg.cli import app
from clpg.decision import decide_participation

runner = CliRunner()


def write_model(path: Path, model: object) -> None:
    path.write_text(canonical_json(model), encoding="utf-8")


def test_version_json() -> None:
    result = runner.invoke(app, ["version", "--json"])
    assert result.exit_code == 0
    assert '"version":"0.1.1"' in result.output


def test_decide_json(tmp_path: Path) -> None:
    files = full_inputs()
    args = ["decide"]
    for name, model in files.items():
        path = tmp_path / f"{name}.json"
        write_model(path, model)
        args.extend([f"--{name}", str(path)])
    args.append("--json")
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert '"decision":"act"' in result.output


def test_schema_export_json(tmp_path: Path) -> None:
    result = runner.invoke(app, ["schema", "export", str(tmp_path / "schemas"), "--json"])
    assert result.exit_code == 0
    assert (tmp_path / "schemas" / "TaskSnapshot.schema.json").exists()


def test_conformance_run_json() -> None:
    result = runner.invoke(app, ["conformance", "run", "examples/conformance", "--json"])
    assert result.exit_code == 0
    assert '"ok":true' in result.output


def test_explain_json_reports_digest_validity(tmp_path: Path) -> None:
    files = full_inputs()
    receipt = decide_participation(**files)  # type: ignore[arg-type]
    path = tmp_path / "receipt.json"
    write_model(path, receipt)
    result = runner.invoke(app, ["explain", "--receipt", str(path), "--json"])
    assert result.exit_code == 0
    assert '"decision_digest_valid":true' in result.output
    assert '"receipt_digest_valid":true' in result.output
