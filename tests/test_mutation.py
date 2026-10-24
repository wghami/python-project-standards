"""Mutation-score gate (TST-12)."""

import json
from pathlib import Path

from project_standards.mutation import check, score


def test_score_counts_timeouts_as_killed() -> None:
    assert score({"killed": 8, "timeout": 1, "survived": 1}) == 90.0


def test_no_mutants_has_no_score() -> None:
    assert score({"total": 0}) is None


def _stats(tmp_path: Path, **stats: int) -> Path:
    path = tmp_path / "stats.json"
    path.write_text(json.dumps(stats))
    return path


def test_gate(tmp_path: Path) -> None:
    assert check(_stats(tmp_path, killed=9, survived=1), 90) == []
    assert check(_stats(tmp_path), 90) == []
    errors = check(_stats(tmp_path, killed=8, survived=1, no_tests=1), 90)
    assert errors == ["mutation score 80.0 % is below 90 % (1 survived, 1 untested)"]
