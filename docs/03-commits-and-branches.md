# 03 — Commits and branches

Rules: COM-1…6, BR-1…4 in `02-commits-and-versioning.md`.

## Commit messages

`standards check-commit-msg FILE` validates one message. The `commit-msg` hook calls it on every
commit. It checks:

- the header is `<type>(<scope>)!: <summary>`, with a type and scope from `standards.toml`;
- a scope is present for `feat`, `fix`, `perf` and `refactor` (configurable);
- the summary is lower case, has no trailing period, and the header is ≤ 72 characters;
- a blank line separates the header from the body;
- `!` comes with a `BREAKING CHANGE:` footer.

A PR title is checked as a header only: a breaking title (`feat(api)!: …`) needs no footer
there, because the squash body carries the commits' `BREAKING CHANGE:` footers (BR-4), and each
commit is checked for it.

`Merge …` and `Revert "…"` messages pass. `fixup!` and `squash!` are accepted locally, so that
`git commit --fixup` works, but refused in CI.

```bash
uv run standards check-commits --range origin/main..HEAD   # every commit of a branch
uv run standards check-pr-title "feat(api): add simulations"   # the future squash header
```

Every failure explains the rule and how to fix it, for example:

```text
✗ type 'feat' requires a scope: core, api, docs
```

## Branch names

`standards check-branch-name` runs as a pre-push hook. In CI it checks the PR head (`--name`).
Accepted names:

- `main`, and a detached `HEAD` (as in CI);
- `<type>/<topic>`, with a listed type and a lower-case topic (`feat/rule-compiler`,
  `fix/dst-gap`);
- the prefixes in `[branches] extra_prefixes` (default `dependabot/`).
