"""``standards``: the command line that hooks and CI call."""

import argparse
import json
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import yaml

from project_standards import (
    badges,
    branches,
    commits,
    doc_impact,
    drift,
    hooks,
    mutation,
    parity,
    readme,
    site,
    standards_docs,
    suppressions,
    versioning,
)
from project_standards._git import Git, GitError
from project_standards.config import load

type Handler = Callable[[argparse.Namespace], list[str]]


def _root(args: argparse.Namespace) -> Path:
    return Path(args.root)


def _commit_msg(args: argparse.Namespace) -> list[str]:
    message = Path(args.file).read_text(encoding="utf-8")
    return commits.check_message(message, load(_root(args)), allow_autosquash=True)


def _commits(args: argparse.Namespace) -> list[str]:
    config = load(_root(args))
    raw = Git(_root(args)).run("log", "--format=%H%x1f%B%x1e", args.range)
    errors: list[str] = []
    for entry in filter(None, (e.strip() for e in raw.split("\x1e"))):
        sha, message = entry.split("\x1f", 1)
        errors.extend(f"{sha[:10]}: {e}" for e in commits.check_message(message, config))
    return errors


def _pr_title(args: argparse.Namespace) -> list[str]:
    config = load(_root(args))
    return [f"PR title: {e}" for e in commits.check_message(args.title, config, header_only=True)]


def _branch(args: argparse.Namespace) -> list[str]:
    name = args.name or Git(_root(args)).try_run("symbolic-ref", "--short", "HEAD") or "HEAD"
    return branches.check_branch(name, load(_root(args)))


def _suppressions(args: argparse.Namespace) -> list[str]:
    root = _root(args)
    names = args.paths or Git(root).lines("ls-files", "*.py", "*.pyi")
    return suppressions.check_files(root / name for name in names)


def _version(args: argparse.Namespace) -> list[str]:
    root, git = _root(args), Git(_root(args))
    errors = versioning.check_pyproject(root)
    if args.remote:
        errors += versioning.check_published(git, args.remote)
    if args.released:
        errors += versioning.check_released(git, load(root))
    return errors


def _doc_impact(args: argparse.Namespace) -> list[str]:
    base = args.base or os.environ.get("STANDARDS_BASE_REF") or "origin/main"
    change = doc_impact.collect(Git(_root(args)), base)
    if change is None:
        sys.stderr.write(f"note: '{base}' not found; doc-impact skipped (first push?)\n")
        return []
    return doc_impact.check(change, load(_root(args)))


def _parity(args: argparse.Namespace) -> list[str]:
    return parity.check(_root(args) / args.config, _root(args) / args.workflow)


def _standards(args: argparse.Namespace) -> list[str]:
    root = _root(args)
    return standards_docs.check(root / args.docs, root / args.config, commands())


def _mutation(args: argparse.Namespace) -> list[str]:
    return mutation.check(_root(args) / args.stats, args.min)


def _drift(args: argparse.Namespace) -> list[str]:
    return drift.check(_root(args) / args.answers, Git(_root(args)))


def _readme(args: argparse.Namespace) -> list[str]:
    config = load(_root(args)).readme
    if not config.repository:
        return ['standards.toml: set [readme] repository = "owner/name"']
    return readme.check(readme.Project(root=_root(args), readme=config), write=args.write)


def _badge(args: argparse.Namespace) -> list[str]:
    document = badges.measure(args.metric, _root(args) / args.source)
    out = _root(args) / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return []


def _site(args: argparse.Namespace) -> list[str]:
    try:
        return site.check(args.url, args.commit)
    except site.SiteError as error:
        return [str(error)]


def _hooks(args: argparse.Namespace) -> list[str]:
    return hooks.check(Git(_root(args)))


def _build() -> tuple[argparse.ArgumentParser, tuple[str, ...]]:
    parser = argparse.ArgumentParser(prog="standards", description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, handler: Handler, help_text: str) -> argparse.ArgumentParser:
        command = sub.add_parser(name, help=help_text)
        command.set_defaults(handler=handler)
        return command

    add("check-commit-msg", _commit_msg, "validate a commit message file").add_argument("file")
    add("check-commits", _commits, "validate every commit in a range").add_argument(
        "--range", required=True
    )
    add("check-pr-title", _pr_title, "validate a PR title").add_argument("title")
    add("check-branch-name", _branch, "validate the branch name").add_argument("--name")
    add("check-suppressions", _suppressions, "forbid pragmas and reasonless ignores").add_argument(
        "paths", nargs="*"
    )
    version = add("check-version", _version, "version comes from tags; tags are published")
    version.add_argument("--remote", help="also check the latest tag exists on this remote")
    version.add_argument("--released", action="store_true", help="no untagged releasable commit")
    add("check-doc-impact", _doc_impact, "docs change with what they describe").add_argument(
        "--base"
    )
    hook_parity = add("check-hook-parity", _parity, "every hook stage also runs in CI")
    hook_parity.add_argument("--config", default=".pre-commit-config.yaml")
    hook_parity.add_argument("--workflow", default=".github/workflows/ci.yml")
    docs = add("check-standards", _standards, "standards docs are consistent with the tooling")
    docs.add_argument("--docs", default="docs/standards")
    docs.add_argument("--config", default=".pre-commit-config.yaml")
    mutants = add("check-mutation-score", _mutation, "mutation score gate")
    mutants.add_argument("stats")
    mutants.add_argument("--min", type=float, required=True)
    add("check-template-drift", _drift, "project is on the latest standards release").add_argument(
        "--answers", default=".copier-answers.yml"
    )
    add("check-hooks-installed", _hooks, "git hooks are installed")
    add("readme", _readme, "regenerate (or check) README badges and gates").add_argument(
        "--write", action="store_true", help="rewrite README.md instead of failing when stale"
    )
    deployed = add("check-site", _site, "the deployed docs site serves every page of this build")
    deployed.add_argument("url", help="base URL of the deployed site")
    deployed.add_argument("--commit", help="the commit that was built (checks build.json)")
    badge = add("badge", _badge, "write a shields.io badge from a gate's report")
    badge.add_argument("metric", choices=["coverage", "docstrings", "mutation"])
    badge.add_argument("source", help="coverage.xml, interrogate output or mutmut stats")
    badge.add_argument("--out", required=True, help="where to write the badge JSON")
    return parser, tuple(sub.choices)


def commands() -> tuple[str, ...]:
    """Names of every ``standards`` subcommand (documented in the standards, STD-3)."""
    return _build()[1]


def main(argv: Sequence[str] | None = None) -> int:
    """Run one check; print its findings; return the process exit status."""
    args = _build()[0].parse_args(argv)
    handler: Handler = args.handler
    try:
        errors = handler(args)
    except (GitError, OSError, TypeError, ValueError, KeyError, yaml.YAMLError) as error:
        errors = [f"{type(error).__name__}: {error}"]
    for error in errors:
        sys.stderr.write(f"✗ {error}\n")
    if not errors:
        sys.stdout.write(f"✓ {args.command}\n")
    return 1 if errors else 0
