# 15 — Documentation deployment

Rules: DOC-1…4, DOC-11.

Documentation is tested like code, before **and** after it is deployed.

| Stage | Check |
|---|---|
| 💻 push / ☁️ CI | `mkdocs build --strict` (the `docs-build` hook, deliberately **without** `--quiet`, which would hide the warnings `--strict` counts): any warning fails, including a broken internal link or anchor, or a page missing from the navigation. Project standards pages are exempt from the navigation (`not_in_nav`) and are linked from `standards/project/README.md` instead |
| 💻 push / ☁️ CI | every Python code block in the docs is executed (pytest-markdown-docs) |
| 💻 push / ☁️ CI | docstrings at 100 %; the API reference is generated from them at build time |
| ☁️ `main` | the `pages` job builds the site, writes `build.json` with the commit, deploys to GitHub Pages, then runs `standards check-site` against the **live** URL |
| 📅 weekly | external links (lychee), and `standards check-site` again: the site is still served |

## `standards check-site URL [--commit SHA]`

1. fetches `URL/sitemap.xml` (MkDocs writes it when `site_url` is set, which the template does);
2. requests every page listed, and reports any status other than 200;
3. with `--commit`, fetches `build.json` (bypassing caches) and fails unless it names that commit,
   which proves the site that is served is the one just built, not a stale CDN copy or a failed
   deployment.

Only `http(s)` URLs are fetched. In CI, the job retries for up to five minutes while the CDN picks
up the new site; a site that never becomes consistent fails the job, so `main` turns red.

**Setup:** in the repository settings, Pages → Source: "GitHub Actions" (or
`gh api -X POST repos/OWNER/NAME/pages -f build_type=workflow`).
