"""``standards.toml`` is optional, and malformed values are refused."""

from pathlib import Path

import pytest

from project_standards.config import DEFAULT_TYPES, Config, DocRule, load


def test_missing_file_gives_defaults(tmp_path: Path) -> None:
    assert load(tmp_path) == Config()


def test_every_section_is_read(tmp_path: Path) -> None:
    (tmp_path / "standards.toml").write_text(
        """
[commits]
types = ["feat", "fix"]
scopes = ["core"]
scope_required_for = ["feat"]
max_header_length = 50
releasing_types = ["feat"]
[branches]
allowed = ["main", "develop"]
extra_prefixes = ["renovate/"]
[doc_impact]
watched = ["src/**"]
[[doc_impact.rules]]
paths = ["src/**"]
docs = ["docs/**"]
"""
    )
    assert load(tmp_path) == Config(
        types=("feat", "fix"),
        scopes=("core",),
        scope_required_for=("feat",),
        max_header_length=50,
        allowed_branches=("main", "develop"),
        extra_branch_prefixes=("renovate/",),
        watched=("src/**",),
        doc_rules=(DocRule(paths=("src/**",), docs=("docs/**",)),),
        releasing_types=("feat",),
    )


def test_defaults_include_the_conventional_types() -> None:
    assert "feat" in DEFAULT_TYPES
    assert "fix" in DEFAULT_TYPES


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("[commits]\ntypes = 'feat'", "standards.toml: 'types' must be a list"),
        ("[commits]\ntypes = ['feat', 1]", "standards.toml: 'types' must be a list of strings"),
        ("commits = 3", "standards.toml: [commits] must be a mapping"),
        ("[doc_impact]\nrules = 3", "standards.toml: [[doc_impact.rules]] must be a list"),
        (
            "[doc_impact]\nrules = [3]",
            "standards.toml: [[doc_impact.rules]] entry must be a mapping",
        ),
        (
            "[commits]\nmax_header_length = 'long'",
            "standards.toml: 'max_header_length' must be an integer",
        ),
    ],
)
def test_malformed_values_are_refused(tmp_path: Path, text: str, message: str) -> None:
    (tmp_path / "standards.toml").write_text(text)
    with pytest.raises(TypeError) as error:
        load(tmp_path)
    assert str(error.value) == message


def test_a_rule_without_paths_or_docs_has_none(tmp_path: Path) -> None:
    (tmp_path / "standards.toml").write_text("[[doc_impact.rules]]\n")
    assert load(tmp_path).doc_rules == (DocRule(paths=(), docs=()),)
