# python-project-standards — documentation

This repository has two halves that ship together:

- a **Copier template** that gives a Python project its binding standards (`docs/standards/`),
  hooks, CI/CD and strict tool configuration;
- the **`standards` CLI**, which turns those rules into checks that hooks and CI run.

The binding rules themselves live in
[`template/docs/standards/`](standards/README.md). This folder explains the
**features** that deliver and enforce them, one feature per page.

## Features

| # | Feature | What it gives you | Commands |
|---|---|---|---|
| 01 | [Getting started](01-getting-started.md) | A new repository in five minutes, fully protected | `copier copy` |
| 02 | [The template](02-template.md) | What is generated, what the project owns, what updates touch | `copier update` |
| 03 | [Commits and branches](03-commits-and-branches.md) | Conventional Commits and branch names, locally and in CI | `standards check-commit-msg`, `standards check-commits`, `standards check-pr-title`, `standards check-branch-name` |
| 04 | [Versioning and releases](04-versioning-and-releases.md) | SemVer from tags, automatic releases, immutable tags | `standards check-version` |
| 05 | [No silent suppressions](05-suppressions.md) | No coverage pragmas, no reasonless ignores | `standards check-suppressions` |
| 06 | [Doc impact](06-doc-impact.md) | Docs change together with what they describe | `standards check-doc-impact` |
| 07 | [Standards that match the tooling](07-standards-consistency.md) | Rules, hooks, CI and CLI cannot disagree | `standards check-standards`, `standards check-hook-parity` |
| 08 | [Badges and the gates table](08-badges-and-gates.md) | A README that shows what the gates measured | `standards readme`, `standards badge` |
| 09 | [Mutation testing](09-mutation-testing.md) | Proof that the tests catch bugs, not just run lines | `standards check-mutation-score` |
| 10 | [Template drift](10-template-drift.md) | Every project knows when it is behind | `standards check-template-drift` |
| 11 | [Git hooks](11-git-hooks.md) | Three stages, installed and checked | `standards check-hooks-installed` |
| 12 | [CI/CD workflows](12-ci-workflows.md) | Required checks, nightly and weekly gates, releases | — |
| 13 | [Standards feedback](13-standards-feedback.md) | How friction in a project becomes a better standard | — |
| 14 | [Configuration reference](14-configuration.md) | Every key of `standards.toml` | — |
| 15 | [Documentation deployment](15-docs-deployment.md) | Docs built strictly, deployed automatically, verified live | `standards check-site` |
| 16 | [Notebooks and scripts](16-notebooks-and-scripts.md) | Two levels of use beyond the reference, both kept runnable | `standards check-notebooks`, `standards check-scripts` |

## The idea in one paragraph

**Shift left.** Every rule has a gate; every gate runs at the earliest stage that can run it, on
the developer's machine before code leaves it, then again in CI, with only slow or external checks
left to nightly and weekly jobs. Nothing is enforced by goodwill alone, and nothing can drift:
the documents, the hooks, the workflows, the README badges and the CLI are cross-checked on every
push.
