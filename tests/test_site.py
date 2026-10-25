"""The deployed docs site is verified page by page, and as the right build (DOC-11).

These tests serve a directory on localhost; they are the only ones allowed to open sockets.
"""

import json
import threading
from collections.abc import Iterator, Mapping
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from project_standards import site
from project_standards.cli import main

pytestmark = pytest.mark.enable_socket


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002  # stdlib signature
        del format, args


@pytest.fixture
def served(tmp_path: Path) -> Iterator[tuple[Path, str]]:
    root = tmp_path / "site"
    root.mkdir()
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Quiet, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield root, f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


def _publish(root: Path, base: str, commit: str = "a" * 40, *, missing: str = "") -> None:
    (root / "index.html").write_text("home")
    (root / "guide").mkdir()
    (root / "guide" / "index.html").write_text("guide")
    locs = "".join(f"<url><loc>{base}{p}</loc></url>" for p in ("", "guide/", missing) if p != "-")
    (root / "sitemap.xml").write_text(f"<urlset>{locs}</urlset>")
    (root / "build.json").write_text(json.dumps({"commit": commit}))


def test_a_complete_site_of_this_build_passes(served: tuple[Path, str]) -> None:
    root, base = served
    _publish(root, base, missing="-")
    assert site.check(base, "a" * 40) == []
    assert site.check(base.rstrip("/"), None) == []


def test_missing_pages_and_stale_builds_are_reported(served: tuple[Path, str]) -> None:
    root, base = served
    _publish(root, base, commit="b" * 40, missing="gone/")
    assert site.check(base, "a" * 40) == [
        f"{base}gone/: HTTP 404",
        f"{base} serves build bbbbbbbbbb, expected aaaaaaaaaa (stale cache or failed deployment)",
    ]


def test_missing_sitemap_marker_or_pages(served: tuple[Path, str]) -> None:
    root, base = served
    assert site.check(base, None) == [
        f"{base}sitemap.xml: HTTP 404 (is the site deployed, with site_url set?)"
    ]
    (root / "sitemap.xml").write_text("<urlset></urlset>")
    assert site.check(base, None) == [f"{base}sitemap.xml lists no pages"]
    _publish(root, base, missing="-")
    (root / "build.json").unlink()
    assert site.check(base, "a" * 40) == [f"{base}build.json: HTTP 404 (the deploy job writes it)"]


def test_relative_sitemap_entries_are_resolved() -> None:
    assert site.pages("https://x.io/docs/", "<loc>a/</loc><loc> https://y.io/b </loc>") == [
        "https://x.io/docs/a/",
        "https://y.io/b",
    ]


@pytest.mark.parametrize("url", ["file:///etc/passwd", "https:///no-host"])
def test_only_http_urls_with_a_host_are_fetched(url: str) -> None:
    with pytest.raises(site.SiteError) as error:
        site.fetch(url)
    assert str(error.value) == f"{url}: only http(s) URLs are checked"


class _Fake:
    """A connection that records what it was asked, to check the request without a network."""

    status = 200
    used: list[str] = []  # noqa: RUF012  # shared on purpose: the factory creates instances

    def __init__(self, host: str, port: int | None, timeout: float) -> None:
        self.used.append(f"{host}:{port}:{timeout}")

    def request(self, method: str, url: str, *, headers: Mapping[str, str]) -> None:
        self.used.append(f"{method} {url} {dict(headers)}")

    def getresponse(self) -> "_Fake":
        return self

    def read(self) -> bytes:
        return b"ok"

    def close(self) -> None:
        self.used.append("closed")


def test_each_scheme_uses_its_own_connection() -> None:
    _Fake.used.clear()
    assert site.fetch("https://docs.example/a/?v=1", {"https": _Fake}) == (200, "ok")
    assert _Fake.used == [
        f"docs.example:None:{site.TIMEOUT_SECONDS}",
        "GET /a/?v=1 {'Cache-Control': 'no-cache'}",
        "closed",
    ]
    with pytest.raises(site.SiteError):
        site.fetch("http://docs.example/", {"https": _Fake})


def test_the_default_connections_cover_http_and_https() -> None:
    assert sorted(site.CONNECTIONS) == ["http", "https"]
    connection = site.CONNECTIONS["https"]("docs.example", None, 1.0)
    assert type(connection).__name__ == "HTTPSConnection"
    connection.close()


def test_redirects_are_reported_not_followed(served: tuple[Path, str]) -> None:
    root, base = served
    (root / "guide").mkdir()
    assert site.fetch(f"{base}guide")[0] == 301


def test_unreachable_server_is_an_error(
    served: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    _, base = served
    dead = "http://127.0.0.1:9/"
    with pytest.raises(site.SiteError, match=r"^http://127\.0\.0\.1:9/sitemap\.xml: "):
        site.check(dead, None)
    assert main(["check-site", dead]) == 1
    assert capsys.readouterr().err.startswith("✗ http://127.0.0.1:9/sitemap.xml: ")
    assert base


def test_cli_passes_the_commit(
    served: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    root, base = served
    _publish(root, base, missing="-")
    assert main(["check-site", base, "--commit", "a" * 40]) == 0
    assert main(["check-site", base, "--commit", "c" * 40]) == 1
    assert "expected cccccccccc" in capsys.readouterr().err
