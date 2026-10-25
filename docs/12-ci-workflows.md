# 12 — CI/CD workflows

Rules: CI-1…11, SEC-7…13.

| Workflow | Trigger | Jobs |
|---|---|---|
| `ci.yml` | PR, push to `main` | rerun of the pre-commit stage; rerun of the pre-push stage (coverage report uploaded); commits, PR title and branch (PRs only); gitleaks over the full history; pip-audit; on `main`: `badges`, `release`, `pages` (deploy, then verify the live site) |
| `codeql.yml` | PR, push to `main`, weekly | CodeQL for Python and for the workflows themselves |
| `scorecard.yml` | push to `main`, weekly, branch-protection changes | OpenSSF Scorecard |
| `nightly.yml` | nightly; PRs labelled `mutation` / `perf` | mutation score, performance budgets; a scheduled failure opens a `release-blocker` |
| `weekly.yml` | weekly | pip-audit, external links (lychee), template drift, deployed docs still served; a failure opens an issue |

**Conventions in every workflow:**

- every action is pinned by commit SHA (`zizmor` and `actionlint` check this before commit);
- `permissions: {}` at the top, then least privilege per job;
- `persist-credentials: false`, and pushes use the job token explicitly;
- untrusted values (PR title, branch name) reach shells only through environment variables;
- `UV_LOCKED=1`, so a stale lockfile fails the run.

The repository rulesets make every `ci.yml` job and CodeQL **required checks** on `main`, with no
bypass, and make release tags immutable.

**This repository's own CI** adds a `smoke` job: it renders the template from the PR, adds an
example notebook (executed) and an example script with its smoke test
(`.github/smoke/add_examples.py`), a project standards page outside the nav, then runs every hook
stage of the rendered project. A template change that breaks a fresh project fails the PR.
