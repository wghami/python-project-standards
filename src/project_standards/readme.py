"""README badges and the shift-left gates table (DOC-10), generated so they cannot go stale.

Both blocks live between marker comments in ``README.md``. They are derived from the files that
actually enforce the standards: the workflows, the hook configuration and ``.copier-answers.yml``.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import yaml

from project_standards._typed import mapping, maybe_sequence, sequence, text
from project_standards.config import Readme

LOCAL = "local"
_HOOK_COLUMNS = {"pre-commit": "💻 commit", "commit-msg": "💻 commit", "pre-push": "💻 push"}
_GATE_COLUMNS = ("💻 commit", "💻 push", "☁️ CI", "🌙 nightly", "📅 weekly")
_PYTHON_QUERY = quote("$.project['requires-python']", safe="")


def _q(url: str) -> str:
    return quote(url, safe="")


def _shield(label: str, image: str, link: str) -> str:
    return f"[![{label}]({image})]({link})"


@dataclass(frozen=True, slots=True, kw_only=True)
class Project:
    """What the README generator needs to know about a repository."""

    root: Path
    readme: Readme

    @property
    def repo(self) -> str:
        """``owner/name`` on GitHub."""
        return self.readme.repository

    def has(self, relative: str) -> bool:
        """True when ``relative`` exists in the repository."""
        return (self.root / relative).exists()

    def raw(self, branch: str, path: str) -> str:
        """URL of a file on a branch of the repository."""
        return f"https://raw.githubusercontent.com/{self.repo}/{branch}/{path}"


def _workflow_badge(project: Project, name: str, label: str, query: str) -> str:
    base = f"https://github.com/{project.repo}/actions/workflows/{name}"
    return _shield(label, f"{base}/badge.svg?{query}", base)


def _status(project: Project) -> list[str]:
    owner, name = project.repo.split("/", 1)
    row = [_workflow_badge(project, "ci.yml", "CI", "branch=main")]
    if project.has(".github/workflows/codeql.yml"):
        row.append(_workflow_badge(project, "codeql.yml", "CodeQL", "branch=main"))
    if project.has(".github/workflows/scorecard.yml"):
        row.append(
            _shield(
                "OpenSSF Scorecard",
                f"https://api.scorecard.dev/projects/github.com/{project.repo}/badge",
                f"https://scorecard.dev/viewer/?uri=github.com/{project.repo}",
            )
        )
    if project.has(".github/workflows/nightly.yml"):
        row.append(_workflow_badge(project, "nightly.yml", "Nightly", "event=schedule"))
    if project.has("mkdocs.yml"):
        site = f"https://{owner.lower()}.github.io/{name}/"
        row.append(
            _shield("docs", f"https://img.shields.io/website?url={_q(site)}&label=docs", site)
        )
    return row


def _measured(project: Project) -> list[str]:
    def metric(label: str, workflow: str) -> str:
        data = project.raw(project.readme.badges_branch, f"{label}.json")
        link = f"https://github.com/{project.repo}/actions/workflows/{workflow}"
        return _shield(label, f"https://img.shields.io/endpoint?url={_q(data)}", link)

    row = [metric("coverage", "ci.yml")]
    if project.has(".github/workflows/nightly.yml"):
        row.append(metric("mutation", "nightly.yml"))
    row.append(metric("docstrings", "ci.yml"))
    python = (
        "https://img.shields.io/badge/dynamic/toml"
        f"?url={_q(project.raw('main', 'pyproject.toml'))}&query={_PYTHON_QUERY}"
        "&label=python&logo=python&logoColor=white"
    )
    return [
        *row,
        _shield(
            "release",
            f"https://img.shields.io/github/v/release/{project.repo}?sort=semver",
            f"https://github.com/{project.repo}/releases",
        ),
        _shield("python", python, "pyproject.toml"),
        _shield("license", f"https://img.shields.io/github/license/{project.repo}", "LICENSE"),
    ]


def _built_with(project: Project) -> list[str]:
    docs = project.readme.standards_docs
    astral = "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh"
    row = [
        _shield("uv", f"{astral}/uv/main/assets/badge/v0.json", "https://github.com/astral-sh/uv"),
        _shield(
            "Ruff", f"{astral}/ruff/main/assets/badge/v2.json", "https://github.com/astral-sh/ruff"
        ),
        _shield(
            "types: pyright strict",
            "https://img.shields.io/badge/types-pyright%20strict-2a6db2",
            f"{docs}/03-code-quality.md",
        ),
        _shield(
            "pre-commit",
            "https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit",
            ".pre-commit-config.yaml",
        ),
        _shield(
            "Conventional Commits",
            "https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196?logo=conventionalcommits&logoColor=white",
            "https://www.conventionalcommits.org",
        ),
    ]
    if project.has(".copier-answers.yml"):
        answers = _q(project.raw("main", ".copier-answers.yml"))
        row.append(
            _shield(
                "standards",
                f"https://img.shields.io/badge/dynamic/yaml?url={answers}&query=%24._commit&label=standards&color=6f42c1",
                f"https://github.com/{project.readme.template_repository}",
            )
        )
    row.append(
        _shield(
            "Copier",
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json",
            "https://github.com/copier-org/copier",
        )
    )
    return row


def badges(project: Project) -> str:
    """Three rows: live status, measured quality, how the project is built."""
    rows = (_status(project), _measured(project), _built_with(project))
    return "\n".join(" ".join(row) for row in rows)


@dataclass(frozen=True, slots=True, kw_only=True)
class Gate:
    """One check and the stages that run it."""

    name: str
    stages: frozenset[str]


def _hook_gates(config: dict[str, object]) -> list[Gate]:
    defaults = {str(s) for s in sequence(config.get("default_stages", ["pre-commit"]), "stages")}
    gates: list[Gate] = []
    for raw_repo in sequence(config.get("repos", []), "repos"):
        repo = mapping(raw_repo, "repo")
        hooks = [mapping(h, "hook") for h in sequence(repo.get("hooks", []), "hooks")]
        groups = [hooks] if text(repo.get("repo"), "repo url") != LOCAL else [[h] for h in hooks]
        for group in groups:
            stages = {
                str(s) for h in group for s in sequence(h.get("stages", list(defaults)), "stages")
            }
            columns = {_HOOK_COLUMNS[s] for s in stages if s in _HOOK_COLUMNS} | {"☁️ CI"}
            label = " · ".join(f"`{text(h.get('id'), 'hook id')}`" for h in group)
            if len(group) > 1:
                label = (
                    f"{text(repo.get('repo'), 'repo url').rstrip('/').rsplit('/', 1)[-1]}: {label}"
                )
            else:
                label = f"{text(group[0].get('name', group[0].get('id')), 'hook name')} ({label})"
            gates.append(Gate(name=label, stages=frozenset(columns)))
    return gates


def _triggers(workflow: dict[str, object]) -> dict[str, object]:
    """The workflow's ``on:`` events. PyYAML (YAML 1.1) reads the key ``on`` as ``True``."""
    value: object = {}
    for key, item in workflow.items():
        if str(key) in {"on", "True"}:
            value = item
    if isinstance(value, str):
        return {value: None}
    events = maybe_sequence(value)
    if events is not None:
        return {str(event): None for event in events}
    return mapping(value, "on")


