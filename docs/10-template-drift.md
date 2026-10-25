# 10 — Template drift

Rule: STD-2.

`standards check-template-drift [--answers .copier-answers.yml]` reads the template release the
project was rendered from (`_commit`), lists the release tags of the template (`_src_path`, with
`gh:owner/repo` expanded), and fails when a newer `vX.Y.Z` exists:

```text
✗ standards template v0.3.0 is available (this project uses v0.2.0); run `copier update`
```

Only tags of the exact form `refs/tags/vX.Y.Z` count; `release/v9.0.0` or `latest` do not. A
project rendered from an untagged commit is told to update from a release.

The `weekly.yml` workflow runs it, and opens an issue when the project is behind. The update
itself is a normal PR: `build(standards): update the template to vX.Y.Z`.
