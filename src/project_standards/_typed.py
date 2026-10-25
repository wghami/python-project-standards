"""Narrow untyped data (YAML, TOML, JSON) to the shapes the checks rely on, or raise TypeError."""

from typing import cast


def mapping(value: object, what: str) -> dict[str, object]:
    """Return ``value`` as a mapping, or raise naming ``what``."""
    if not isinstance(value, dict):
        msg = f"{what} must be a mapping"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def sequence(value: object, what: str) -> list[object]:
    """Return ``value`` as a list, or raise naming ``what``."""
    if not isinstance(value, list):
        msg = f"{what} must be a list"
        raise TypeError(msg)
    return cast("list[object]", value)


def strings(value: object, what: str) -> list[str]:
    """Return ``value`` as a list of strings, or raise naming ``what``."""
    items = sequence(value, what)
    if not all(isinstance(item, str) for item in items):
        msg = f"{what} must be a list of strings"
        raise TypeError(msg)
    return [str(item) for item in items]


def text(value: object, what: str) -> str:
    """Return ``value`` as a string, or raise naming ``what``."""
    if not isinstance(value, str):
        msg = f"{what} must be a string"
        raise TypeError(msg)
    return value


def maybe_sequence(value: object) -> list[object] | None:
    """Return ``value`` as a list when it is one, else ``None``."""
    return cast("list[object]", value) if isinstance(value, list) else None
