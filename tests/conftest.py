"""Shared fixtures: real git repositories in temporary directories."""

import itertools
from pathlib import Path

import pytest

from project_standards._git import Git

_counter = itertools.count()


class Repo:
    """A throw-away git repository with helpers for writing, committing and tagging."""

    def __init__(self, path: Path) -> None:
        """Wrap the repository at ``path``."""
        self.path = path
        self.git = Git(path)

    def write(self, name: str, text: str = "x\n") -> Path:
        target = self.path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return target

    def commit(self, message: str, files: dict[str, str] | None = None) -> str:
        for name, text in (files or {f"file{next(_counter)}.txt": "x\n"}).items():
            self.write(name, text)
        self.git.run("add", "-A")
        self.git.run("commit", "-q", "-m", message)
        return self.git.run("rev-parse", "HEAD")

    def add_remote(self) -> Path:
        remote = self.path.parent / f"{self.path.name}-remote.git"
        Git(self.path.parent).run("init", "-q", "--bare", str(remote))
        self.git.run("remote", "add", "origin", str(remote))
        return remote


def make_repo(path: Path) -> Repo:
    path.mkdir(parents=True, exist_ok=True)
    git = Git(path)
    git.run("init", "-q", "-b", "main")
    for key, value in (
        ("user.name", "Test"),
        ("user.email", "test@example.invalid"),
        ("commit.gpgsign", "false"),
        ("tag.gpgsign", "false"),
    ):
        git.run("config", key, value)
    return Repo(path)


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return make_repo(tmp_path / "repo")
