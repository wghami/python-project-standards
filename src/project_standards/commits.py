"""Conventional Commits checks (COM-1, COM-2, COM-4)."""

import re
from dataclasses import dataclass

from project_standards.config import Config

HEADER = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9][a-z0-9-]*)\))?(?P<bang>!)?: (?P<subject>.+)$"
)
_PASS_THROUGH = (re.compile(r"^Merge "), re.compile(r'^Revert "'))
_AUTOSQUASH = re.compile(r"^(fixup|squash|amend)! ")
_BREAKING = re.compile(r"^BREAKING[ -]CHANGE: \S", re.MULTILINE)


@dataclass(frozen=True, slots=True, kw_only=True)
class Header:
    """A parsed commit header."""

    type: str
    scope: str | None
    breaking: bool
    subject: str


def parse_header(line: str) -> Header | None:
    """Parse a Conventional Commit header, or return ``None`` if it is not one."""
    match = HEADER.match(line)
    if match is None:
        return None
    return Header(
        type=match["type"],
        scope=match["scope"],
        breaking=match["bang"] is not None,
        subject=match["subject"],
    )


def clean(message: str) -> str:
    """Drop git comment lines and surrounding blank lines from a message."""
    lines = [line for line in message.splitlines() if not line.startswith("#")]
    return "\n".join(lines).strip()


def is_breaking(message: str) -> bool:
    """True when the message declares a breaking change, by ``!`` or footer."""
    text = clean(message)
    header = parse_header(text.split("\n", 1)[0])
    return (header is not None and header.breaking) or _BREAKING.search(text) is not None


def _header_errors(header: Header, config: Config) -> list[str]:
    errors: list[str] = []
    if header.type not in config.types:
        errors.append(f"type '{header.type}' is not one of: {', '.join(config.types)}")
    if header.scope is None and header.type in config.scope_required_for:
        errors.append(f"type '{header.type}' requires a scope: {', '.join(config.scopes)}")
    if header.scope is not None and header.scope not in config.scopes:
        errors.append(f"scope '{header.scope}' is not one of: {', '.join(config.scopes)}")
    if header.subject.endswith("."):
        errors.append("the summary must not end with a period")
    if header.subject[0].isupper():
        errors.append("the summary starts with a lower-case imperative verb ('add', not 'Add')")
    return errors


def check_message(message: str, config: Config, *, allow_autosquash: bool = False) -> list[str]:
    """Return every rule the commit message breaks (empty list = valid)."""
    text = clean(message)
    if not text:
        return ["the commit message is empty"]
    first, _, rest = text.partition("\n")
    if any(p.match(first) for p in _PASS_THROUGH):
        return []
    if _AUTOSQUASH.match(first):
        return [] if allow_autosquash else ["fixup!/squash! commits must be squashed before merge"]
    header = parse_header(first)
    if header is None:
        return [f"'{first}' is not '<type>(<scope>): <summary>' (Conventional Commits)"]
    errors = _header_errors(header, config)
    if len(first) > config.max_header_length:
        errors.append(
            f"the header is {len(first)} characters; the limit is {config.max_header_length}"
        )
    if rest and not rest.startswith("\n"):
        errors.append("separate the header from the body with one blank line")
    if header.breaking and _BREAKING.search(text) is None:
        errors.append("'!' needs a 'BREAKING CHANGE: <what breaks>' footer (COM-2)")
    return errors


def is_releasing(message: str, config: Config) -> bool:
    """True when the commit triggers a release (a feat/fix/perf or a breaking change)."""
    header = parse_header(clean(message).split("\n", 1)[0])
    if header is None:
        return False
    return header.type in config.releasing_types or is_breaking(message)
