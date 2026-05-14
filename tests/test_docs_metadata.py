from pathlib import Path

from clpg.receipts import CLPG_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_citation_cff_distinguishes_software_from_source_paper() -> None:
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    lines = cff.splitlines()
    assert 'version: "0.1.1"' in cff
    assert 'doi: "10.5281/zenodo.19394600"' in cff
    assert "references:" in cff
    assert not any(line.startswith("doi:") for line in lines)


def test_public_markdown_files_are_not_single_giant_lines() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        *sorted((ROOT / "docs").glob("*.md")),
    ]
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) > 1, f"{path} should not be a single-line document"
        assert max(len(line) for line in lines) <= 320, f"{path} has an oversized line"


def test_version_metadata_is_0_1_1() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.1.1"' in pyproject
    assert CLPG_VERSION == "0.1.1"
