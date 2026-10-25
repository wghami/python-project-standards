"""Load the project-owned ``standards.toml``."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from project_standards._typed import mapping, sequence, strings, text

DEFAULT_TYPES = (
    "feat",
    "fix",
    "perf",
    "refactor",
    "test",
    "docs",
    "build",
    "ci",
    "chore",
    "style",
    "revert",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DocRule:
    """Source paths and the documentation that must change with them."""

    paths: tuple[str, ...]
    docs: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Readme:
    """Where the README badges point (DOC-10)."""

    repository: str = ""
    template_repository: str = "wghami/python-project-standards"
    badges_branch: str = "badges"
    standards_docs: str = "docs/standards"
    skip_jobs: tuple[str, ...] = (
        "pre-commit-stage",
        "pre-push-stage",
        "release",
        "badges",
        "report",
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class Config:
    """Settings for every check, read from ``standards.toml``."""

    types: tuple[str, ...] = DEFAULT_TYPES
    scopes: tuple[str, ...] = ()
    scope_required_for: tuple[str, ...] = ("feat", "fix", "perf", "refactor")
    max_header_length: int = 72
    allowed_branches: tuple[str, ...] = ("main",)
    extra_branch_prefixes: tuple[str, ...] = ("dependabot/",)
    watched: tuple[str, ...] = ()
    doc_rules: tuple[DocRule, ...] = field(default=())
    releasing_types: tuple[str, ...] = ("feat", "fix", "perf")
    readme: Readme = field(default_factory=Readme)


def _strings(table: dict[str, object], key: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = table.get(key)
    return default if value is None else tuple(strings(value, f"standards.toml: '{key}'"))


def _rules(impact: dict[str, object]) -> tuple[DocRule, ...]:
    tables = sequence(impact.get("rules", []), "standards.toml: [[doc_impact.rules]]")
    return tuple(
        DocRule(paths=_strings(t, "paths", ()), docs=_strings(t, "docs", ()))
        for t in (mapping(raw, "standards.toml: [[doc_impact.rules]] entry") for raw in tables)
    )


def _text(table: dict[str, object], key: str, default: str) -> str:
    return text(table.get(key, default), f"standards.toml: '{key}'")


def _readme(table: dict[str, object]) -> Readme:
    defaults = Readme()
    return Readme(
        repository=_text(table, "repository", defaults.repository),
        template_repository=_text(table, "template_repository", defaults.template_repository),
        badges_branch=_text(table, "badges_branch", defaults.badges_branch),
        standards_docs=_text(table, "standards_docs", defaults.standards_docs),
        skip_jobs=_strings(table, "skip_jobs", defaults.skip_jobs),
    )


def load(root: Path) -> Config:
    """Read ``standards.toml`` from ``root``; missing file means defaults."""
    path = root / "standards.toml"
    data: dict[str, object] = tomllib.loads(path.read_text()) if path.exists() else {}
    commits, branches, impact, readme = (
        mapping(data.get(k, {}), f"standards.toml: [{k}]")
        for k in ("commits", "branches", "doc_impact", "readme")
    )
    rules = _rules(impact)
    max_len = commits.get("max_header_length", 72)
    if not isinstance(max_len, int):
        msg = "standards.toml: 'max_header_length' must be an integer"
        raise TypeError(msg)
    return Config(
        types=_strings(commits, "types", DEFAULT_TYPES),
        scopes=_strings(commits, "scopes", ()),
        scope_required_for=_strings(
            commits, "scope_required_for", ("feat", "fix", "perf", "refactor")
        ),
        max_header_length=max_len,
        allowed_branches=_strings(branches, "allowed", ("main",)),
        extra_branch_prefixes=_strings(branches, "extra_prefixes", ("dependabot/",)),
        watched=_strings(impact, "watched", ()),
        doc_rules=rules,
        releasing_types=_strings(commits, "releasing_types", ("feat", "fix", "perf")),
        readme=_readme(readme),
    )
