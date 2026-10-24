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
        ("[commits]\ntypes = 'feat'", "'types' must be a list of strings"),
        ("[commits]\ntypes = ['feat', 1]", "'types' must be a list of strings"),
        ("commits = 3", r"\[commits\] must be a table"),
        ("[doc_impact]\nrules = 3", "must be an array of tables"),
        ("[commits]\nmax_header_length = 'long'", "must be an integer"),
    ],
)
def test_malformed_values_are_refused(tmp_path: Path, text: str, message: str) -> None:
    (tmp_path / "standards.toml").write_text(text)
    with pytest.raises(TypeError, match=message):
        load(tmp_path)
