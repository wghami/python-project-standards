# 01 — Getting started

**Prerequisites:** `git`, [`uv`](https://docs.astral.sh/uv/), and for the GitHub side the `gh`
CLI, signed in.

## 1. Render the project

```bash
uvx copier copy --trust gh:wghami/python-project-standards my-project
```

Copier asks for the project name, package name, description, author, GitHub owner, Python
version, the allowed commit scopes, and the minimum mutation score. `--trust` lets it run three
post-render tasks: `git init`, `uv lock`, and `pre-commit install`.

## 2. First commit

```bash
cd my-project
git add -A
git commit -m "feat(core): bootstrap from python-project-standards"
```

The commit runs the pre-commit and commit-msg hooks. A `feat` commit makes the first release
`v0.1.0` once CI is green.

## 3. Create the repository and protect it

```bash
gh repo create OWNER/NAME --public --source . --remote origin
gh api -X POST repos/OWNER/NAME/pages -f build_type=workflow
git push -u origin main
```

Then add, in the repository settings or through the API:

- **Squash merging only**, with the PR title as the commit title and the **commit messages** as
  the body (BR-4: footers such as `BREAKING CHANGE:` must survive the merge).
- A **ruleset on `main`**: PR required, required status checks (every `ci.yml` job and CodeQL),
  linear history, no force push or deletion, no bypass.
- A **ruleset on `refs/tags/v*`**: no update or deletion, so release tags are immutable (CI-6).
- **Labels:** `release-blocker`, `maintenance`, `mutation`, `perf`.
- Secret scanning with push protection, Dependabot alerts, private vulnerability reporting.

## 4. Work

```bash
git switch -c feat/first-feature
# … edit, commit (hooks run) …
git push -u origin feat/first-feature   # pre-push hooks: tests at 100 %, docs, contracts …
gh pr create --fill
```

Merging a PR with a releasable commit (`feat`, `fix`, `perf`, or a breaking change) releases a
new version automatically.
