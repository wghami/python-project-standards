"""Path globbing with ``**`` that behaves the same on every Python version."""

import re
from functools import cache


@cache
def _compile(pattern: str) -> re.Pattern[str]:
    out: list[str] = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches(path: str, pattern: str) -> bool:
    """True when the repository-relative ``path`` matches ``pattern``.

    ``*`` and ``?`` stay within one path segment; ``**`` spans segments.
    """
    return _compile(pattern).match(path) is not None


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    """True when ``path`` matches at least one of ``patterns``."""
    return any(matches(path, p) for p in patterns)