def _schedule_column(triggers: dict[str, object]) -> str | None:
    crons = [
        text(mapping(c, "schedule").get("cron"), "cron")
        for c in sequence(triggers.get("schedule", []), "schedule")
    ]
    if not crons:
        return None
    return "🌙 nightly" if all(c.split()[4] == "*" for c in crons) else "📅 weekly"


def _job_gates(root: Path, skip: tuple[str, ...]) -> list[Gate]:
    gates: list[Gate] = []
    for path in sorted((root / ".github" / "workflows").glob("*.yml")):
        workflow = mapping(yaml.safe_load(path.read_text(encoding="utf-8")), str(path))
        triggers = _triggers(workflow)
        scheduled = _schedule_column(triggers)
        on_pr = "pull_request" in triggers or "push" in triggers
        for job_id, raw_job in mapping(workflow.get("jobs", {}), "jobs").items():
            job = mapping(raw_job, f"job {job_id}")
            if job_id in skip:
                continue
            columns = {scheduled} if scheduled else set[str]()
            condition = str(job.get("if", ""))
            if on_pr:
                columns.add("🏷️ label" if "labels" in condition else "☁️ CI")
            if columns:  # a manual-only workflow is not a gate
                gates.append(Gate(name=str(job.get("name", job_id)), stages=frozenset(columns)))
    return gates


def gates_table(project: Project) -> str:
    """The shift-left table: every gate and the earliest stages that run it."""
    hooks_file = project.root / ".pre-commit-config.yaml"
    config = mapping(yaml.safe_load(hooks_file.read_text(encoding="utf-8")) or {}, str(hooks_file))
    hook_gates = _hook_gates(config)
    gates = hook_gates + _job_gates(project.root, project.readme.skip_jobs)
    local = sum(1 for g in hook_gates if g.stages & {"💻 commit", "💻 push"})
    lines = [
        (
            f"**{len(gates)} gates.** {local} run on your machine before code leaves it "
            "(`pre-commit` / `pre-push` hooks); CI reruns every one of them, and scheduled jobs "
            "add the slow and the external checks."
        ),
        "",
        "| Gate | " + " | ".join(_GATE_COLUMNS) + " |",
        "|---|" + "|".join(":-:" for _ in _GATE_COLUMNS) + "|",
    ]
    for gate in gates:
        marks = [
            "🏷️" if c == "☁️ CI" and "🏷️ label" in gate.stages else ("✓" if c in gate.stages else "")
            for c in _GATE_COLUMNS
        ]
        lines.append(f"| {gate.name} | " + " | ".join(marks) + " |")
    return "\n".join(lines)


_BLOCK = "<!-- standards:{name}:{edge} -->"


def _replace(readme: str, name: str, body: str) -> str | None:
    start, end = _BLOCK.format(name=name, edge="start"), _BLOCK.format(name=name, edge="end")
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(readme) is None:
        return None
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", readme, count=1)


def render(project: Project, readme: str) -> tuple[str, list[str]]:
    """Return ``readme`` with both blocks regenerated, and the markers that are missing."""
    missing: list[str] = []
    for name, body in (("badges", badges(project)), ("gates", gates_table(project))):
        updated = _replace(readme, name, body)
        if updated is None:
            missing.append(
                f"README.md has no {_BLOCK.format(name=name, edge='start')} … "
                f"{_BLOCK.format(name=name, edge='end')} block"
            )
        else:
            readme = updated
    return readme, missing


def check(project: Project, *, write: bool) -> list[str]:
    """Regenerate the README blocks; with ``write=False`` only report that they are stale."""
    path = project.root / "README.md"
    current = path.read_text(encoding="utf-8")
    updated, missing = render(project, current)
    if missing:
        return missing
    if updated == current:
        return []
    if write:
        path.write_text(updated, encoding="utf-8")
        return []
    return ["README.md badges or gates table are out of date: run `standards readme --write`"]
