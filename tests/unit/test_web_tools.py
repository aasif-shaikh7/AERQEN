"""Tests for the web tools (ADR-015).

The SSRF guard and the parsing are pure functions, tested without the network (IP-literal
URLs avoid DNS). Two live tests actually hit the internet and skip when it is unavailable.
"""

from __future__ import annotations

import pytest

from tools.registry import ToolRegistry
from tools.web import (
    _decode_ddg_href,
    _html_to_text,
    _parse_ddg_results,
    build_web_tools,
    is_public_url,
)


# ------------------------------------------------------------------- SSRF guard


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://10.0.0.5/admin",
        "http://192.168.1.1/",
        "http://172.16.0.1/",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata SSRF classic
        "http://localhost:8765/",
        "ftp://example.com/x",
        "file:///etc/passwd",
    ],
)
def test_ssrf_guard_blocks_private_and_nonhttp(url):
    ok, why = is_public_url(url)
    assert ok is False and why


@pytest.mark.parametrize("url", ["http://1.1.1.1/", "https://8.8.8.8/"])
def test_ssrf_guard_allows_public_ip(url):
    ok, _ = is_public_url(url)
    assert ok is True


# --------------------------------------------------------------------- parsing


def test_decode_ddg_href_extracts_real_url():
    href = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FEverest&rut=xyz"
    assert _decode_ddg_href(href) == "https://en.wikipedia.org/wiki/Everest"


def test_parse_ddg_results():
    html = (
        "<a rel='nofollow' href=\"//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa\" "
        "class='result-link'>First <b>Result</b></a>"
        "<a href=\"//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fb\" "
        "class='result-link'>Second</a>"
    )
    results = _parse_ddg_results(html, max_results=5)
    assert results == [
        {"title": "First Result", "url": "https://example.com/a"},
        {"title": "Second", "url": "https://example.com/b"},
    ]


def test_parse_ddg_results_respects_limit():
    html = "".join(
        f"<a href=\"//duckduckgo.com/l/?uddg=https%3A%2F%2Fe.com%2F{i}\" "
        f"class='result-link'>r{i}</a>"
        for i in range(10)
    )
    assert len(_parse_ddg_results(html, max_results=3)) == 3


def test_html_to_text_extracts_title_and_skips_script():
    html = "<html><head><title>Hello Page</title></head><body><p>Visible text</p>" \
           "<script>var x=1; alert('nope')</script><p>More text</p></body></html>"
    title, text = _html_to_text(html)
    assert title == "Hello Page"
    assert "Visible text" in text and "More text" in text
    assert "alert" not in text and "var x" not in text


# ----------------------------------------------------------------------- tools


def test_registers_search_low_and_fetch_medium():
    reg = ToolRegistry()
    build_web_tools(reg)
    assert reg.get("web.search").risk == "LOW"
    assert reg.get("web.fetch").risk == "MEDIUM"


def test_fetch_tool_refuses_private_url():
    from tools.registry import ToolError

    reg = ToolRegistry()
    build_web_tools(reg)
    with pytest.raises(ToolError):
        reg.get("web.fetch").run(url="http://127.0.0.1:8765/secret")


# -------------------------------------------------------------- live (network)


def _net_or_skip():
    import socket
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=3).close()
    except OSError:
        pytest.skip("no internet; skipping live web test")


@pytest.mark.live
def test_live_web_search_returns_results():
    _net_or_skip()
    reg = ToolRegistry()
    build_web_tools(reg)
    out = reg.get("web.search").run(query="python programming language", max_results=3)
    assert out["count"] >= 1
    assert all(r["url"].startswith("http") for r in out["results"])


@pytest.mark.live
def test_live_web_fetch_reads_a_page():
    _net_or_skip()
    reg = ToolRegistry()
    build_web_tools(reg)
    out = reg.get("web.fetch").run(url="https://example.com/")
    assert "example" in (out["title"] + out["text"]).lower()
