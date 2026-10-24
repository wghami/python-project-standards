"""Hook ↔ CI parity (HK-2, HK-5): every local hook stage is also run by CI."""

import re
from pathlib import Path
from typing import cast

import yaml

DEFAULT_STAGE = "pre-commit"


def hook_stages(config_text: str) -> dict[str, set[str]]:
    """Map each git-hook stage used in a pre-commit config to the hook ids it runs."""
    data = cast("dict[str, object]", yaml.safe_load(config_text) or {})
    defaults = cast("list[str]", data.get("default_stages", [DEFAULT_STAGE]))
    stages: dict[str, set[str]] = {}
    for repo in cast("list[dict[str, object]]", data.get("repos", [])):
        for hook in cast("list[dict[str, object]]", repo.get("hooks", [])):
            for stage in cast("list[str]", hook.get("stages", defaults)):
                stages.setdefault(stage, set()).add(cast("str", hook["id"]))
    return stages


def _runs_stage(workflow: str, stage: str) -> bool:
    for line in workflow.splitlines():
        if (
            "pre-commit run" in line
            and "--all-files" in line
            and re.search(rf"--hook-stage[ =]{re.escape(stage)}\b", line)
        ):
            return True
    return False


def check(config_path: Path, workflow_path: Path) -> list[str]:
    """Return one error per hook stage that CI does not reproduce."""
    stages = hook_stages(config_path.read_text())
    workflow = workflow_path.read_text()
    errors: list[str] = []
    for stage, ids in sorted(stages.items()):
        if stage == "commit-msg":
            if "standards check-commits" not in workflow:
                errors.append(
                    f"{workflow_path}: commit-msg hooks run locally but CI never runs "
                    "`standards check-commits`"
                )
        elif not _runs_stage(workflow, stage):
            errors.append(
                f"{workflow_path}: no `pre-commit run --all-files --hook-stage {stage}` "
                f"step, so {', '.join(sorted(ids))} would only run locally"
            )
    return errors
