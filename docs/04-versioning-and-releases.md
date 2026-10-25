# 04 — Versioning and releases

Rules: VER-1…5, CI-4, CI-6, CI-7.

## The tag is the version

`pyproject.toml` declares `dynamic = ["version"]`, and `hatch-vcs` reads the version from the
latest `vX.Y.Z` tag. The package exposes it as `__version__`, and the editable install refreshes
it when a tag moves (`[tool.uv] cache-keys`). There is no version string to forget, and no bump
commit on `main`.

## Releases

On every green push to `main`, the `release` job:

1. refuses to run while a `release-blocker` issue is open;
2. computes the next version with `cz bump --get-next`, from the Conventional Commits since the
   last tag (`fix`/`perf` → patch, `feat` → minor, breaking → major, minor while `0.y.z`);
3. pushes an annotated tag; builds the wheel and sdist; generates a CycloneDX SBOM; attests build
   provenance; creates the GitHub Release with generated notes;
4. asserts the result with `standards check-version --remote origin --released`.

## `standards check-version`

| Option | Checks |
|---|---|
| (none) | `pyproject.toml` has no static version and declares it dynamic |
| `--remote origin` | the latest tag reachable from `HEAD` is on `origin`, pointing to the same commit (a moved tag fails) |
| `--released` | no releasable commit since the latest tag is left untagged |

The `version-tag` pre-push hook runs it with `--remote origin`. Before the first release, when no
tag exists yet, it passes.

**Fix forward.** Tags are immutable (a ruleset forbids moving or deleting them). If a release job
fails after tagging, the fix is a new `fix` commit, which releases the next patch.
