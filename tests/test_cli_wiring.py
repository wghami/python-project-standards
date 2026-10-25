"""Each subcommand is wired to the right check with the right arguments (exact output)."""

import json
import os
from pathlib import Path

import pytest

from conftest import Repo
from project_standards.cli import commands, main

SNAPSHOT = Path(__file__).parent / "snapshots" / "cli_help.txt"


def _help(argv: list[str], capsys: pytest.CaptureFixture[str]) -> str:
    with pytest.raises(SystemExit) as exit_info:
        main([*argv, "--help"])
    assert exit_info.value.code == 0
    return capsys.readouterr().out


def test_help_matches_the_snapshot(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "100")
    text = "".join(
        f"$ standards {' '.join(a)} --help\n{_help(a, capsys)}\n"
        for a in [[], *([c] for c in commands())]
    )
    text = text.rstrip("\n") + "\n"  # one trailing newline, as end-of-file-fixer keeps it
    if os.environ.get("STANDARDS_UPDATE_SNAPSHOTS"):
        SNAPSHOT.write_text(text)
    assert text == SNAPSHOT.read_text()


@pytest.mark.parametrize(
    "argv", [[], ["check-commits"], ["check-mutation-score", "s.json"], ["check-pr-title"]]
)
def test_missing_required_arguments_are_usage_errors(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(argv)
    assert exit_info.value.code == 2


@pytest.fixture
def project(repo: Repo) -> Repo:
    repo.write("standards.toml", '[commits]\nscopes = ["core"]\n')
    repo.write("pyproject.toml", '[project]\nname = "x"\ndynamic = ["version"]\n')
    repo.commit("chore: start")
    return repo


def run(project: Repo, *argv: str) -> int:
    return main(["--root", str(project.path), *argv])


def test_root_defaults_to_the_current_directory(
    project: Repo, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(project.path)
    project.git.run("checkout", "-q", "-b", "wip")
    assert main(["check-branch-name"]) == 1
    assert "branch 'wip'" in capsys.readouterr().err


@pytest.fixture
def elsewhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run from a directory that is not a repository, so only --root can find the project."""
    path = tmp_path / "elsewhere"
    path.mkdir()
    monkeypatch.chdir(path)
    return path


def test_commit_msg_allows_autosquash_locally(project: Repo) -> None:
    message = project.write("msg", "fixup! feat(core): x\n")
    assert run(project, "check-commit-msg", str(message)) == 0


def test_commits_report_short_shas(project: Repo, capsys: pytest.CaptureFixture[str]) -> None:
    sha = project.commit("bad message")
    assert run(project, "check-commits", "--range", "HEAD~1..HEAD") == 1
    assert capsys.readouterr().err == (
        f"✗ {sha[:10]}: 'bad message' is not '<type>(<scope>): <summary>' (Conventional Commits)\n"
    )


def test_branch_from_git(
    project: Repo, elsewhere: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert elsewhere.exists()
    project.git.run("checkout", "-q", "-b", "wip")
    assert run(project, "check-branch-name") == 1
    assert "✗ branch 'wip' must be" in capsys.readouterr().err


def test_suppressions_scan_python_and_stub_files(
    project: Repo, elsewhere: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert elsewhere.exists()
    project.commit("chore: add", {"a.pyi": "x: int  " + "#" + " noqa\n", "b.py": "x = 1\n"})
    assert run(project, "check-suppressions") == 1
    assert capsys.readouterr().err == (
        f"✗ {project.path / 'a.pyi'}:1: noqa must name its rule codes (LNT-4)\n"
    )


def test_version_reports_every_problem(project: Repo, capsys: pytest.CaptureFixture[str]) -> None:
    project.add_remote()
    project.write("pyproject.toml", '[project]\nversion = "1"\n')
    sha = project.commit("feat(core): x")
    project.git.run("tag", "v0.1.0")
    assert run(project, "check-version", "--remote", "origin", "--released") == 1
    assert capsys.readouterr().err == (
        "✗ pyproject.toml sets [project].version; it must come from git tags (VER-1)\n"
        '✗ pyproject.toml must declare dynamic = ["version"] (VER-1)\n'
        "✗ tag v0.1.0 is not on 'origin': git push origin v0.1.0\n"
    )
    project.commit("fix(core): y")
    assert run(project, "check-version", "--released") == 1
    assert "not tagged" in capsys.readouterr().err
    assert sha


def test_doc_impact_defaults_to_origin_main(project: Repo) -> None:
    project.write("standards.toml", '[doc_impact]\nwatched = ["src/**"]\n')
    project.commit("chore: config")
    project.add_remote()
    project.git.run("push", "-q", "origin", "main")
    project.git.run("fetch", "-q", "origin")
    project.commit("docs: code", {"src/a.py": "x = 1\n"})
    assert run(project, "check-doc-impact") == 1


def test_standards_reads_the_given_hook_config(
    project: Repo, capsys: pytest.CaptureFixture[str]
) -> None:
    project.write("d/a.md", "".join(f"`standards {c}`\n" for c in commands()))
    project.write("h.yaml", "repos: [{hooks: [{id: lonely}]}]\n")
    assert run(project, "check-standards", "--docs", "d", "--config", "h.yaml") == 1
    assert capsys.readouterr().err == (
        f"✗ hook `lonely` ({project.path / 'h.yaml'}) is not documented in {project.path / 'd'}\n"
    )


def test_mutation_score_uses_the_minimum(
    project: Repo, elsewhere: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert elsewhere.exists()
    project.write("s.json", json.dumps({"killed": 9, "survived": 1}))
    assert run(project, "check-mutation-score", "s.json", "--min", "95") == 1
    assert capsys.readouterr().err == (
        "✗ mutation score 90.0 % is below 95 % (1 survived, 0 untested)\n"
    )


def test_drift_and_hooks_run_in_the_project(
    project: Repo, elsewhere: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert elsewhere.exists()
    project.write(".copier-answers.yml", f"_commit: v0.1.0\n_src_path: {project.path}\n")
    assert run(project, "check-template-drift") == 0
    assert run(project, "check-hooks-installed") == 1
    assert capsys.readouterr().err.count("is not installed") == 3


def test_readme_needs_a_repository(project: Repo, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(project, "readme") == 1
    assert capsys.readouterr().err == ('✗ standards.toml: set [readme] repository = "owner/name"\n')


def test_readme_check_then_write(project: Repo, elsewhere: Path) -> None:
    assert elsewhere.exists()
    project.write("standards.toml", '[readme]\nrepository = "o/d"\n')
    project.write(".pre-commit-config.yaml", "repos: []\n")
    project.write(".github/workflows/ci.yml", "on: push\njobs: {}\n")
    marked = "<!-- standards:badges:start --><!-- standards:badges:end -->\n"
    project.write("README.md", marked + marked.replace("badges", "gates"))
    assert run(project, "readme") == 1
    assert run(project, "readme", "--write") == 0
    assert run(project, "readme") == 0
    assert "[![CI](https://github.com/o/d/" in (project.path / "README.md").read_text()


def test_badge_writes_the_endpoint_document(project: Repo, elsewhere: Path) -> None:
    assert elsewhere.exists()
    project.write("doc.txt", "actual: 100.0%")
    assert run(project, "badge", "docstrings", "doc.txt", "--out", "out/b/docstrings.json") == 0
    assert json.loads((project.path / "out" / "b" / "docstrings.json").read_text()) == {
        "schemaVersion": 1,
        "label": "docstrings",
        "message": "100%",
        "color": "brightgreen",
    }
    assert (project.path / "out" / "b" / "docstrings.json").read_text().endswith("}\n")
