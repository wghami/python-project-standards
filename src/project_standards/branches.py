"""Branch naming (BR-1)."""

import re

from project_standards.config import Config


def check_branch(name: str, config: Config) -> list[str]:
    """Return the problems with a branch name (empty list = valid).

    ``HEAD`` (a detached checkout, as in CI) is always accepted.
    """
    if name in {"HEAD", *config.allowed_branches}:
        return []
    if any(name.startswith(prefix) for prefix in config.extra_branch_prefixes):
        return []
    kinds = "|".join(map(re.escape, config.types))
    if re.fullmatch(rf"(?:{kinds})/[a-z0-9][a-z0-9._-]*", name):
        return []
    return [
        (
            f"branch '{name}' must be '<type>/<topic>' with type in {', '.join(config.types)} "
            "and a lower-case topic (e.g. feat/rule-compiler)"
        )
    ]
