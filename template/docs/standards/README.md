# Engineering Standards

These documents are **binding**. Every contributor, human or AI agent, follows them. A change that
breaks a rule is not merged.

Each rule has an ID (e.g. `COV-2`) so reviews and commit messages can cite it, and names **what
enforces it**. `review` means a human checks it, and the rule is in the PR checklist.

| # | Document | Covers |
|---|---|---|
| 01 | [Repository layout](01-repository-layout.md) | Where things live |
| 02 | [Commits, branches & versioning](02-commits-and-versioning.md) | Conventional Commits, SemVer from tags, automatic releases |
| 03 | [Code quality](03-code-quality.md) | Python conventions, typing, linting, dependency injection |
| 04 | [Architecture](04-architecture.md) | Layers, ports & adapters, import contracts |
| 05 | [Testing](05-testing.md) | Test types, 100 % coverage, mutation testing |
| 06 | [Documentation](06-documentation.md) | Docs that cannot go stale, docstrings, ADRs |
| 07 | [Security](07-security.md) | Generic application and supply-chain security |
| 08 | [Git hooks](08-git-hooks.md) | What runs at commit, commit-msg and pre-push |
| 09 | [CI/CD](09-ci-cd.md) | Workflows, required checks, releases |
| 10 | [Definition of Done](10-definition-of-done.md) | The checklist for every change |
| 11 | [Keeping standards current](11-keeping-standards-current.md) | How these rules evolve and reach every project |
| — | [Project-specific](project/README.md) | Rules that only apply to this project |

## Principles

0. **Shift left.** Every rule has a gate, and every gate runs at the **earliest** stage that can
   run it: in the editor and at commit, then at push, then in CI, with only the slow or external
   checks left to nightly and weekly jobs. Each README shows this as a generated table, next to
   badges that report what the gates measured.
1. **Machines enforce, humans judge.** Anything a tool can check is checked by a tool, locally
   *and* in CI.
2. **Local hooks are a convenience; CI is the authority.** Hooks can be skipped with
   `--no-verify`; CI cannot. CI reruns every hook stage.
3. **No silent exceptions.** Exclusions (coverage, lint, typing) are declared in configuration,
   with a reason, where review sees them. Inline exclusions are refused.
4. **The standards are code.** They are versioned, released, tested (`standards check-standards`)
   and pulled into projects like any other dependency ([11](11-keeping-standards-current.md)).
