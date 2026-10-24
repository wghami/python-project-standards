# python-project-standards

Binding engineering standards for Python projects, **and the tooling that enforces them**:

- **`template/`**: a [Copier](https://copier.readthedocs.io) template containing the standards
  documents (`docs/standards/`), pre-commit hooks, GitHub Actions (CI with a 100 % coverage gate,
  automatic SemVer releases from Conventional Commits, CodeQL, nightly mutation testing, weekly
  drift and audit), and strict ruff / pyright / pytest configuration.
- **`standards`**: a CLI (this package) that turns the rules into checks: commit messages, branch
  names, suppressions, doc impact, version ↔ tag, hook ↔ CI parity, consistency of the standards
  documents, mutation score, template drift and installed hooks.

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
