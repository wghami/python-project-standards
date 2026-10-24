"""Silent exclusions are refused (COV-2, TYP-3, LNT-4)."""

from pathlib import Path

import pytest

from project_standards.suppressions import check_files, check_text


def _real(text: str) -> str:
    """Fixtures write ``~`` for ``#`` so this file is not itself a suppression."""
    return text.replace("~", "#")


@pytest.mark.parametrize(
    "line",
    [
        "x = 1  ~ pragma: no cover",
        "if x:  ~ PRAGMA: NO BRANCH",
        "~ ruff: noqa",
        "~ flake8: noqa: E501",
        "x = 1  ~ noqa",
        "x = 1  ~ noqa: E501",
        "x = 1  ~ type: ignore",
        "x = 1  ~ type: ignore[attr-defined]",
        "x = 1  ~ pyright: ignore",
        "x = 1  ~ pyright: ignore[reportAny]",
        "~ pyright: basic",
        "subprocess.run(x)  ~ nosec B603",
    ],
)
def test_forbidden_suppressions_are_reported(line: str) -> None:
    assert check_text(_real(line), "m.py") != []


@pytest.mark.parametrize(
    "line",
    [
        "x = 1  ~ noqa: E501  ~ long URL",
        "x = 1  ~ noqa: S603, S607  ~ fixed binary",
        "x = 1  ~ type: ignore[attr-defined]  ~ stub is wrong upstream",
        "x = 1  ~ pyright: ignore[reportAny]  ~ json payload",
        "message = 'no pragma here'",
    ],
)
def test_justified_suppressions_pass(line: str) -> None:
    assert check_text(_real(line), "m.py") == []


def test_errors_carry_path_and_line_number() -> None:
    assert check_text(_real("ok\nx  ~ noqa"), "pkg/m.py")[0].startswith("pkg/m.py:2:")


def test_only_python_files_are_read(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text(_real("x  ~ noqa\n"))
    stub = tmp_path / "bad.pyi"
    stub.write_text(_real("x: int  ~ type: ignore\n"))
    notes = tmp_path / "notes.md"
    notes.write_text(_real("x  ~ noqa\n"))
    assert len(check_files([bad, stub, notes])) == 2
