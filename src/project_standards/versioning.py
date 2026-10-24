"""Version ↔ tag consistency (VER-1, VER-2, VER-3).

The version is derived from git tags (``hatch-vcs``), so code and tag cannot disagree. What can
still go wrong is checked here: a static version sneaking into ``pyproject.toml``, a tag that
exists locally but not on GitHub (or points elsewhere), and releasable commits left untagged.
"""

import re
import tomllib
from pathlib import Path

from project_standards import commits
from project_standards._git import Git
from project_standards.config import Config

_TAG = re.compile(r"^v\d+\.\d+\.\d+$")


def check_pyproject(root: Path) -> list[str]:
    """The version must be dynamic (from tags), never written by hand (VER-1)."""
    project = tomllib.loads((root / "pyproject.toml").read_text()).get("project", {})
    errors: list[str] = []
    if "version" in project:
        errors.append("pyproject.toml sets [project].version; it must come from git tags (VER-1)")
    if "version" not in project.get("dynamic", []):
        errors.append('pyproject.toml must declare dynamic = ["version"] (VER-1)')
    return errors


def latest_tag(git: Git) -> str | None:
    """The newest ``vX.Y.Z`` tag reachable from ``HEAD``, if any."""
    tag = git.try_run("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*")
    return tag if tag is not None and _TAG.match(tag) else None


def _remote_commit(git: Git, remote: str, tag: str) -> str | None:
    found: dict[str, str] = {}
    for line in git.lines("ls-remote", "--tags", remote, f"refs/tags/{tag}*"):
        sha, ref = line.split("\t", 1)
        found[ref] = sha
    return found.get(f"refs/tags/{tag}^{{}}", found.get(f"refs/tags/{tag}"))


def check_published(git: Git, remote: str) -> list[str]:
    """The latest reachable tag exists on ``remote`` and points to the same commit (VER-3)."""
    tag = latest_tag(git)
    if tag is None:
        if git.lines("tag", "--list", "v[0-9]*"):
            return ["tags exist but none is reachable from HEAD; rebase on the default branch"]
        return []  # bootstrap: nothing has been released yet
    local = git.run("rev-parse", f"{tag}^{{commit}}")
    remote_sha = _remote_commit(git, remote, tag)
    if remote_sha is None:
        return [f"tag {tag} is not on '{remote}': git push {remote} {tag}"]
    if remote_sha != local:
        return [f"tag {tag} points to {remote_sha[:10]} on '{remote}' but {local[:10]} locally"]
    return []


def check_released(git: Git, config: Config) -> list[str]:
    """No releasable commit is left without a tag (VER-2); run after the release job."""
    tag = latest_tag(git)
    revision = f"{tag}..HEAD" if tag else "HEAD"
    raw = git.run("log", "--format=%H%x1f%B%x1e", revision)
    pending = [
        entry.split("\x1f", 1)[0][:10]
        for entry in (e.strip() for e in raw.split("\x1e"))
        if entry and commits.is_releasing(entry.split("\x1f", 1)[1], config)
    ]
    if pending:
        return [
            (
                f"releasable commits are not tagged ({', '.join(pending)}); the release job "
                "must run `cz bump` and push the tag (VER-2)"
            )
        ]
    return []
