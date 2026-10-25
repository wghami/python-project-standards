"""Measured-quality badges (CI-10): coverage, docstrings and mutation score as shields.io JSON.

The numbers come from the gates' own reports, so a badge can only show what a gate measured.
"""

import json
import re
from pathlib import Path

from project_standards import mutation
from project_standards._typed import mapping

_COVERAGE_ATTR = re.compile(r'\b(lines|branches)-(valid|covered)="(\d+)"')
_INTERROGATE = re.compile(r"actual: (\d+(?:\.\d+)?)%")
_PERFECT = 99.995  # shown as 100% only when it rounds to 100.0
_COLOURS = ((99.95, "brightgreen"), (90.0, "green"), (80.0, "yellow"), (70.0, "orange"))


def colour(percent: float) -> str:
    """Badge colour for a percentage: only a perfect score is bright green."""
    return next((name for floor, name in _COLOURS if percent >= floor), "red")


def coverage_percent(report: str) -> float:
    """Combined line + branch coverage from a Cobertura ``coverage.xml`` (as coverage.py does).

    Raises:
        ValueError: the report has no line/branch totals.
    """
    totals = {f"{kind}-{what}": int(value) for kind, what, value in _COVERAGE_ATTR.findall(report)}
    if len(totals) != len(("lines-valid", "lines-covered", "branches-valid", "branches-covered")):
        msg = "coverage.xml has no lines/branches totals"
        raise ValueError(msg)
    valid = totals["lines-valid"] + totals["branches-valid"]
    covered = totals["lines-covered"] + totals["branches-covered"]
    return 100.0 if valid == 0 else 100.0 * covered / valid


def docstring_percent(report: str) -> float:
    """Docstring coverage from interrogate's summary line ``actual: 97.5%``.

    Raises:
        ValueError: the summary line is missing.
    """
    match = _INTERROGATE.search(report)
    if match is None:
        msg = "interrogate output has no 'actual: N%' summary"
        raise ValueError(msg)
    return float(match[1])


def _shown(percent: float) -> str:
    return "100%" if percent >= _PERFECT else f"{percent:.1f}%"


def endpoint(label: str, percent: float | None) -> dict[str, object]:
    """A shields.io endpoint document; ``None`` means nothing was measured yet."""
    if percent is None:
        return {
            "schemaVersion": 1,
            "label": label,
            "message": "no mutants yet",
            "color": "lightgrey",
        }
    return {
        "schemaVersion": 1,
        "label": label,
        "message": _shown(percent),
        "color": colour(percent),
    }


def measure(metric: str, source: Path) -> dict[str, object]:
    """Read ``source`` for ``metric`` (coverage, docstrings or mutation) and build its badge.

    Raises:
        ValueError: unknown metric, or a report without the expected totals.
    """
    text = source.read_text(encoding="utf-8")
    if metric == "coverage":
        return endpoint("coverage", coverage_percent(text))
    if metric == "docstrings":
        return endpoint("docstrings", docstring_percent(text))
    if metric == "mutation":
        stats = mapping(json.loads(text), str(source))
        counts = {k: v for k, v in stats.items() if isinstance(v, int)}
        if mutation.score(counts) is None and counts.get("total", 0) > 0:
            return {
                "schemaVersion": 1,
                "label": "mutation",
                "message": "not measured",
                "color": "red",
            }
        return endpoint(
            "mutation", mutation.score({k: v for k, v in stats.items() if isinstance(v, int)})
        )
    msg = f"unknown metric '{metric}' (coverage, docstrings, mutation)"
    raise ValueError(msg)
