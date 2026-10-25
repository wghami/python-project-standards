"""README badges and the gates table are generated from the configuration (DOC-10)."""

import os
from pathlib import Path

import pytest

from project_standards.config import Readme
from project_standards.readme import Project, badges, check, gates_table, render

SNAPSHOTS = Path(__file__).parent / "snapshots"
HOOKS = """
default_stages: [pre-commit]
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: local
    hooks:
      - {id: ruff-check, name: ruff check, entry: x, language: system}
      - {id: commit-msg, entry: x, language: system, stages: [commit-msg]}
      - {id: tests, name: tests, entry: x, language: system, stages: [pre-push]}
      - {id: nameless, entry: x, language: system, stages: [pre-push, manual]}
"""
CI = """
on:
  pull_request:
  push: {branches: [main]}
jobs:
  pre-commit-stage: {runs-on: x}
  secrets: {name: secret scan, runs-on: x}
  audit: {runs-on: x}
  release: {runs-on: x}
"""
NIGHTLY = """
on:
  schedule: [{cron: "17 2 * * *"}]
  pull_request: {types: [labeled]}
jobs:
  mutation: {name: mutation score, if: "contains(github.event.pull_request.labels.*.name, 'm')"}
  report: {runs-on: x}
"""
WEEKLY = """
on:
  schedule: [{cron: "23 4 * * 1"}]
jobs:
  links: {name: external links}
"""
MANUAL = "on: workflow_dispatch\njobs:\n  rebuild: {name: rebuild}\n"
LISTED = "on: [push]\njobs:\n  lint: {name: lint everything}\n"
README = (
    "# Demo\n<!-- standards:badges:start -->\nold\n<!-- standards:badges:end -->\n\ntext\n\n"
    "<!-- standards:gates:start -->\n<!-- standards:gates:end -->\nend\n"
)


def _project(root: Path, *, full: bool = True) -> Project:
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (root / ".pre-commit-config.yaml").write_text(HOOKS)
    (workflows / "ci.yml").write_text(CI)
    if full:
        for name, text in (
            ("nightly.yml", NIGHTLY),
            ("weekly.yml", WEEKLY),
            ("manual.yml", MANUAL),
            ("listed.yml", LISTED),
            ("codeql.yml", "on: push\njobs: {}\n"),
            ("scorecard.yml", "on: push\njobs: {}\n"),
        ):
            (workflows / name).write_text(text)
        (root / "mkdocs.yml").write_text("site_name: x\n")
        (root / ".copier-answers.yml").write_text("_commit: v0.1.0\n")
    (root / "README.md").write_text(README)
    return Project(root=root, readme=Readme(repository="Owner/demo"))


def _snapshot(name: str, text: str) -> None:
    path = SNAPSHOTS / name
    if os.environ.get("STANDARDS_UPDATE_SNAPSHOTS"):
        path.write_text(text)
    assert text == path.read_text()


def test_full_readme_matches_the_snapshot(tmp_path: Path) -> None:
    project = _project(tmp_path)
    rendered, missing = render(project, README)
    assert missing == []
    _snapshot("readme_full.md", rendered)


def test_minimal_project_shows_only_what_exists(tmp_path: Path) -> None:
    project = _project(tmp_path, full=False)
    _snapshot("readme_minimal.md", badges(project) + "\n\n" + gates_table(project) + "\n")


def test_missing_markers_are_reported(tmp_path: Path) -> None:
    project = _project(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Demo\n<!-- standards:gates:start -->\n<!-- standards:gates:end -->\n"
    )
    assert check(project, write=False) == [
        "README.md has no <!-- standards:badges:start --> … <!-- standards:badges:end --> block"
    ]


def test_stale_readme_fails_until_written(tmp_path: Path) -> None:
    project = _project(tmp_path)
    assert check(project, write=False) == [
        "README.md badges or gates table are out of date: run `standards readme --write`"
    ]
    assert (tmp_path / "README.md").read_text() == README
    assert check(project, write=True) == []
    assert check(project, write=False) == []
    assert (tmp_path / "README.md").read_text() == render(project, README)[0]


def test_only_the_first_block_is_replaced(tmp_path: Path) -> None:
    project = _project(tmp_path)
    block = "<!-- standards:badges:start -->\n<!-- standards:badges:end -->"
    rendered, _ = render(
        project, f"{block}\n{block}\n<!-- standards:gates:start --><!-- standards:gates:end -->"
    )
    assert rendered.count("[![CI]") == 1
    assert rendered.endswith(
        f"{block}\n<!-- standards:gates:start -->\n"
        + gates_table(project)
        + "\n<!-- standards:gates:end -->"
    )


def test_empty_hook_config_and_skipped_jobs(tmp_path: Path) -> None:
    project = _project(tmp_path, full=False)
    (tmp_path / ".pre-commit-config.yaml").write_text("")
    project = Project(
        root=tmp_path,
        readme=Readme(
            repository="o/d", skip_jobs=("secrets", "audit", "pre-commit-stage", "release")
        ),
    )
    assert gates_table(project).splitlines()[0].startswith("**0 gates.** 0 run")


def test_malformed_workflow_is_refused(tmp_path: Path) -> None:
    project = _project(tmp_path, full=False)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("on: 3\njobs: {}\n")
    with pytest.raises(TypeError, match=r"^on must be a mapping$"):
        gates_table(project)
