"""Load the project-owned ``standards.toml``."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

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


def _strings(table: dict[str, object], key: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = table.get(key)
    if value is None:
        return default
    items = cast("list[object]", value) if isinstance(value, list) else None
    if items is None or not all(isinstance(item, str) for item in items):
        msg = f"standards.toml: '{key}' must be a list of strings"
        raise TypeError(msg)
    return tuple(cast("list[str]", items))


def _table(data: dict[str, object], key: str) -> dict[str, object]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        msg = f"standards.toml: [{key}] must be a table"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def _rules(impact: dict[str, object]) -> tuple[DocRule, ...]:
    raw = impact.get("rules", [])
    if not isinstance(raw, list):
        msg = "standards.toml: [[doc_impact.rules]] must be an array of tables"
        raise TypeError(msg)
    tables = cast("list[dict[str, object]]", raw)
    return tuple(
        DocRule(paths=_strings(t, "paths", ()), docs=_strings(t, "docs", ())) for t in tables
    )


def load(root: Path) -> Config:
    """Read ``standards.toml`` from ``root``; missing file means defaults."""
    path = root / "standards.toml"
    data: dict[str, object] = tomllib.loads(path.read_text()) if path.exists() else {}
    commits, branches, impact = (_table(data, k) for k in ("commits", "branches", "doc_impact"))
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
    )
