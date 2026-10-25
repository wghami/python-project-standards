"""Notebooks as documentation (DOC-12): one concept per notebook, committed fully executed.

Checked without running anything: names and numbering, the opening and closing cells, that every
code cell ran exactly once from top to bottom with no error, that only the public API is used,
and that the index links every notebook. Running them is the ``notebooks`` hook's job (nbmake).
"""

import json
import re
from pathlib import Path

from project_standards._typed import mapping, sequence

_NAME = re.compile(r"(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.ipynb")
_NOTEBOOK_FORMAT = 4


def _source(cell: dict[str, object]) -> str:
    raw = cell.get("source", "")
    return raw if isinstance(raw, str) else "".join(str(line) for line in sequence(raw, "source"))


def _private_imports(code: str, package: str) -> list[str]:
    pattern = re.compile(
        rf"^\s*(?:from|import)\s+({re.escape(package)}(?:\.\w+)*)(.*)$", re.MULTILINE
    )
    found: list[str] = []
    for module, rest in pattern.findall(code):
        names = [part.strip().split(" as ")[0] for part in rest.removeprefix(" import").split(",")]
        if any(part.startswith("_") for part in module.split(".")) or (
            rest.startswith(" import") and any(n.startswith("_") for n in names)
        ):
            found.append(f"{module}{rest}".strip())
    return found


def _opening_errors(cells: list[dict[str, object]], number: str) -> list[str]:
    errors: list[str] = []
    first = cells[0]
    text = _source(first)
    if first.get("cell_type") != "markdown" or not text.startswith(f"# {number} — "):
        errors.append(f"the first cell is a markdown title '# {number} — <concept>'")
    errors.extend(
        f"the first cell states {label}"
        for label in ("**Concept:**", "**You will learn:**")
        if label not in text
    )
    last = cells[-1]
    if last.get("cell_type") != "markdown" or "**Next:**" not in _source(last):
        errors.append("the last cell is markdown and says what comes **Next:**")
    return errors


def _execution_errors(cells: list[dict[str, object]], package: str | None) -> list[str]:
    errors: list[str] = []
    code = [c for c in cells if c.get("cell_type") == "code"]
    if any(not _source(c).strip() for c in code):
        errors.append("remove empty code cells")
    counts = [c.get("execution_count") for c in code]
    if counts != list(range(1, len(code) + 1)):
        errors.append(
            "code cells must have run once, top to bottom, in a fresh kernel: re-run "
            "it with `jupyter nbconvert --to notebook --execute --inplace`"
        )
    for cell in code:
        outputs = [mapping(o, "output") for o in sequence(cell.get("outputs", []), "outputs")]
        if any(o.get("output_type") == "error" for o in outputs):
            errors.append("a code cell has an error output")
        if package is not None:
            errors.extend(
                f"uses private API: {i}" for i in _private_imports(_source(cell), package)
            )
    return errors


def _notebook_errors(path: Path, number: str, package: str | None) -> list[str]:
    notebook = mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
    if notebook.get("nbformat") != _NOTEBOOK_FORMAT:
        return [f"{path.name}: nbformat {_NOTEBOOK_FORMAT} is required"]
    cells = [mapping(c, "cell") for c in sequence(notebook.get("cells", []), "cells")]
    if not cells:
        return [f"{path.name}: the notebook is empty"]
    errors = _opening_errors(cells, number) + _execution_errors(cells, package)
    return [f"{path.name}: {error}" for error in errors]


def check(directory: Path, package: str | None) -> list[str]:
    """Return every problem with the notebooks in ``directory`` (none when it does not exist)."""
    files = sorted(directory.glob("*.ipynb"))
    if not files:
        return []
    index = directory / "README.md"
    listed = index.read_text(encoding="utf-8") if index.exists() else ""
    errors = [] if index.exists() else [f"{index}: missing; it introduces and links every notebook"]
    numbers: list[int] = []
    for path in files:
        name = _NAME.fullmatch(path.name)
        if name is None:
            errors.append(
                f"{path.name}: the name must be NN-concept.ipynb (e.g. 01-time-grid.ipynb)"
            )
            continue
        numbers.append(int(name[1]))
        errors += _notebook_errors(path, name[1], package)
        if index.exists() and f"]({path.name})" not in listed:
            errors.append(f"{index}: does not link {path.name}")
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        errors.append(f"{directory}: notebooks are numbered 01, 02, … without gaps or duplicates")
    return errors
