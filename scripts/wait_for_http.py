#!/usr/bin/env python3
"""Poll an HTTP URL until status 200 or timeout."""

from __future__ import annotations

import ipaddress
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_SCHEMES = frozenset({"http", "https"})
"""Only plain HTTP(S) is pollable. Rejects file://, gopher://, ftp:// and the
other urllib-supported schemes that turn this readiness probe into an
arbitrary-resource fetcher."""


def validate_url(raw: str) -> str:
    """Return a URL rebuilt from validated parts, or raise ``ValueError``.

    This probe waits for a *local* service to come up during CI and local
    bring-up, so the target is confined to loopback. That keeps a caller-supplied
    string from being used to reach arbitrary hosts (SSRF) through this process.
    """
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"unsupported URL scheme {parsed.scheme!r}: expected http or https")
    if parsed.username or parsed.password:
        raise ValueError("URL must not embed credentials")
    host = parsed.hostname
    if not host:
        raise ValueError("URL must include a host")
    if not _is_loopback(host):
        raise ValueError(f"host {host!r} is not loopback: this probe only waits on local services")
    port = parsed.port  # urllib raises ValueError on a non-numeric or out-of-range port
    scheme = "https" if parsed.scheme == "https" else "http"
    netloc = f"{host}:{port}" if port is not None else host
    return urllib.parse.urlunsplit((scheme, netloc, parsed.path, parsed.query, ""))


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


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
