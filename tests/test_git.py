"""The git wrapper raises on failure, or returns None when asked to try."""

import pytest

from conftest import Repo
from project_standards._git import GitError


def test_run_returns_stripped_output(repo: Repo) -> None:
    assert repo.git.run("rev-parse", "--is-inside-work-tree") == "true"


def test_run_raises_with_the_command_and_stderr(repo: Repo) -> None:
    with pytest.raises(GitError, match="git rev-parse HEAD"):
        repo.git.run("rev-parse", "HEAD")


def test_try_run_returns_none_on_failure(repo: Repo) -> None:
    assert repo.git.try_run("rev-parse", "HEAD") is None


def test_lines_drops_empty_lines(repo: Repo) -> None:
    repo.commit("feat(core): one")
    assert repo.git.lines("log", "--format=%s%n") == ["feat(core): one"]
