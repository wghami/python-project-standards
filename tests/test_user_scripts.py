"""User-facing scripts share one shape and each has a smoke test (DOC-13)."""

from pathlib import Path

from project_standards.cli import main
from project_standards.user_scripts import check

GOOD = '''"""Simulate one year."""

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
NESTED = '''"""Main hidden in a class."""


class Runner:
    def main(self, argv: object = None) -> int:
        return 0


if __name__ == "__main__":
    raise SystemExit(Runner().main())
'''
SIGNATURE = "needs `def main(argv: Sequence[str] | None = None) -> int`"
GUARD = 'needs `if __name__ == "__main__": raise SystemExit(main())`'


def _project(tmp_path: Path, scripts: dict[str, str], *, index: bool = True) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "__init__.py").write_text('"""Scripts."""\n')
    (tmp_path / "tests" / "scripts").mkdir(parents=True)
    for name, text in scripts.items():
        (tmp_path / "scripts" / f"{name}.py").write_text(text)
        (tmp_path / "tests" / "scripts" / f"test_{name}.py").write_text("")
    if index:
        listing = "".join(f"- `scripts/{n}.py`\n" for n in scripts)
        (tmp_path / "scripts" / "README.md").write_text(listing)
    return tmp_path


def test_good_scripts_pass(tmp_path: Path) -> None:
    assert check(_project(tmp_path, {"simulate_year": GOOD})) == []
    assert main(["--root", str(tmp_path), "check-scripts"]) == 0


def test_no_scripts_means_nothing_to_check(tmp_path: Path) -> None:
    assert check(tmp_path) == []
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "__init__.py").write_text("")
    assert check(tmp_path) == []


def test_every_rule_is_reported(tmp_path: Path) -> None:
    root = _project(tmp_path, {"bad": "def main(args):\n    return 0\n"}, index=False)
    (root / "tests" / "scripts" / "test_bad.py").unlink()
    assert check(root) == [
        f"{root / 'scripts' / 'README.md'}: missing; it introduces every script",
        "scripts/bad.py: needs a module docstring (what it does, for whom)",
        f"scripts/bad.py: {SIGNATURE}",
        f"scripts/bad.py: {GUARD}",
        "scripts/bad.py: needs a smoke test tests/scripts/test_bad.py",
    ]


def test_main_signature_details(tmp_path: Path) -> None:
    variants = {
        "no_default": GOOD.replace(" = None", ""),
        "wrong_default": GOOD.replace(" = None", " = ()"),
        "no_return": GOOD.replace(" -> int", ""),
        "nested": NESTED,
        "other_guard": GOOD.replace('if __name__ == "__main__":', "if True:"),
        "name_right": GOOD.replace('if __name__ == "__main__":', 'if "x" == __name__:'),
    }
    root = _project(tmp_path, variants)
    errors = check(root)
    for name in ("no_default", "wrong_default", "no_return", "nested"):
        assert f"scripts/{name}.py: {SIGNATURE}" in errors
    assert f"scripts/other_guard.py: {GUARD}" in errors
    assert f"scripts/name_right.py: {GUARD}" in errors
    assert "scripts/no_default.py: needs a module docstring (what it does, for whom)" not in errors
    (root / "scripts" / "README.md").write_text("")
    assert f"{root / 'scripts' / 'README.md'}: does not mention `scripts/nested.py`" in check(root)
