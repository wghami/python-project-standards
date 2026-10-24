"""Every local hook stage is reproduced by CI (HK-5)."""

from pathlib import Path

from project_standards.parity import check, hook_stages

CONFIG = """
default_stages: [pre-commit]
repos:
  - repo: local
    hooks:
      - {id: ruff, name: ruff, entry: ruff, language: system}
      - {id: tests, name: tests, entry: pytest, language: system, stages: [pre-push]}
      - {id: msg, name: msg, entry: x, language: system, stages: [commit-msg]}
"""

GOOD_WORKFLOW = """
- run: uv run pre-commit run --all-files --hook-stage pre-commit
- run: uv run pre-commit run --hook-stage=pre-push --all-files
- run: uv run standards check-commits --range x
"""


def test_hook_stages_use_defaults_and_overrides() -> None:
    assert hook_stages(CONFIG) == {
        "pre-commit": {"ruff"},
        "pre-push": {"tests"},
        "commit-msg": {"msg"},
    }


def test_empty_config_has_no_stages() -> None:
    assert hook_stages("") == {}
    assert hook_stages("repos:\n  - repo: local\n    hooks:\n      - id: a\n") == {
        "pre-commit": {"a"}
    }


def _paths(tmp_path: Path, workflow: str) -> tuple[Path, Path]:
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(CONFIG)
    ci = tmp_path / "ci.yml"
    ci.write_text(workflow)
    return config, ci


def test_complete_workflow_passes(tmp_path: Path) -> None:
    assert check(*_paths(tmp_path, GOOD_WORKFLOW)) == []


def test_missing_stages_are_reported(tmp_path: Path) -> None:
    errors = check(*_paths(tmp_path, "- run: uv run pre-commit run --hook-stage pre-push\n"))
    assert len(errors) == 3
    assert any("standards check-commits" in e for e in errors)
    assert any("tests" in e for e in errors)
