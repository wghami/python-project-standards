"""The feature documentation stays complete and navigable (DOC-4, DOC-6)."""

import re
from pathlib import Path

import pytest

from project_standards.cli import commands

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = sorted(DOCS.glob("*.md"))
_LINK = re.compile(r"\]\((?!https?://|#)([^)#\s]+)")


def test_every_page_is_linked_from_the_index() -> None:
    index = (DOCS / "README.md").read_text()
    unlinked = [p.name for p in PAGES if p.name != "README.md" and f"]({p.name})" not in index]
    assert unlinked == []


@pytest.mark.parametrize("page", [*PAGES, ROOT / "README.md"], ids=lambda p: p.name)
def test_relative_links_resolve(page: Path) -> None:
    broken = [t for t in _LINK.findall(page.read_text()) if not (page.parent / t).exists()]
    assert broken == []


def test_every_command_has_a_feature_page() -> None:
    corpus = "\n".join(p.read_text() for p in PAGES)
    assert [c for c in commands() if f"`standards {c}" not in corpus] == []
