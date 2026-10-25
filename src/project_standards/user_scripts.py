"""User-facing scripts (DOC-13): advanced applications with one shape, each tested.

Every ``scripts/<name>.py`` has a module docstring, a ``main(argv=None) -> int`` entry point, the
``if __name__ == "__main__"`` guard, a smoke test ``tests/scripts/test_<name>.py``, and a mention
in ``scripts/README.md``.
"""

import ast
from pathlib import Path

_SIGNATURE = "main(argv: Sequence[str] | None = None) -> int"


def _has_main(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            args = node.args
            return (
                [a.arg for a in args.args] == ["argv"]
                and len(args.defaults) == 1
                and isinstance(args.defaults[0], ast.Constant)
                and args.defaults[0].value is None
                and node.returns is not None
            )
    return False


def _has_guard(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        for node in tree.body
    )


def check(root: Path) -> list[str]:
    """Return every problem with the scripts under ``root / "scripts"``."""
    directory = root / "scripts"
    files = sorted(p for p in directory.glob("*.py") if p.name != "__init__.py")
    if not files:
        return []
    index = directory / "README.md"
    listed = index.read_text(encoding="utf-8") if index.exists() else ""
    errors = [] if index.exists() else [f"{index}: missing; it introduces every script"]
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        name = f"scripts/{path.name}"
        if ast.get_docstring(tree) is None:
            errors.append(f"{name}: needs a module docstring (what it does, for whom)")
        if not _has_main(tree):
            errors.append(f"{name}: needs `def {_SIGNATURE}`")
        if not _has_guard(tree):
            errors.append(f'{name}: needs `if __name__ == "__main__": raise SystemExit(main())`')
        if not (root / "tests" / "scripts" / f"test_{path.stem}.py").exists():
            errors.append(f"{name}: needs a smoke test tests/scripts/test_{path.stem}.py")
        if index.exists() and f"`{name}`" not in listed:
            errors.append(f"{index}: does not mention `{name}`")
    return errors
