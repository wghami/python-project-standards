"""The ``standards`` command line wires every check and reports uniformly."""

import json
import runpy
from pathlib import Path

import pytest

from conftest import Repo, make_repo
from project_standards.cli import main

STANDARDS = """
[commits]
scopes = ["core"]
[doc_impact]
watched = ["src/**"]
[[doc_impact.rules]]
paths = ["src/**"]
docs = ["docs/**"]
"""


@pytest.fixture
def project(repo: Repo) -> Repo:
    repo.write("standards.toml", STANDARDS)
    repo.write("pyproject.toml", '[project]\nname = "x"\ndynamic = ["version"]\n')
    repo.commit("chore: start")
    return repo


def run(project: Repo, *argv: str) -> int:
    return main(["--root", str(project.path), *argv])


def test_success_prints_a_check_mark(project: Repo, capsys: pytest.CaptureFixture[str]) -> None:
    message = project.write("msg.txt", "feat(core): add x\n")
    assert run(project, "check-commit-msg", str(message)) == 0
    assert capsys.readouterr().out == "✓ check-commit-msg\n"


def test_failure_lists_errors(project: Repo, capsys: pytest.CaptureFixture[str]) -> None:
    message = project.write("msg.txt", "added stuff\n")
    assert run(project, "check-commit-msg", str(message)) == 1
    assert "✗ 'added stuff' is not" in capsys.readouterr().err


def test_unexpected_errors_are_reported_not_raised(
    project: Repo, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(project, "check-commit-msg", str(project.path / "absent")) == 1
    assert "FileNotFoundError" in capsys.readouterr().err


def test_commit_range_and_pr_title(project: Repo) -> None:
    project.commit("feat(core): add x")
    assert run(project, "check-commits", "--range", "HEAD~1..HEAD") == 0
    project.commit("bad message")
    assert run(project, "check-commits", "--range", "HEAD~2..HEAD") == 1
    assert run(project, "check-pr-title", "feat(core): add x") == 0
    assert run(project, "check-pr-title", "Add x") == 1


def test_branch_name_from_git_or_argument(project: Repo) -> None:
    assert run(project, "check-branch-name") == 0
    project.git.run("checkout", "-q", "--detach")
    assert run(project, "check-branch-name") == 0
    assert run(project, "check-branch-name", "--name", "wip") == 1


def test_suppressions_from_git_or_arguments(project: Repo) -> None:
    project.commit("chore: add code", {"src/a.py": "x = 1  " + "#" + " noqa\n"})
    assert run(project, "check-suppressions") == 1
    assert run(project, "check-suppressions", "standards.toml") == 0


def test_version_checks(project: Repo) -> None:
    project.add_remote()
    project.git.run("push", "-q", "origin", "main")
    assert run(project, "check-version") == 0
    assert run(project, "check-version", "--remote", "origin", "--released") == 0
    project.commit("feat(core): add x")
    assert run(project, "check-version", "--released") == 1


def test_doc_impact_base_from_env_or_skip(
    project: Repo, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(project, "check-doc-impact") == 0
    assert "not found" in capsys.readouterr().err
    base = project.git.run("rev-parse", "HEAD")
    project.commit("feat(core): add x", {"src/a.py": "x = 1\n"})
    monkeypatch.setenv("STANDARDS_BASE_REF", base)
    assert run(project, "check-doc-impact") == 1
    assert run(project, "check-doc-impact", "--base", "HEAD") == 0


def test_hook_parity_and_standards(project: Repo) -> None:
    project.write(".pre-commit-config.yaml", "repos: []\n")
    project.write(".github/workflows/ci.yml", "jobs: {}\n")
    assert run(project, "check-hook-parity") == 0
    project.write("docs/standards/a.md", "| X-1 | rule | `standards check-commits` |\n")
    assert run(project, "check-standards") == 1


def test_mutation_score(project: Repo) -> None:
    stats = project.write("stats.json", json.dumps({"killed": 1, "survived": 1}))
    assert run(project, "check-mutation-score", str(stats), "--min", "90") == 1


def test_template_drift(project: Repo, tmp_path: Path) -> None:
    template = make_repo(tmp_path / "template")
    template.commit("feat(core): x")
    template.git.run("tag", "v0.1.0")
    project.write(".copier-answers.yml", f"_commit: v0.1.0\n_src_path: {template.path}\n")
    assert run(project, "check-template-drift") == 0


def test_hooks_installed(project: Repo) -> None:
    assert run(project, "check-hooks-installed") == 1


def test_module_entry_point(project: Repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["standards", "--root", str(project.path), "check-branch-name"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("project_standards", run_name="__main__")
    assert exit_info.value.code == 0
