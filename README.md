# python-project-standards

<!-- standards:badges:start -->
[![CI](https://github.com/wghami/python-project-standards/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/wghami/python-project-standards/actions/workflows/ci.yml) [![CodeQL](https://github.com/wghami/python-project-standards/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/wghami/python-project-standards/actions/workflows/codeql.yml) [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/wghami/python-project-standards/badge)](https://scorecard.dev/viewer/?uri=github.com/wghami/python-project-standards) [![Nightly](https://github.com/wghami/python-project-standards/actions/workflows/nightly.yml/badge.svg?event=schedule)](https://github.com/wghami/python-project-standards/actions/workflows/nightly.yml) [![docs](https://img.shields.io/website?url=https%3A%2F%2Fwghami.github.io%2Fpython-project-standards%2F&label=docs)](https://wghami.github.io/python-project-standards/)
[![coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fwghami%2Fpython-project-standards%2Fbadges%2Fcoverage.json)](https://github.com/wghami/python-project-standards/actions/workflows/ci.yml) [![mutation](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fwghami%2Fpython-project-standards%2Fbadges%2Fmutation.json)](https://github.com/wghami/python-project-standards/actions/workflows/nightly.yml) [![docstrings](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fwghami%2Fpython-project-standards%2Fbadges%2Fdocstrings.json)](https://github.com/wghami/python-project-standards/actions/workflows/ci.yml) [![release](https://img.shields.io/github/v/release/wghami/python-project-standards?sort=semver)](https://github.com/wghami/python-project-standards/releases) [![python](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fwghami%2Fpython-project-standards%2Fmain%2Fpyproject.toml&query=%24.project%5B%27requires-python%27%5D&label=python&logo=python&logoColor=white)](pyproject.toml) [![license](https://img.shields.io/github/license/wghami/python-project-standards)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![types: pyright strict](https://img.shields.io/badge/types-pyright%20strict-2a6db2)](template/docs/standards/03-code-quality.md) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](.pre-commit-config.yaml) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org) [![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
<!-- standards:badges:end -->

Binding engineering standards for Python projects, **and the tooling that enforces them**:

- **`template/`**: a [Copier](https://copier.readthedocs.io) template containing the standards
  documents (`docs/standards/`), pre-commit hooks, GitHub Actions (CI with a 100 % coverage gate,
  automatic SemVer releases from Conventional Commits, CodeQL, nightly mutation testing, weekly
  drift and audit), and strict ruff / pyright / pytest configuration.
- **`standards`**: a CLI (this package) that turns the rules into checks: commit messages, branch
  names, suppressions, doc impact, version ↔ tag, hook ↔ CI parity, consistency of the standards
  documents, mutation score, template drift and installed hooks.

Full documentation of every feature: [`docs/`](docs/README.md).

## Shift left, by design

The standards follow one principle: every rule has a gate, and every gate runs at the earliest
stage that can run it. This repository is held to its own standards. Its gates:

<!-- standards:gates:start -->
**29 gates.** 21 run on your machine before code leaves it (`pre-commit` / `pre-push` hooks); CI reruns every one of them, and scheduled jobs add the slow and the external checks.

| Gate | 💻 commit | 💻 push | ☁️ CI | 🌙 nightly | 📅 weekly |
|---|:-:|:-:|:-:|:-:|:-:|
| pre-commit-hooks: `check-added-large-files` · `check-case-conflict` · `check-merge-conflict` · `check-toml` · `check-yaml` · `detect-private-key` · `end-of-file-fixer` · `trailing-whitespace` | ✓ |  | ✓ |  |  |
| gitleaks (`gitleaks`) | ✓ |  | ✓ |  |  |
| ruff format (`ruff-format`) | ✓ |  | ✓ |  |  |
| ruff check (`ruff-check`) | ✓ |  | ✓ |  |  |
| pyright (changed files) (`pyright`) | ✓ |  | ✓ |  |  |
| no silent suppressions (`suppressions`) | ✓ |  | ✓ |  |  |
| uv.lock in sync (`uv-lock`) | ✓ |  | ✓ |  |  |
| actionlint (`actionlint`) | ✓ |  | ✓ |  |  |
| zizmor (workflow security) (`zizmor`) | ✓ |  | ✓ |  |  |
| conventional commit message (`commit-msg`) | ✓ |  | ✓ |  |  |
| branch name (`branch-name`) |  | ✓ | ✓ |  |  |
| pyright (whole repository) (`pyright-all`) |  | ✓ | ✓ |  |  |
| tests (100 % line + branch coverage) (`tests`) |  | ✓ | ✓ |  |  |
| docstring coverage 100 % (`docstrings`) |  | ✓ | ✓ |  |  |
| bandit (`bandit`) |  | ✓ | ✓ |  |  |
| docs build (strict) (`docs-build`) |  | ✓ | ✓ |  |  |
| docs changed with what they describe (`doc-impact`) |  | ✓ | ✓ |  |  |
| version from tags, tags published (`version-tag`) |  | ✓ | ✓ |  |  |
| standards consistent with tooling (`standards-docs`) |  | ✓ | ✓ |  |  |
| README badges and gates table up to date (`readme`) |  | ✓ | ✓ |  |  |
| every hook stage runs in CI (`hook-parity`) |  | ✓ | ✓ |  |  |
| commits, PR title, branch name |  |  | ✓ |  |  |
| render the template and run its pipeline |  |  | ✓ |  |  |
| secret scan (full history) |  |  | ✓ |  |  |
| dependency audit |  |  | ✓ |  |  |
| publish and verify docs |  |  | ✓ |  |  |
| CodeQL (Python, Actions) |  |  | ✓ |  | ✓ |
| mutation score ≥ 90 % |  |  | 🏷️ | ✓ |  |
| OpenSSF Scorecard |  |  | ✓ |  | ✓ |
<!-- standards:gates:end -->

## Start a project

```bash
uvx copier copy --trust gh:wghami/python-project-standards my-project
cd my-project && git add -A && git commit -m "chore: render from python-project-standards"
```

## Keep a project current

```bash
uvx copier update --trust
```

A weekly job in every project runs `standards check-template-drift` and opens an issue when a
newer release of this template exists.

## Change a standard

Edit the document under `template/docs/standards/` **and** its enforcement (CLI, hooks or
workflows) in the same PR. CI renders a sample project from the PR and runs its whole pipeline.
Merging releases a new version automatically. See
[`11-keeping-standards-current.md`](template/docs/standards/11-keeping-standards-current.md).

## Develop

```bash
uv sync
uv run pre-commit install
uv run pytest --cov
```
