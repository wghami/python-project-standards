"""Measured badges report exactly what the gates measured (CI-10)."""

import json
from pathlib import Path

import pytest

from project_standards.badges import (
    colour,
    coverage_percent,
    docstring_percent,
    endpoint,
    measure,
)

COVERAGE = (
    '<?xml version="1.0" ?>\n<coverage version="7" lines-valid="90" lines-covered="81" '
    'line-rate="0.9" branches-covered="9" branches-valid="10" branch-rate="0.9">'
)


@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        (100.0, "brightgreen"),
        (99.95, "brightgreen"),
        (99.9, "green"),
        (90.0, "green"),
        (89.9, "yellow"),
        (80.0, "yellow"),
        (79.9, "orange"),
        (70.0, "orange"),
        (69.9, "red"),
    ],
)
def test_colour_thresholds(percent: float, expected: str) -> None:
    assert colour(percent) == expected


def test_coverage_combines_lines_and_branches_like_coverage_py() -> None:
    assert coverage_percent(COVERAGE) == 90.0


def test_empty_coverage_is_complete() -> None:
    report = 'lines-valid="0" lines-covered="0" branches-valid="0" branches-covered="0"'
    assert coverage_percent(report) == 100.0


def test_incomplete_coverage_report_is_refused() -> None:
    with pytest.raises(ValueError, match=r"^coverage.xml has no lines/branches totals$"):
        coverage_percent('lines-valid="1" lines-covered="1" branches-valid="1"')


def test_docstring_percent_reads_the_summary() -> None:
    assert docstring_percent("RESULT: PASSED (minimum: 0.0%, actual: 97.5%)") == 97.5
    assert docstring_percent("actual: 100%") == 100.0
    with pytest.raises(ValueError, match=r"^interrogate output has no 'actual: N%' summary$"):
        docstring_percent("nothing")


@pytest.mark.parametrize(
    ("percent", "message", "color"),
    [
        (100.0, "100%", "brightgreen"),
        (99.996, "100%", "brightgreen"),
        (99.994, "100.0%", "brightgreen"),
        (91.25, "91.2%", "green"),
    ],
)
def test_endpoint_documents(percent: float, message: str, color: str) -> None:
    assert endpoint("coverage", percent) == {
        "schemaVersion": 1,
        "label": "coverage",
        "message": message,
        "color": color,
    }


def test_nothing_measured_is_grey() -> None:
    assert endpoint("mutation", None) == {
        "schemaVersion": 1,
        "label": "mutation",
        "message": "no mutants yet",
        "color": "lightgrey",
    }


def test_measure_each_metric(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(COVERAGE)
    (tmp_path / "doc.txt").write_text("actual: 100.0%")
    (tmp_path / "stats.json").write_text(json.dumps({"killed": 9, "survived": 1, "x": "y"}))
    assert measure("coverage", tmp_path / "coverage.xml")["message"] == "90.0%"
    assert measure("docstrings", tmp_path / "doc.txt")["message"] == "100%"
    assert measure("mutation", tmp_path / "stats.json") == endpoint("mutation", 90.0)
    with pytest.raises(
        ValueError, match=r"^unknown metric 'speed' \(coverage, docstrings, mutation\)$"
    ):
        measure("speed", tmp_path / "doc.txt")
