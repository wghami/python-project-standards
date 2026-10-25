# 14 — Configuration reference (`standards.toml`)

Every key is optional; the defaults are shown. Wrong types fail with a message naming the key.

```toml
[commits]
types = ["feat", "fix", "perf", "refactor", "test", "docs", "build", "ci", "chore", "style", "revert"]
scopes = []                                   # rendered from the copier answer
scope_required_for = ["feat", "fix", "perf", "refactor"]
max_header_length = 72
releasing_types = ["feat", "fix", "perf"]     # plus any breaking change

[branches]
allowed = ["main"]
extra_prefixes = ["dependabot/"]

[readme]
repository = ""                               # "owner/name"; required by `standards readme`
template_repository = "wghami/python-project-standards"
badges_branch = "badges"
standards_docs = "docs/standards"             # where the pyright badge links to
skip_jobs = ["pre-commit-stage", "pre-push-stage", "release", "badges", "report"]

[doc_impact]
watched = []                                  # globs: changes here need documentation

[[doc_impact.rules]]                          # repeat for each mapping
paths = []                                    # globs of sources
docs = []                                     # globs of the documents that describe them
```

The other configuration a project carries:

| File | Configures |
|---|---|
| `pyproject.toml` | ruff, pyright, pytest, coverage, commitizen, mutmut, bandit |
| `.pre-commit-config.yaml` | the hooks of the three stages |
| `.importlinter` | the project's layers (owned by the project) |
| `mkdocs.yml` | the documentation site (strict) |
| `.copier-answers.yml` | the template release and the answers (managed by Copier) |
