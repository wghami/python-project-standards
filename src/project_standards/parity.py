"""Hook ↔ CI parity (HK-2, HK-5): every local hook stage is also run by CI."""

import re
from pathlib import Path

import yaml

from project_standards._typed import mapping, sequence, strings, text

DEFAULT_STAGE = "pre-commit"


def hook_stages(config_text: str) -> dict[str, set[str]]:
    """Map each git-hook stage used in a pre-commit config to the hook ids it runs."""
    data = mapping(yaml.safe_load(config_text) or {}, "pre-commit config")
    defaults = strings(data.get("default_stages", [DEFAULT_STAGE]), "default_stages")
    stages: dict[str, set[str]] = {}
    for repo in sequence(data.get("repos", []), "repos"):
        for raw_hook in sequence(mapping(repo, "repo").get("hooks", []), "hooks"):
            hook = mapping(raw_hook, "hook")
            hook_id = text(hook.get("id"), "hook id")
            for stage in strings(hook.get("stages", defaults), f"stages of {hook_id}"):
                stages.setdefault(stage, set()).add(hook_id)
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
