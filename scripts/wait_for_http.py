#!/usr/bin/env python3
"""Poll an HTTP URL until status 200 or timeout."""

from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCHEMES = {"http": "http", "https": "https"}
"""Only plain HTTP(S) is pollable. Rejects file://, gopher://, ftp:// and the
other urllib-supported schemes that turn this readiness probe into an
arbitrary-resource fetcher."""

LOOPBACK_HOSTS = {"localhost": "localhost", "127.0.0.1": "127.0.0.1", "::1": "[::1]"}
"""Hosts this probe may reach, mapping the accepted spelling to the literal used
to rebuild the URL."""

_PATH_RE = re.compile(r"/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*")


def validate_url(raw: str) -> str:
    """Return a URL rebuilt from validated parts, or raise ``ValueError``.

    Every component of the returned URL comes from a literal in this module or
    from an ``int``, never from the caller's string: the scheme and host are
    *looked up* in the tables above rather than copied through, and the port is
    an integer. Only the path survives as text, and only after matching a strict
    pattern.

    That construction is the point, not decoration. This probe waits for a local
    service during CI and bring-up, so confining it to loopback keeps a
    caller-supplied string from reaching arbitrary hosts (SSRF) -- including the
    cloud metadata endpoint at 169.254.169.254 -- through this process. Building
    the result from the lookup values rather than from the input is what makes
    that guarantee hold for the string actually passed to urlopen.
    """
    parsed = urllib.parse.urlsplit(raw)
    scheme = SCHEMES.get(parsed.scheme)
    if scheme is None:
        raise ValueError(f"unsupported URL scheme {parsed.scheme!r}: expected http or https")
    if parsed.username or parsed.password:
        raise ValueError("URL must not embed credentials")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    host = LOOPBACK_HOSTS.get(parsed.hostname)
    if host is None:
        raise ValueError(
            f"host {parsed.hostname!r} is not loopback: this probe only waits on local services"
        )
    port = parsed.port  # urllib raises ValueError on a non-numeric or out-of-range port
    path = parsed.path or "/"
    if not _PATH_RE.fullmatch(path):
        raise ValueError(f"unsupported URL path {path!r}")
    netloc = f"{host}:{int(port)}" if port is not None else host
    return f"{scheme}://{netloc}{path}"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: wait_for_http.py <url> <timeout_seconds>", file=sys.stderr)
        return 2
    try:
        url = validate_url(argv[1])
    except ValueError as error:
        print(f"invalid url: {error}", file=sys.stderr)
        return 2
    try:
        timeout = float(argv[2])
    except ValueError:
        print("timeout_seconds must be a number", file=sys.stderr)
        return 2
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310 - scheme+host validated above
                if getattr(resp, "status", 200) == 200:
                    print(f"ready: {url}")
                    return 0
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    print(f"timeout waiting for {url}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
