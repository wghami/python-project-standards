"""The Copier template renders a project whose standards and tooling agree (STD-3)."""

import tomllib
import warnings
from pathlib import Path

import pytest
import yaml
from copier import run_copy
from copier.errors import DirtyLocalWarning

from project_standards import parity, standards_docs, versioning
from project_standards.cli import commands
from project_standards.config import load

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = {
    "project_name": "Demo Project",
    "author_name": "Test Author",
    "github_owner": "wghami",
    "description": "A demo. " + "x" * 200,
    "commit_scopes": ["core", "docs"],
}


@pytest.fixture(scope="module")
def rendered(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("rendered")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DirtyLocalWarning)  # local edits are what we test
        run_copy(
            str(ROOT),
            destination,
            data=ANSWERS,
            defaults=True,
            skip_tasks=True,
            quiet=True,
            vcs_ref="HEAD",
            unsafe=True,
        )
    return destination


def test_names_are_derived(rendered: Path) -> None:
    project = tomllib.loads((rendered / "pyproject.toml").read_text())["project"]
    assert project["name"] == "demo-project"
    assert (rendered / "src" / "demo_project" / "__init__.py").exists()
    assert project["requires-python"] == ">=3.12,<3.13"


def test_version_is_dynamic(rendered: Path) -> None:
    assert versioning.check_pyproject(rendered) == []


def test_standards_toml_is_valid(rendered: Path) -> None:
    config = load(rendered)
    assert config.scopes == ("core", "docs")
    assert config.doc_rules


def test_standards_documents_match_the_tooling(rendered: Path) -> None:
    docs = rendered / "docs" / "standards"
    assert standards_docs.check(docs, rendered / ".pre-commit-config.yaml", commands()) == []


def test_ci_reruns_every_hook_stage(rendered: Path) -> None:
    workflow = rendered / ".github" / "workflows" / "ci.yml"
    assert parity.check(rendered / ".pre-commit-config.yaml", workflow) == []


def test_answers_are_recorded(rendered: Path) -> None:
    answers = yaml.safe_load((rendered / ".copier-answers.yml").read_text())
    assert answers["_src_path"] == str(ROOT)
    assert answers["package_name"] == "demo_project"


def test_rendered_files_have_one_trailing_newline(rendered: Path) -> None:
    for path in rendered.rglob("*"):
        if path.is_file() and path.suffix in {".toml", ".yml", ".yaml", ".md", ".py", ""}:
            text = path.read_text()
            assert not text or (text.endswith("\n") and not text.endswith("\n\n")), path


def test_rendered_python_respects_the_line_length(rendered: Path) -> None:
    long_description = "x" * 200  # descriptions can be long; code lines cannot
    assert long_description not in (rendered / "src" / "demo_project" / "__init__.py").read_text()
    for path in rendered.rglob("*.py"):
        assert all(len(line) <= 100 for line in path.read_text().splitlines()), path
