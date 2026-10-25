# 05 — No silent suppressions

Rules: COV-2, TYP-1, TYP-3, LNT-4, SEC-4.

`standards check-suppressions [PATHS…]` scans Python files (by default every tracked `*.py` and
`*.pyi`) and refuses:

| Pattern | Why |
|---|---|
| `pragma: no cover` / `no branch`, in any case | uncovered code is deleted or redesigned, never excluded |
| file-level `ruff: noqa` / `flake8: noqa` | a whole file escaping lint is never justified |
| `noqa` without codes, or codes without a reason | write `noqa: S603  # fixed binary, no shell` |
| `type: ignore` / `pyright: ignore` without a rule, or without a reason | write `pyright: ignore[rule]  # why` |
| `nosec` | security suppressions go through ruff `S` rules, with a reason |
| `pyright: basic` | strict typing cannot be lowered per file |

The only coverage exclusions are the patterns listed in `pyproject.toml` (`if TYPE_CHECKING:`,
`@overload`, `...` bodies, `assert_never(`). Changing that list needs an ADR.
