[![CI](https://github.com/Owner/demo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Owner/demo/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fbadges%2Fcoverage.json)](https://github.com/Owner/demo/actions/workflows/ci.yml) [![docstrings](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fbadges%2Fdocstrings.json)](https://github.com/Owner/demo/actions/workflows/ci.yml) [![release](https://img.shields.io/github/v/release/Owner/demo?sort=semver)](https://github.com/Owner/demo/releases) [![python](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fmain%2Fpyproject.toml&query=%24.project%5B%27requires-python%27%5D&label=python&logo=python&logoColor=white)](pyproject.toml) [![license](https://img.shields.io/github/license/Owner/demo)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![types: pyright strict](https://img.shields.io/badge/types-pyright%20strict-2a6db2)](docs/standards/03-code-quality.md) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](.pre-commit-config.yaml) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org) [![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)

**7 gates.** 5 run on your machine before code leaves it (`pre-commit` / `pre-push` hooks); CI reruns every one of them, and scheduled jobs add the slow and the external checks.

| Gate | 💻 commit | 💻 push | ☁️ CI | 🌙 nightly | 📅 weekly |
|---|:-:|:-:|:-:|:-:|:-:|
| pre-commit-hooks: `end-of-file-fixer` · `trailing-whitespace` | ✓ |  | ✓ |  |  |
| ruff check (`ruff-check`) | ✓ |  | ✓ |  |  |
| commit-msg (`commit-msg`) | ✓ |  | ✓ |  |  |
| tests (`tests`) |  | ✓ | ✓ |  |  |
| nameless (`nameless`) |  | ✓ | ✓ |  |  |
| secret scan |  |  | ✓ |  |  |
| audit |  |  | ✓ |  |  |
