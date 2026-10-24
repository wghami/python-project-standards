"""Docs must change together with what they describe (DOC-6)."""

from conftest import Repo
from project_standards.config import Config, DocRule
from project_standards.doc_impact import Change, check, collect

CONFIG = Config(
    watched=("src/**", "pyproject.toml"),
    doc_rules=(DocRule(paths=("src/engine/**",), docs=("docs/engine.md",)),),
)


def test_missing_base_skips(repo: Repo) -> None:
    repo.commit("feat(core): x")
    assert collect(repo.git, "origin/main") is None


def test_collect_reads_files_and_messages(repo: Repo) -> None:
    base = repo.commit("chore: start")
    repo.commit("feat(core): x\n\nDocs-Reviewed: internal", {"src/engine/a.py": "x"})
    change = collect(repo.git, base)
    assert change == Change(
        files=("src/engine/a.py",), messages=("feat(core): x\n\nDocs-Reviewed: internal",)
    )


def test_mapped_change_with_its_doc_passes() -> None:
    change = Change(files=("src/engine/a.py", "docs/engine.md"), messages=("feat(core): x",))
    assert check(change, CONFIG) == []


def test_mapped_change_without_its_doc_fails() -> None:
    change = Change(files=("src/engine/a.py",), messages=("feat(core): x",))
    assert "docs/engine.md" in check(change, CONFIG)[0]


def test_unmapped_watched_file_fails() -> None:
    change = Change(files=("pyproject.toml",), messages=("build: x",))
    assert "not mapped" in check(change, CONFIG)[0]


def test_unwatched_files_are_ignored() -> None:
    assert check(Change(files=("README.md",), messages=("docs: x",)), CONFIG) == []


def test_docs_reviewed_footer_waives_the_rule() -> None:
    change = Change(files=("src/engine/a.py",), messages=("fix(core): x\n\nDocs-Reviewed: typo",))
    assert check(change, CONFIG) == []
