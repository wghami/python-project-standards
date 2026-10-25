"""Mutation-score gate (TST-12) over ``mutmut export-cicd-stats`` output."""

import json
from pathlib import Path

from project_standards._typed import mapping

_KILLED = ("killed", "timeout", "segfault")
_ALIVE = ("survived", "no_tests", "suspicious")


def score(stats: dict[str, int]) -> float | None:
    """Killed share of the evaluated mutants, in percent; ``None`` when there are none."""
    killed = sum(stats.get(k, 0) for k in _KILLED)
    evaluated = killed + sum(stats.get(k, 0) for k in _ALIVE)
    return None if evaluated == 0 else 100.0 * killed / evaluated


def not_evaluated(stats: dict[str, int]) -> str:
    """The message for mutants that exist but were never run (the baseline test run failed)."""
    return (
        f"mutmut evaluated none of the {stats.get('total', 0)} mutants: the baseline test "
        "run failed (see the `mutmut run` output)"
    )


def check(stats_path: Path, minimum: float) -> list[str]:
    """Fail when the mutation score is below ``minimum`` percent."""
    raw = mapping(json.loads(stats_path.read_text()), str(stats_path))
    stats = {key: value for key, value in raw.items() if isinstance(value, int)}
    value = score(stats)
    if value is None:
        return [] if stats.get("total", 0) == 0 else [not_evaluated(stats)]
    if value >= minimum:
        return []
    return [
        (
            f"mutation score {value:.1f} % is below {minimum:g} % "
            f"({stats.get('survived', 0)} survived, {stats.get('no_tests', 0)} untested)"
        )
    ]
