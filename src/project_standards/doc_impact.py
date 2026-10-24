"""Doc-impact rule (DOC-6): watched files cannot change without their documentation."""

import re
from dataclasses import dataclass

from project_standards._git import Git
from project_standards.config import Config
from project_standards.globs import matches_any

_REVIEWED = re.compile(r"^Docs-Reviewed: *(?P<reason>\S.*)$", re.MULTILINE)


@dataclass(frozen=True, slots=True, kw_only=True)
class Change:
    """What a range of commits changed."""

    files: tuple[str, ...]
    messages: tuple[str, ...]


def collect(git: Git, base: str) -> Change | None:
    """Files and messages between ``merge-base(base, HEAD)`` and ``HEAD``; ``None`` if no base."""
    merge_base = git.try_run("merge-base", base, "HEAD")
    if merge_base is None:
        return None
    files = tuple(git.lines("diff", "--name-only", merge_base, "HEAD"))
    raw = git.run("log", "--format=%B%x1e", f"{merge_base}..HEAD")
    return Change(files=files, messages=tuple(m.strip() for m in raw.split("\x1e") if m.strip()))


def check(change: Change, config: Config) -> list[str]:
    """Return one error per watched change whose documentation was not updated."""
    if any(_REVIEWED.search(m) for m in change.messages):
        return []
    errors: list[str] = []
    for path in change.files:
        if not matches_any(path, config.watched):
            continue
        rules = [r for r in config.doc_rules if matches_any(path, r.paths)]
        if not rules:
            errors.append(
                f"{path}: watched but not mapped in [[doc_impact.rules]] of "
                "standards.toml; map it to the docs that describe it"
            )
            continue
        errors.extend(
            f"{path} changed, but none of {', '.join(rule.docs)} did. Update them, or add a "
            "'Docs-Reviewed: <why>' commit footer"
            for rule in rules
            if not any(matches_any(changed, rule.docs) for changed in change.files)
        )
    return errors
