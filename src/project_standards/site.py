"""Verify a deployed documentation site (DOC-11): every page is served, and it is this build.

The deploy job writes ``build.json`` (``{"commit": "<sha>"}``) into the site before uploading it.
After deployment, this check reads ``sitemap.xml``, requests every page it lists, and compares the
served build marker with the commit that was built, so a stale cache or a half-published site
fails instead of passing silently.
"""

import json
import re
from collections.abc import Callable, Mapping
from http.client import HTTPConnection, HTTPSConnection
from typing import Protocol
from urllib.parse import urljoin, urlsplit

from project_standards._typed import mapping, text

_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
HTTP_OK = 200
TIMEOUT_SECONDS = 20.0


class SiteError(RuntimeError):
    """The site could not be fetched at all."""


class Connection(Protocol):
    """The part of ``http.client.HTTPConnection`` that :func:`fetch` uses."""

    def request(self, method: str, url: str, *, headers: Mapping[str, str]) -> None:
        """Send a request."""
        ...

    def getresponse(self) -> "Response":
        """Read the response."""
        ...

    def close(self) -> None:
        """Close the connection."""
        ...


class Response(Protocol):
    """The part of ``http.client.HTTPResponse`` that :func:`fetch` uses."""

    status: int

    def read(self) -> bytes:
        """The body."""
        ...


type ConnectionFactory = Callable[[str, int | None, float], Connection]
CONNECTIONS: Mapping[str, ConnectionFactory] = {
    "http": lambda host, port, timeout: HTTPConnection(host, port, timeout=timeout),
    "https": lambda host, port, timeout: HTTPSConnection(host, port, timeout=timeout),
}


def fetch(url: str, connections: Mapping[str, ConnectionFactory] = CONNECTIONS) -> tuple[int, str]:
    """GET ``url`` and return the status code and body.

    Redirects are not followed: a moved page is reported, not silently accepted.

    Raises:
        SiteError: the URL is not http(s), or the server cannot be reached.
    """
    parts = urlsplit(url)
    if parts.scheme not in connections or not parts.hostname:
        msg = f"{url}: only http(s) URLs are checked"
        raise SiteError(msg)
    connection = connections[parts.scheme](parts.hostname, parts.port, TIMEOUT_SECONDS)
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    try:
        connection.request("GET", target, headers={"Cache-Control": "no-cache"})
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8", errors="replace")
    except OSError as error:
        msg = f"{url}: {error}"
        raise SiteError(msg) from error
    finally:
        connection.close()


def pages(base: str, sitemap: str) -> list[str]:
    """Page URLs listed in a sitemap, made absolute against ``base``."""
    return [urljoin(base, loc) for loc in _LOC.findall(sitemap)]


def check(base: str, commit: str | None) -> list[str]:
    """Return every problem with the site deployed at ``base``."""
    base = base if base.endswith("/") else f"{base}/"
    status, sitemap = fetch(urljoin(base, "sitemap.xml"))
    if status != HTTP_OK:
        return [f"{base}sitemap.xml: HTTP {status} (is the site deployed, with site_url set?)"]
    urls = pages(base, sitemap)
    if not urls:
        return [f"{base}sitemap.xml lists no pages"]
    errors = [f"{url}: HTTP {code}" for url in urls if (code := fetch(url)[0]) != HTTP_OK]
    if commit is not None:
        status, body = fetch(urljoin(base, f"build.json?commit={commit}"))
        if status != HTTP_OK:
            return [*errors, f"{base}build.json: HTTP {status} (the deploy job writes it)"]
        served = text(mapping(json.loads(body), "build.json").get("commit"), "build.json commit")
        if served != commit:
            errors.append(
                f"{base} serves build {served[:10]}, expected {commit[:10]} "
                "(stale cache or failed deployment)"
            )
    return errors
