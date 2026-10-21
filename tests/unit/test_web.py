"""Tests for the web chat service and server (ADR-013).

The model is faked, so these run without Ollama. They prove the two things that matter:
a task runs to an answer, and a MEDIUM step pauses for a web Allow/Deny decision.
"""

from __future__ import annotations

import json
import time
import urllib.request

import pytest

from app.web.server import PAGE, _Handler, _lan_ip
from app.web.service import AgentService
from core.agent.loop import AgentLoop
from core.executor.simple import SimpleExecutor
from core.runner import StepRunner
from core.verifier.checker import ContractVerifier
from integrations.ai.provider import LLMProvider, LLMReply, ToolCall
from security.approvals.approver import Approver
from security.audit.log import MemoryAuditLog
from security.policy.policy import PolicyEngine
from tools.files import build_file_tools
from tools.registry import ToolRegistry


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, replies):
        self._replies = list(replies)

    def chat(self, messages, tools):
        return self._replies.pop(0) if self._replies else LLMReply(content="done")


def _make_build(tmp_path, replies):
    """Return a build_agent(approver) -> AgentLoop using a fake model."""

    def build(approver: Approver) -> AgentLoop:
        registry = ToolRegistry()
        verifier = ContractVerifier()
        build_file_tools(registry, tmp_path, verifier=verifier)
        runner = StepRunner(registry, PolicyEngine(), SimpleExecutor(registry), verifier,
                            approver, MemoryAuditLog())
        return AgentLoop(FakeProvider(replies), runner, max_steps=6)

    return build


def _wait(service, sid, want, tries=50):
    for _ in range(tries):
        state = service.poll(sid)
        if state["state"] == want:
            return state
        time.sleep(0.02)
    return service.poll(sid)


# --------------------------------------------------------------------- service


def test_service_runs_read_only_task_to_answer(tmp_path):
    svc = AgentService(_make_build(tmp_path, [LLMReply(content="hello there")]))
    sid = svc.start("say hi")
    state = _wait(svc, sid, "done")
    assert state["state"] == "done"
    assert state["answer"] == "hello there"


def test_service_pauses_for_approval_then_allows(tmp_path):
    replies = [
        LLMReply(tool_calls=[ToolCall("files_write_text", {"path": "a.txt", "content": "hi"})]),
        LLMReply(content="done, wrote the file"),
    ]
    svc = AgentService(_make_build(tmp_path, replies))
    sid = svc.start("write a file")

    pending = _wait(svc, sid, "awaiting_approval")
    assert pending["state"] == "awaiting_approval"
    assert pending["pending"]["tool"] == "files.write_text"
    assert pending["pending"]["risk"] == "MEDIUM"

    assert svc.approve(sid, True) is True
    done = _wait(svc, sid, "done")
    assert done["state"] == "done"
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "hi"


def test_service_denied_approval_blocks(tmp_path):
    replies = [LLMReply(tool_calls=[ToolCall("files_write_text", {"path": "a.txt", "content": "x"})])]
    svc = AgentService(_make_build(tmp_path, replies))
    sid = svc.start("write a file")
    _wait(svc, sid, "awaiting_approval")
    svc.approve(sid, False)
    done = _wait(svc, sid, "blocked")
    assert done["state"] == "blocked"
    assert not (tmp_path / "a.txt").exists()


def test_unknown_session_polls_unknown(tmp_path):
    svc = AgentService(_make_build(tmp_path, []))
    assert svc.poll("nope")["state"] == "unknown"


# --------------------------------------------------------------------- server


def test_lan_ip_is_a_string():
    assert isinstance(_lan_ip(), str) and _lan_ip()


def test_page_is_self_contained_html():
    assert PAGE.startswith("<!doctype html>")
    assert "AERQEN" in PAGE


def test_http_round_trip_with_token(tmp_path):
    from http.server import ThreadingHTTPServer
    import threading

    svc = AgentService(_make_build(tmp_path, [LLMReply(content="pong")]))
    _Handler.service = svc
    _Handler.token = "secret123"
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"

    def post(path, body, token="secret123"):
        req = urllib.request.Request(
            base + path, data=json.dumps(body).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-AERQEN-Token": token},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())

    try:
        # Wrong token is refused.
        try:
            post("/api/ask", {"message": "hi"}, token="wrong")
            assert False, "expected 403"
        except urllib.error.HTTPError as e:
            assert e.code == 403

        # Correct token: ask -> poll to done.
        status, body = post("/api/ask", {"message": "ping"})
        assert status == 200 and "task_id" in body
        sid = body["task_id"]

        answer = None
        for _ in range(50):
            req = urllib.request.Request(base + f"/api/poll?task_id={sid}",
                                         headers={"X-AERQEN-Token": "secret123"})
            with urllib.request.urlopen(req, timeout=5) as r:
                s = json.loads(r.read())
            if s["state"] == "done":
                answer = s["answer"]
                break
            time.sleep(0.02)
        assert answer == "pong"
    finally:
        httpd.shutdown()
        httpd.server_close()
