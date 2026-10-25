# 07 — Standards that match the tooling

Rules: DOC-6, STD-3, HK-5.

## `standards check-standards`

Reads every Markdown file under `--docs` (default `docs/standards`) and the hook configuration
(`--config`, default `.pre-commit-config.yaml`). It fails when:

- a rule ID (a table row whose first cell looks like `COV-2` or `MEO-SEC-1`) is defined twice;
- a rule row has an empty cell (every rule names what enforces it);
- a hook in the configuration is not mentioned (as `` `hook-id` ``) in the standards;
- the standards cite a `standards <command>` that does not exist, or a command exists that the
  standards never cite.

So a new hook, a new command or a new rule cannot land without its documentation, and a
documented check cannot silently disappear.

## `standards check-hook-parity`

Reads the hook configuration and `.github/workflows/ci.yml` (`--config`, `--workflow`). Every
stage used locally must be rerun by CI:

- `pre-commit` and `pre-push` → a `pre-commit run --all-files --hook-stage <stage>` step;
- `commit-msg` → a `standards check-commits` step.

Skipping hooks with `--no-verify` therefore saves nothing: CI runs the same hooks.
