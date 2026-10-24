"""The standards documents stay consistent with the tooling (STD-3)."""

from pathlib import Path

from project_standards.standards_docs import check

HOOKS = "repos:\n  - repo: local\n    hooks:\n      - {id: ruff-check, entry: x}\n"


def _docs(tmp_path: Path, *texts: str) -> Path:
    docs = tmp_path / "standards"
    docs.mkdir()
    for number, text in enumerate(texts):
        (docs / f"{number:02}.md").write_text(text)
    return docs


GOOD = """# Rules
| ID | Rule | Enforced by |
|---|---|---|
| COV-1 | Coverage is 100 % | `standards check-suppressions` |
| SEC-PRT-2 | Pipes \\| escaped | review, `ruff-check` |
"""


def test_consistent_documents_pass(tmp_path: Path) -> None:
    hooks = tmp_path / "hooks.yaml"
    hooks.write_text(HOOKS)
    assert check(_docs(tmp_path, GOOD), hooks, ["check-suppressions"]) == []


def test_no_documents_is_an_error(tmp_path: Path) -> None:
    assert "no standards documents" in check(_docs(tmp_path), None, [])[0]


def test_duplicate_ids_and_empty_cells_are_reported(tmp_path: Path) -> None:
    docs = _docs(tmp_path, GOOD, "| COV-1 | again |  |\n")
    errors = check(docs, None, ["check-suppressions"])
    assert any("already defined" in e for e in errors)
    assert any("empty cell" in e for e in errors)


def test_commands_must_exist_and_be_documented(tmp_path: Path) -> None:
    errors = check(_docs(tmp_path, GOOD), None, ["check-new"])
    assert "unknown command `standards check-suppressions`" in errors[0]
    assert "`standards check-new` is not documented" in errors[1]


def test_hooks_must_be_documented(tmp_path: Path) -> None:
    hooks = tmp_path / "hooks.yaml"
    hooks.write_text(HOOKS.replace("ruff-check", "mystery"))
    errors = check(_docs(tmp_path, GOOD), hooks, ["check-suppressions"])
    assert errors == [f"hook `mystery` ({hooks}) is not documented in {tmp_path / 'standards'}"]


def test_missing_hook_config_is_skipped(tmp_path: Path) -> None:
    assert check(_docs(tmp_path, GOOD), tmp_path / "absent.yaml", ["check-suppressions"]) == []
