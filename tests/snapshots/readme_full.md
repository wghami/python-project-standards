# Demo
<!-- standards:badges:start -->
[![CI](https://github.com/Owner/demo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Owner/demo/actions/workflows/ci.yml) [![CodeQL](https://github.com/Owner/demo/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/Owner/demo/actions/workflows/codeql.yml) [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/Owner/demo/badge)](https://scorecard.dev/viewer/?uri=github.com/Owner/demo) [![Nightly](https://github.com/Owner/demo/actions/workflows/nightly.yml/badge.svg?event=schedule)](https://github.com/Owner/demo/actions/workflows/nightly.yml) [![docs](https://img.shields.io/website?url=https%3A%2F%2Fowner.github.io%2Fdemo%2F&label=docs)](https://owner.github.io/demo/)
[![coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fbadges%2Fcoverage.json)](https://github.com/Owner/demo/actions/workflows/ci.yml) [![mutation](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fbadges%2Fmutation.json)](https://github.com/Owner/demo/actions/workflows/nightly.yml) [![docstrings](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fbadges%2Fdocstrings.json)](https://github.com/Owner/demo/actions/workflows/ci.yml) [![release](https://img.shields.io/github/v/release/Owner/demo?sort=semver)](https://github.com/Owner/demo/releases) [![python](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fmain%2Fpyproject.toml&query=%24.project%5B%27requires-python%27%5D&label=python&logo=python&logoColor=white)](pyproject.toml) [![license](https://img.shields.io/github/license/Owner/demo)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![types: pyright strict](https://img.shields.io/badge/types-pyright%20strict-2a6db2)](docs/standards/03-code-quality.md) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](.pre-commit-config.yaml) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org) [![standards](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOwner%2Fdemo%2Fmain%2F.copier-answers.yml&query=%24._commit&label=standards&color=6f42c1)](https://github.com/wghami/python-project-standards) [![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
<!-- standards:badges:end -->

text

<!-- standards:gates:start -->
**10 gates.** 5 run on your machine before code leaves it (`pre-commit` / `pre-push` hooks); CI reruns every one of them, and scheduled jobs add the slow and the external checks.

| Gate | 💻 commit | 💻 push | ☁️ CI | 🌙 nightly | 📅 weekly |
|---|:-:|:-:|:-:|:-:|:-:|
| pre-commit-hooks: `end-of-file-fixer` · `trailing-whitespace` | ✓ |  | ✓ |  |  |
| ruff check (`ruff-check`) | ✓ |  | ✓ |  |  |
| commit-msg (`commit-msg`) | ✓ |  | ✓ |  |  |
| tests (`tests`) |  | ✓ | ✓ |  |  |
| nameless (`nameless`) |  | ✓ | ✓ |  |  |
| secret scan |  |  | ✓ |  |  |
| audit |  |  | ✓ |  |  |
| lint everything |  |  | ✓ |  |  |
| mutation score |  |  | 🏷️ | ✓ |  |
| external links |  |  |  |  | ✓ |
<!-- standards:gates:end -->
end
