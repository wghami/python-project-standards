"""A thin, testable wrapper around the ``git`` binary."""

import shutil
import subprocess
from pathlib import Path

_GIT = shutil.which("git") or "git"


class GitError(RuntimeError):
    """A git command failed."""


class Git:
    """Runs git commands in one working tree."""

    def __init__(self, cwd: Path) -> None:
        """Bind to the repository containing ``cwd``."""
        self.cwd = cwd

    def run(self, *args: str) -> str:
        """Run ``git <args>`` and return stripped stdout.

        Raises:
            GitError: the command exited with a non-zero status.
        """
        completed = subprocess.run(  # noqa: S603  # fixed binary, arguments never reach a shell
            [_GIT, *args], cwd=self.cwd, capture_output=True, text=True, check=False
        )
        if completed.returncode != 0:
            msg = f"git {' '.join(args)}: {completed.stderr.strip()}"
            raise GitError(msg)
        return completed.stdout.strip()

    def try_run(self, *args: str) -> str | None:
        """Like :meth:`run`, but return ``None`` instead of raising."""
        try:
            return self.run(*args)
        except GitError:
            return None

    def lines(self, *args: str) -> list[str]:
        """Run a command and return its non-empty output lines."""
        return [line for line in self.run(*args).splitlines() if line]
