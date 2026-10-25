# 08 — Badges and the gates table

Rules: DOC-10, CI-10, CI-11, SEC-13.

## `standards readme [--write]`

Generates two blocks in `README.md`, between marker comments:

```text
<!-- standards:badges:start -->   …   <!-- standards:badges:end -->
<!-- standards:gates:start -->    …   <!-- standards:gates:end -->
```

Without `--write` it only checks. The `readme` pre-push hook runs it **with** `--write`: like a
formatter, it fixes the README and fails the push because files changed, so a stale README never
reaches GitHub, and CI (which reruns the hook) fails if one ever does. `[readme] repository = "owner/name"` in
`standards.toml` is required.

**Badges, in three rows, each one shown only when its source exists:**

| Row | Badges | Backed by |
|---|---|---|
| Status | CI, CodeQL, OpenSSF Scorecard, Nightly, docs | the workflows themselves |
| Measured | coverage, mutation, docstrings, release, Python, licence | the gates' own reports, GitHub releases, `pyproject.toml` |
| Built with | uv, Ruff, pyright strict, pre-commit, Conventional Commits, standards release, Copier | the configuration and `.copier-answers.yml` |

**The gates table** lists every hook (hooks from one external repo are grouped) and every
workflow job (except reruns, the release and the badge publication: `[readme] skip_jobs`). Each row shows the earliest
stages that run it: 💻 commit, 💻 push, ☁️ CI (🏷️ when only on a PR label), 🌙 nightly, 📅 weekly.

## `standards badge METRIC SOURCE --out FILE`

Writes a [shields.io endpoint](https://shields.io/badges/endpoint-badge) document from a gate's
report:

| Metric | Source |
|---|---|
| `coverage` | `coverage.xml` (lines + branches, combined as coverage.py does) |
| `docstrings` | interrogate output (`actual: N%`) |
| `mutation` | `mutants/mutmut-cicd-stats.json` |

Only a perfect score is bright green. A mutation run that evaluated nothing (a failing baseline) is shown as a red **"not measured"**, never as "no mutants yet". The `badges` job (coverage and docstrings, on every push to
`main`) and the nightly mutation job publish these files to an orphan **`badges`** branch, with
`.github/scripts/publish-badges.sh`. `main` and its history are never touched. The mutation badge
is published whether the gate passes or fails, because a badge that only shows good news is not
a measurement.

## OpenSSF Scorecard

`scorecard.yml` runs weekly, on every push to `main`, and when branch protection changes. It
publishes the results for the badge and uploads them to code scanning.
