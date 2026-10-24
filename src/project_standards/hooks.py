"""Local hooks are installed (HK-1)."""

from pathlib import Path

from project_standards._git import Git

STAGES = ("pre-commit", "commit-msg", "pre-push")


def check(git: Git) -> list[str]:
    """Return one error per missing pre-commit-managed git hook."""
    hooks_dir = git.cwd / git.run("rev-parse", "--git-path", "hooks")
    errors: list[str] = []
    for stage in STAGES:
        hook = Path(hooks_dir, stage)
        if not hook.exists() or "pre-commit" not in hook.read_text(errors="replace"):
            errors.append(f"git hook '{stage}' is not installed: run `uv run pre-commit install`")
    return errors
