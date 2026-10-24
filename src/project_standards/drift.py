"""Template drift (STD-2): is this project on the latest standards release?"""

import re
from pathlib import Path
from typing import cast

import yaml

from project_standards._git import Git

_VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)")


def repo_url(src: str) -> str:
    """Expand copier's ``gh:owner/repo`` shorthand into a clonable URL."""
    if src.startswith("gh:"):
        return f"https://github.com/{src.removeprefix('gh:')}.git"
    return src


def _version(text: str) -> tuple[int, int, int] | None:
    match = _VERSION.match(text)
    return None if match is None else (int(match[1]), int(match[2]), int(match[3]))


def check(answers_path: Path, git: Git) -> list[str]:
    """Compare the template release a project was rendered from with the newest one."""
    answers = cast("dict[str, str]", yaml.safe_load(answers_path.read_text()))
    current = _version(answers.get("_commit", ""))
    if current is None:
        return [
            (
                f"{answers_path}: _commit '{answers.get('_commit')}' is not a release tag; "
                "update from a tagged template release"
            )
        ]
    tags = git.lines("ls-remote", "--tags", "--refs", repo_url(answers["_src_path"]))
    released = [v for line in tags if (v := _version(line.rsplit("/", 1)[-1])) is not None]
    latest = max(released, default=current)
    if latest > current:
        shown = ".".join(map(str, latest))
        return [
            (
                f"standards template v{shown} is available (this project uses "
                f"{answers['_commit']}); run `copier update`"
            )
        ]
    return []
