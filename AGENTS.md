# Agent instructions

This repository **is** the standards: a Copier template (`template/`) and the `standards` CLI
(`src/project_standards/`) that enforces it. It follows its own rules
(`template/docs/standards/`).

- A change to a rule changes the document **and** its enforcement in the same PR.
- `uv run pytest --cov` must stay at 100 % line + branch coverage; `tests/test_template.py`
  renders the template and checks that the documents and the tooling agree.
- Commits: Conventional Commits with the scopes in `standards.toml`. Releases are tags made by CI.
