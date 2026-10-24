"""Mutation-score gate (TST-12) over ``mutmut export-cicd-stats`` output."""

import json
from pathlib import Path
from typing import cast

_KILLED = ("killed", "timeout", "segfault")
_ALIVE = ("survived", "no_tests", "suspicious")


def score(stats: dict[str, int]) -> float | None:
    """Killed share of the evaluated mutants, in percent; ``None`` when there are none."""
    killed = sum(stats.get(k, 0) for k in _KILLED)
    evaluated = killed + sum(stats.get(k, 0) for k in _ALIVE)
    return None if evaluated == 0 else 100.0 * killed / evaluated


def check(stats_path: Path, minimum: float) -> list[str]:
    """Fail when the mutation score is below ``minimum`` percent."""
    stats = cast("dict[str, int]", json.loads(stats_path.read_text()))
    value = score(stats)
    if value is None or value >= minimum:
        return []
    return [
        (
            f"mutation score {value:.1f} % is below {minimum:g} % "
            f"({stats.get('survived', 0)} survived, {stats.get('no_tests', 0)} untested)"
        )
    ]
