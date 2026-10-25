# 11 — Git hooks

Rules: HK-1…5. The full list of hooks is in `08-git-hooks.md` of the standards.

| Stage | Runs | Typical time |
|---|---|---|
| `pre-commit` | format, lint, strict types on changed files, suppressions, lockfile, workflow lint and security, secrets, file hygiene | seconds |
| `commit-msg` | Conventional Commit | instant |
| `pre-push` | branch name, strict types everywhere, import contracts, all tests at 100 % coverage, docstrings, bandit, strict docs build, doc impact, version/tag, standards consistency, README blocks, hook parity | tens of seconds |

Install them once per clone with `uv run pre-commit install`. The template's `default_install_hook_types`
installs all three stages.

`standards check-hooks-installed` fails when one of the three hooks is missing or is not managed
by pre-commit. A test in `tests/arch/` calls it, so a developer who forgot to install the hooks
finds out from the test suite. The test is skipped in CI, which runs every stage itself.

Every hook calls its tool through `uv run --frozen`, so the versions are those of `uv.lock`, the
same ones CI uses.
