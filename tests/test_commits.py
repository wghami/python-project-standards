"""Conventional Commits rules (COM-1, COM-2)."""

import pytest

from project_standards.commits import check_message, is_breaking, is_releasing, parse_header
from project_standards.config import Config

CONFIG = Config(scopes=("core", "docs"))


def test_parse_header_reads_every_part() -> None:
    header = parse_header("feat(core)!: drop python 3.11")
    assert header is not None
    assert (header.type, header.scope, header.breaking, header.subject) == (
        "feat", "core", True, "drop python 3.11",
    )  # fmt: skip


def test_parse_header_rejects_free_text() -> None:
    assert parse_header("Add things") is None


@pytest.mark.parametrize(
    "message",
    [
        "feat(core): add the rule compiler",
        "docs: explain the bands",
        "fix(core): handle dst\n\nThe grid skipped an hour in March.",
        "feat(core)!: rename the api\n\nBREAKING CHANGE: /simulate is now /simulations",
        "# a git comment line\nchore: tidy",
        "Merge branch 'main' into feat/x",
        'Revert "feat(core): add x"',
    ],
)
def test_valid_messages_pass(message: str) -> None:
    assert check_message(message, CONFIG) == []


@pytest.mark.parametrize(
    ("message", "fragment"),
    [
        ("", "empty"),
        ("# only a comment", "empty"),
        ("Add things", "Conventional Commits"),
        ("feet(core): add x", "type 'feet'"),
        ("feat: add x", "requires a scope"),
        ("docs(website): add x", "scope 'website'"),
        ("docs: add x.", "period"),
        ("docs: Add x", "lower-case"),
        ("docs: " + "x" * 80, "the limit is 72"),
        ("docs: add x\nno blank line", "blank line"),
        ("feat(core)!: rename", "BREAKING CHANGE"),
        ("fixup! feat(core): add x", "squashed"),
    ],
)
def test_invalid_messages_explain_the_rule(message: str, fragment: str) -> None:
    errors = check_message(message, CONFIG)
    assert any(fragment in e for e in errors), errors


def test_autosquash_commits_are_allowed_locally() -> None:
    assert check_message("fixup! feat(core): add x", CONFIG, allow_autosquash=True) == []


def test_breaking_change_by_footer_only() -> None:
    assert is_breaking("refactor(core): x\n\nBREAKING CHANGE: the api moved")
    assert not is_breaking("refactor(core): x")
    assert not is_breaking("free text")


@pytest.mark.parametrize(
    ("message", "releasing"),
    [
        ("feat(core): x", True),
        ("fix(core): x", True),
        ("perf(core): x", True),
        ("docs: x", False),
        ("docs!: x\n\nBREAKING CHANGE: y", True),
        ("free text", False),
    ],
)
def test_releasing_commits(message: str, *, releasing: bool) -> None:
    assert is_releasing(message, CONFIG) is releasing
