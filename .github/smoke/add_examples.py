"""Add one example notebook (executed) and one example script with its test to a rendered project.

Used by the smoke job in ci.yml to prove DOC-12 and DOC-13 work end to end; not part of the CLI.
"""

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(sys.argv[1])
package = sys.argv[2]

notebook = nbformat.v4.new_notebook()
notebook.cells = [
    nbformat.v4.new_markdown_cell(
        "# 01 — The version\n\n**Concept:** the version comes from git tags.\n\n"
        "**You will learn:** where to read it."
    ),
    nbformat.v4.new_code_cell(f"import {package}\n\n{package}.__version__"),
    nbformat.v4.new_markdown_cell("**Next:** there is no next notebook in this example."),
]
notebook.metadata["kernelspec"] = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}
NotebookClient(notebook, timeout=120, kernel_name="python3").execute()
nbformat.write(notebook, root / "notebooks" / "01-the-version.ipynb")
readme = root / "notebooks" / "README.md"
readme.write_text(
    readme.read_text().replace("_None yet._", "- [01 — The version](01-the-version.ipynb)")
)

(
    root / "src" / package / "example.py"
).write_text('''"""A submodule, to prove the API reference documents submodules (DOC-3)."""


def smoke_reference_marker() -> int:
    """Return 42; the smoke job looks for this function in the built reference."""
    return 42
''')
(root / "tests" / "unit" / "test_example.py").write_text(f'''"""The example submodule is covered."""

from {package}.example import smoke_reference_marker


def test_marker() -> None:
    assert smoke_reference_marker() == 42
''')

(
    root / "scripts" / "show_version.py"
).write_text(f'''"""Print the installed version of the package (an example script)."""

import argparse
import sys
from collections.abc import Sequence

import {package}


def main(argv: Sequence[str] | None = None) -> int:
    """Print the version and return the exit status."""
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    sys.stdout.write(f"{{{package}.__version__}}\\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''')
scripts_readme = root / "scripts" / "README.md"
scripts_readme.write_text(
    scripts_readme.read_text().replace(
        "_None yet._", "- `scripts/show_version.py`: print the installed version."
    )
)
(root / "tests" / "scripts").mkdir(parents=True, exist_ok=True)
(
    root / "tests" / "scripts" / "test_show_version.py"
).write_text('''"""The example script prints the version, through main() and as a program."""

import runpy
from pathlib import Path

import pytest

from scripts.show_version import main

SCRIPT = Path(__file__).parents[2] / "scripts" / "show_version.py"


def test_main_prints_the_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert capsys.readouterr().out.strip()


def test_runs_as_a_program(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["show_version"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    assert exit_info.value.code == 0
''')
