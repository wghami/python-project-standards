"""Consistency of the standards documents themselves (STD-3).

Rules are table rows whose first cell is an ID such as ``COV-2``. IDs must be unique, every cell
must be filled in, every hook must be documented, and every ``standards <command>`` cited by the
documents must exist (and the reverse), so the documents cannot drift away from the tooling.
"""

import re
from collections.abc import Iterable
from pathlib import Path

from project_standards.parity import hook_stages

_ROW = re.compile(r"^\|\s*(?P<id>[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+)\s*\|(?P<rest>.*)$")
_COMMAND = re.compile(r"\bstandards (?P<cmd>check-[a-z-]+)")


def _cells(rest: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", rest.rstrip().removesuffix("|"))]


def _rule_errors(path: Path, text: str, seen: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        row = _ROW.match(line)
        if row is None:
            continue
        where, rule_id = f"{path}:{number}", row["id"]
        if rule_id in seen:
            errors.append(f"{where}: rule {rule_id} is already defined at {seen[rule_id]}")
        seen.setdefault(rule_id, where)
        if any(not cell for cell in _cells(row["rest"])):
            errors.append(
                f"{where}: rule {rule_id} has an empty cell (every rule names its enforcer)"
            )
    return errors


def _hook_errors(docs_dir: Path, hook_config: Path, corpus: str) -> list[str]:
    hook_ids: set[str] = set()
    for ids in hook_stages(hook_config.read_text()).values():
        hook_ids |= ids
    return [
        f"hook `{h}` ({hook_config}) is not documented in {docs_dir}"
        for h in sorted(hook_ids)
        if f"`{h}`" not in corpus
    ]


def check(docs_dir: Path, hook_config: Path | None, commands: Iterable[str]) -> list[str]:
    """Return every inconsistency between the standards and the tooling."""
    files = sorted(docs_dir.rglob("*.md"))
    if not files:
        return [f"{docs_dir}: no standards documents found"]
    errors: list[str] = []
    seen: dict[str, str] = {}
    texts = [path.read_text(encoding="utf-8") for path in files]
    for path, text in zip(files, texts, strict=True):
        errors += _rule_errors(path, text, seen)
    corpus = "\n".join(texts)
    cited = {m["cmd"] for m in _COMMAND.finditer(corpus)}
    known = set(commands)
    errors.extend(f"standards cite unknown command `standards {c}`" for c in sorted(cited - known))
    errors.extend(f"`standards {c}` is not documented in {docs_dir}" for c in sorted(known - cited))
    if hook_config is not None and hook_config.exists():
        errors += _hook_errors(docs_dir, hook_config, corpus)
    return errors
