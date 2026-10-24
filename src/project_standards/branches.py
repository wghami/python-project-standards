"""Branch naming (BR-1)."""

import re

from project_standards.config import Config

_TOPIC = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def check_branch(name: str, config: Config) -> list[str]:
    """Return the problems with a branch name (empty list = valid).

    ``HEAD`` (a detached checkout, as in CI) is always accepted.
    """
    if name in {"HEAD", *config.allowed_branches}:
        return []
    if any(name.startswith(prefix) for prefix in config.extra_branch_prefixes):
        return []
    kind, slash, topic = name.partition("/")
    if slash and kind in config.types and _TOPIC.match(topic):
        return []
    return [
        (
            f"branch '{name}' must be '<type>/<topic>' with type in {', '.join(config.types)} "
            "and a lower-case topic (e.g. feat/rule-compiler)"
        )
    ]
