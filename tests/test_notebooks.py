"""Notebooks are one concept each, committed executed, and use only the public API (DOC-12)."""

import json
from pathlib import Path

import pytest

from project_standards.cli import main
from project_standards.notebooks import check

OPENING = "# {n} — Time grid\n\n**Concept:** steps.\n\n**You will learn:** how.\n"


def _md(text: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def _code(
    text: str, count: int | None, outputs: list[dict[str, object]] | None = None
) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": outputs or [],
        "source": text.splitlines(keepends=True),
    }


def _write(directory: Path, name: str, cells: list[dict[str, object]], fmt: int = 4) -> None:
    directory.mkdir(exist_ok=True)
    document: dict[str, object] = {
        "nbformat": fmt,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": cells,
    }
    (directory / name).write_text(json.dumps(document))


def _good(n: str) -> list[dict[str, object]]:
    return [
        _md(OPENING.format(n=n)),
        _code("import demo\ndemo.grid()", 1),
        _code("from demo.time import Grid as G, step", 2),
        _md("**Next:** series."),
    ]


@pytest.fixture
def book(tmp_path: Path) -> Path:
    directory = tmp_path / "notebooks"
    _write(directory, "01-time-grid.ipynb", _good("01"))
    _write(directory, "02-series.ipynb", _good("02"))
    (directory / "README.md").write_text("[a](01-time-grid.ipynb) [b](02-series.ipynb)")
    return directory


def test_good_notebooks_pass(book: Path) -> None:
    assert check(book, "demo") == []


def test_no_notebooks_means_nothing_to_check(tmp_path: Path) -> None:
    assert check(tmp_path / "absent", "demo") == []


def test_index_numbering_and_names(book: Path) -> None:
    (book / "README.md").unlink()
    _write(book, "04-gap.ipynb", _good("04"))
    _write(book, "Bad Name.ipynb", _good("05"))
    assert check(book, "demo") == [
        f"{book / 'README.md'}: missing; it introduces and links every notebook",
        "Bad Name.ipynb: the name must be NN-concept.ipynb (e.g. 01-time-grid.ipynb)",
        f"{book}: notebooks are numbered 01, 02, … without gaps or duplicates",
    ]
    (book / "README.md").write_text("[a](01-time-grid.ipynb)")
    assert f"{book / 'README.md'}: does not link 02-series.ipynb" in check(book, "demo")


def test_opening_and_closing_cells(book: Path) -> None:
    _write(book, "01-time-grid.ipynb", [_md("# Wrong title"), _code("1", 1), _code("2", 2)])
    assert check(book, "demo") == [
        "01-time-grid.ipynb: the first cell is a markdown title '# 01 — <concept>'",
        "01-time-grid.ipynb: the first cell states **Concept:**",
        "01-time-grid.ipynb: the first cell states **You will learn:**",
        "01-time-grid.ipynb: the last cell is markdown and says what comes **Next:**",
    ]


def test_execution_and_private_api(book: Path) -> None:
    error: dict[str, object] = {"output_type": "error", "ename": "E", "evalue": "", "traceback": []}
    _write(
        book,
        "02-series.ipynb",
        [
            _md(OPENING.format(n="02")),
            _code("import demo._internal", 2, [error]),
            _code("from demo.time import _hidden, ok", 1),
            _code("from demo import public as _alias", None),
            _code("   ", 4),
            _md("**Next:** end."),
        ],
    )
    expected = [
        "02-series.ipynb: remove empty code cells",
        (
            "02-series.ipynb: code cells must have run once, top to bottom, in a fresh kernel: "
            "re-run it with `jupyter nbconvert --to notebook --execute --inplace`"
        ),
        "02-series.ipynb: a code cell has an error output",
        "02-series.ipynb: uses private API: demo._internal",
        "02-series.ipynb: uses private API: demo.time import _hidden, ok",
    ]
    assert check(book, "demo") == expected
    assert check(book, None) == expected[:3]


def test_format_and_empty_notebooks(book: Path) -> None:
    _write(book, "01-time-grid.ipynb", _good("01"), fmt=3)
    _write(book, "02-series.ipynb", [])
    assert check(book, "demo") == [
        "01-time-grid.ipynb: nbformat 4 is required",
        "02-series.ipynb: the notebook is empty",
    ]


def test_cli_finds_the_package_under_src(book: Path) -> None:
    root = book.parent
    (root / "src" / "demo").mkdir(parents=True)
    (root / "src" / "demo" / "__init__.py").write_text("")
    cells = [_md(OPENING.format(n="02")), _code("import demo._x", 1), _md("**Next:** end.")]
    _write(book, "02-series.ipynb", cells)
    assert main(["--root", str(root), "check-notebooks"]) == 1
    (root / "src" / "other").mkdir()
    (root / "src" / "other" / "__init__.py").write_text("")
    assert main(["--root", str(root), "check-notebooks"]) == 0
