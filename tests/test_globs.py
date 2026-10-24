"""Globbing: ``*`` stays in one segment, ``**`` crosses segments."""

import pytest

from project_standards.globs import matches, matches_any


@pytest.mark.parametrize(
    ("path", "pattern", "expected"),
    [
        ("src/pkg/a.py", "src/**", True),
        ("src/pkg/a.py", "src/*.py", False),
        ("src/a.py", "src/*.py", True),
        ("a.py", "**/a.py", True),
        ("x/y/a.py", "**/a.py", True),
        ("src/ab.py", "src/a?.py", True),
        ("src/a/b.py", "src/a?b.py", False),
        ("srcXa.py", "src.a.py", False),
        ("docs/standards/01.md", "docs/standards/**", True),
    ],
)
def test_matches(path: str, pattern: str, *, expected: bool) -> None:
    assert matches(path, pattern) is expected


def test_matches_any() -> None:
    assert matches_any("a.py", ("*.md", "*.py"))
    assert not matches_any("a.py", ())
