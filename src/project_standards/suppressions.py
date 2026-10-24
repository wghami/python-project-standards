"""Forbid silent exclusions (COV-2, TYP-3, LNT-4)."""

import re
from collections.abc import Iterable
from pathlib import Path

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"#\s*pragma:\s*no\s*(cover|branch)", re.IGNORECASE),
        "coverage pragmas are forbidden; delete or redesign uncovered code (COV-2)",
    ),
    (
        re.compile(r"#\s*(ruff|flake8)\s*:\s*noqa", re.IGNORECASE),
        "file-level noqa is forbidden (LNT-4)",
    ),
    (
        re.compile(r"#\s*noqa(?!\s*:\s*[A-Z]+\d+)", re.IGNORECASE),
        "noqa must name its rule codes (LNT-4)",
    ),
    (
        re.compile(r"#\s*noqa\s*:\s*[A-Z]+\d+(?:\s*,\s*[A-Z]+\d+)*\s*$"),
        "noqa needs a reason: '# noqa: E501  # why' (LNT-4)",
    ),
    (re.compile(r"#\s*type:\s*ignore(?!\[)"), "type: ignore must name its error code (TYP-3)"),
    (
        re.compile(r"#\s*(type|pyright):\s*ignore\[[^\]]*\]\s*$"),
        "type ignores need a reason: '# pyright: ignore[rule]  # why' (TYP-3)",
    ),
    (re.compile(r"#\s*pyright:\s*ignore(?!\[)"), "pyright: ignore must name its rule (TYP-3)"),
    (
        re.compile(r"#\s*nosec\b", re.IGNORECASE),
        "nosec is forbidden; suppress through ruff: '# noqa: S603  # why' (SEC-4)",
    ),
    (
        re.compile(r"#\s*pyright:\s*basic\b"),
        "lowering the pyright mode in a file is forbidden (TYP-1)",
    ),
)


def check_text(text: str, path: str) -> list[str]:
    """Return one message per forbidden suppression found in ``text``."""
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        errors.extend(
            f"{path}:{number}: {message}" for pattern, message in _RULES if pattern.search(line)
        )
    return errors


def check_files(paths: Iterable[Path]) -> list[str]:
    """Check every Python file in ``paths``."""
    errors: list[str] = []
    for path in paths:
        if path.suffix in {".py", ".pyi"}:
            errors.extend(check_text(path.read_text(encoding="utf-8"), str(path)))
    return errors
