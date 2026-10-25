# 13 — Standards feedback

Rule: STD-7.

The standards improve from use. Every rendered project has `planning/standards-feedback.md`,
and its `AGENTS.md` tells AI coding agents to use it: when a generic rule is unclear, wrong, too
costly, produces a false positive, or is missing, the agent (or the developer) **records it instead
of working around it**.

```markdown
## 2026-11-02 — DOC-5: doc impact fires on generated lockfile changes

- **Context:** a Dependabot PR only touched uv.lock and pyproject.toml.
- **Problem:** every dependency bump needs a Docs-Reviewed footer.
- **Proposal:** map pyproject.toml dependency-only changes to the ADR rule, not to 03/05.
- **Status:** filed https://github.com/wghami/python-project-standards/issues/12
```

The loop:

1. Record the entry in the project, and tell the user.
2. File it as a **Standards feedback** issue on this repository (issue form provided), and record
   the URL in the entry.
3. Fix it upstream: document **and** enforcement in one PR. Merging releases a new version.
4. Each project's weekly drift check reports the release; `copier update` brings it in, and the
   entry is marked `resolved in vX.Y.Z`.
