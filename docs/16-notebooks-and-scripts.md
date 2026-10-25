# 16 — Notebooks and scripts

Rules: LAY-8, DOC-12, DOC-13, TST-14, TST-15.

Users meet a project at three levels, and each is published on the documentation site:

| Level | Folder | Purpose | Kept honest by |
|---|---|---|---|
| 1. Understand | `notebooks/` | One concept per notebook: what happens under the hood, with real outputs | `standards check-notebooks`, then nbmake re-runs every notebook |
| 2. Apply | `scripts/` | Complete applications for specific or advanced uses | `standards check-scripts`, and a smoke test per script in the 100 % coverage run |
| 3. Integrate | `docs/reference.md` | The Python API, generated from docstrings | docstrings at 100 %, strict docs build |

## Notebooks

`standards check-notebooks [--dir notebooks]` checks, without running anything:

- names are `NN-concept.ipynb`, numbered from `01` without gaps or duplicates;
- the first cell is markdown `# NN — <concept>` with **Concept:** and **You will learn:**, and
  the last cell is markdown with **Next:**;
- every code cell ran exactly once, top to bottom (execution counts 1, 2, 3, …), with no error
  output and no empty cell. This proves the committed outputs come from a clean run;
- no import of a private name (`pkg._x`, `from pkg.mod import _y`) of the package under `src/`;
- `notebooks/README.md` links every notebook.

Then the `notebooks` pre-push hook (and CI) **executes** every notebook with nbmake, so a
notebook that breaks because the code changed fails the push. To refresh one after a change:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01-time-grid.ipynb
```

Notebooks are committed with their outputs, so GitHub and the documentation site (mkdocs-jupyter,
`execute: false`) show results without running anything. Ruff lints them, with a few notebook
exemptions declared in `pyproject.toml`.

## Scripts

`standards check-scripts` checks every `scripts/<name>.py`:

- a module docstring (what it does, for whom);
- `def main(argv: Sequence[str] | None = None) -> int`;
- `if __name__ == "__main__": raise SystemExit(main())`;
- a smoke test `tests/scripts/test_<name>.py`;
- a mention of `` `scripts/<name>.py` `` in `scripts/README.md`.

The smoke test calls `main([...])` on small inputs, and runs the module as `__main__` (for
example with `runpy.run_module`), so the scripts are part of the 100 % line and branch coverage
like any other code.

## Repository tooling moved to `tools/`

Code that only hooks and CI call lives in `tools/` (LAY-5). `scripts/` now belongs to users.
