# 02 — The template

`copier.yml` defines the questions; `template/` is what gets rendered. Files ending in `.jinja`
are rendered, everything else is copied as is. The template uses `[[ … ]]` and `[% … %]` as Jinja
delimiters, so GitHub Actions expressions (`${{ … }}`) pass through untouched.

## Who owns what

| Owned by the **template** (updated by `copier update`) | Owned by the **project** (rendered once, never touched again) |
|---|---|
| `docs/standards/*.md` (the generic rules) | `docs/standards/project/` (project rules) |
| `.pre-commit-config.yaml`, `.github/` (workflows, scripts, PR template) | `README.md` (but its badge and gates blocks are generated, see [08](08-badges-and-gates.md)) |
| `pyproject.toml` tool configuration, `standards.toml`, `mkdocs.yml` | `src/`, `tests/`, `scripts/` |
| `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `LICENSE` | `planning/SPEC.md`, `planning/ROADMAP.md`, ADR 0001, `planning/standards-feedback.md` |
| | `.importlinter` (the project's own layers) |

Template-owned files can still be edited by a project. `copier update` merges both sides with a
3-way merge, and shows a real conflict when both sides changed the same lines. Generic **rules**,
however, are changed only upstream (STD-1).

## Updating

```bash
uvx copier update --trust                 # to the latest release
uvx copier update --trust --vcs-ref v0.2.0  # to a given release
```

Do it on a `build/standards-vX.Y.Z` branch, then open a PR. The answers and the template release
are recorded in `.copier-answers.yml`. `pyproject.toml` pins the `standards` CLI to the **same
commit** as the template, so documents and checks always come from one release.
