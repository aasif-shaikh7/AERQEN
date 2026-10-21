"""Web tools (ADR-015): let the agent read from the internet, carefully.

Standard library only (urllib). Two tools:

    web.search  LOW     search the web (DuckDuckGo) -> a list of {title, url}
    web.fetch   MEDIUM  download ONE page and return its text (approval required)

Safety:
- ``web.fetch`` is guarded against SSRF: the URL must be http/https and must resolve to a
  PUBLIC address. localhost, 127.0.0.0/8, 10/8, 172.16/12, 192.168/16, link-local, etc. are
  refused, so the agent cannot be steered into poking the owner's own machine or LAN.
- Downloads are size-capped and HTML is reduced to plain text, then length-capped, so a huge
  or hostile page cannot flood the model.
- Results are returned as data and (like every tool result) re-enter the prompt clearly
  labelled UNTRUSTED, so a web page can never issue instructions to the agent.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Callable

from tools.registry import Tool, ToolError

_DDG_LITE = "https://lite.duckduckgo.com/lite/"
_UA = "Mozilla/5.0 (AERQEN; local research agent)"
_MAX_DOWNLOAD = 2_000_000  # bytes read from a response, hard cap
MAX_FETCH_CHARS = 8000  # characters of page text returned to the model

_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "What to search the web for."},
        "max_results": {"type": "integer", "description": "How many results (default 5)."},
    },
    "required": ["query"],
}
_FETCH_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "Public http(s) page to download and read."}
    },
    "required": ["url"],
}


# ------------------------------------------------------------------ HTTP + parsing


def _http_get(url: str, timeout: float) -> tuple[str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - guarded by caller
        return resp.headers.get_content_type(), resp.read(_MAX_DOWNLOAD)


def _decode_ddg_href(href: str) -> str | None:
    """DuckDuckGo wraps results in a redirect; pull out the real URL (the ``uddg`` param)."""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    uddg = urllib.parse.parse_qs(parsed.query).get("uddg")
    if uddg:
        return uddg[0]
    return href if parsed.scheme in ("http", "https") else None


_RESULT_RE = re.compile(r"""<a[^>]*href="([^"]+)"[^>]*class='result-link'[^>]*>(.*?)</a>""", re.S)


def _parse_ddg_results(html: str, max_results: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for m in _RESULT_RE.finditer(html):
        url = _decode_ddg_href(m.group(1))
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if url:
            out.append({"title": title, "url": url})
        if len(out) >= max_results:
            break
    return out


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._title: list[str] = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self._title.append(data)
        else:
            t = data.strip()
            if t:
                self.parts.append(t)


def _html_to_text(html: str) -> tuple[str, str]:
    p = _TextExtractor()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001 - malformed HTML must not crash a fetch
        pass
    title = " ".join("".join(p._title).split())
    return title, "\n".join(p.parts)


def is_public_url(url: str) -> tuple[bool, str]:
    """SSRF guard: allow only http/https URLs that resolve to a public address."""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        return False, "only http/https URLs are allowed"
    host = p.hostname
    if not host:
        return False, "URL has no host"
    if host.lower() == "localhost":
        return False, "localhost is blocked"
    try:
        port = p.port or (443 if p.scheme == "https" else 80)
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        return False, f"cannot resolve host: {exc}"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False, f"blocked non-public address {ip}"
    return True, ""


# ----------------------------------------------------------------------- tools


def _make_search(timeout: float) -> Callable[..., dict[str, Any]]:
    def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
        q = (query or "").strip()
        if not q:
            raise ToolError("empty search query")
        max_results = max(1, min(int(max_results), 10))
        url = _DDG_LITE + "?" + urllib.parse.urlencode({"q": q})
        try:
            _, raw = _http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"web search failed: {exc}")
        results = _parse_ddg_results(raw.decode("utf-8", "replace"), max_results)
        return {"query": q, "count": len(results), "results": results}

    return web_search


def _make_fetch(timeout: float) -> Callable[..., dict[str, Any]]:
    def web_fetch(url: str) -> dict[str, Any]:
        ok, why = is_public_url(url)
        if not ok:
            raise ToolError(f"refused to fetch {url!r}: {why}")
        try:
            ctype, raw = _http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"fetch failed: {exc}")
        body = raw.decode("utf-8", "replace")
        if "html" in ctype:
            title, text = _html_to_text(body)
        else:
            title, text = "", body
        return {
            "url": url,
            "title": title,
            "content_type": ctype,
            "text": text[:MAX_FETCH_CHARS],
            "truncated": len(text) > MAX_FETCH_CHARS,
        }

    return web_fetch


# ---------------------------------------------------------------- verifier contracts


def _verify_search(step) -> str:
    result = step.result or {}
    if "results" in result:
        return f"Measured: {result.get('count', 0)} web result(s)."
    return "FAILED: web.search returned no results field."


def _verify_fetch(step) -> str:
    result = step.result or {}
    if "text" in result:
        note = " (truncated)" if result.get("truncated") else ""
        return f"Measured: fetched {len(result.get('text', ''))} chars{note}."
    return "FAILED: web.fetch returned no text."


def build_web_tools(registry, timeout: float = 15.0, verifier=None) -> None:
    """Register the web tools (and verifier contracts) into the registry."""
    registry.register(
        Tool(
            name="web.search",
            risk="LOW",
            description="Search the web and get a list of result titles and URLs. Read-only.",
            func=_make_search(timeout),
            input_schema=_SEARCH_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="web.fetch",
            risk="MEDIUM",
            description=(
                "Download ONE public web page and return its text. Needs approval (MEDIUM). "
                "Private/local addresses are refused."
            ),
            func=_make_fetch(timeout),
            input_schema=_FETCH_SCHEMA,
        )
    )
    if verifier is not None:
        verifier.register("web.search", _verify_search)
        verifier.register("web.fetch", _verify_fetch)
