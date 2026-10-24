"""Branch naming (BR-1)."""

import pytest

from project_standards.branches import check_branch
from project_standards.config import Config


@pytest.mark.parametrize(
    "name", ["main", "HEAD", "feat/rule-compiler", "fix/dst_1.2", "dependabot/uv/ruff-0.18"]
)
def test_valid_branches(name: str) -> None:
    assert check_branch(name, Config()) == []


@pytest.mark.parametrize("name", ["develop", "feature/x", "feat/", "feat/Upper", "wip"])
def test_invalid_branches(name: str) -> None:
    assert check_branch(name, Config()) != []
