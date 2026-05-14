from clpg.conformance import run_conformance


def test_conformance_fixtures_pass() -> None:
    result = run_conformance("examples/conformance")
    assert result["ok"], result["failed"]
    assert result["total"] == 10
