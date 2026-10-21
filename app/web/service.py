"""AgentService (ADR-013): runs agent tasks for the web UI, with web-based approvals.

This is the transport-free core the HTTP server sits on top of, so it can be tested
without opening a socket. Each chat message becomes a background task; the UI polls for
its state. When the agent hits a MEDIUM-risk step, :class:`WebApprover` pauses the task
until the UI sends an Allow/Deny decision -- the same human-in-the-loop gate as the CLI.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Callable, Optional

from core.agent.loop import AgentLoop
from core.task_manager.models import Task
from security.approvals.approver import Approver


class WebApprover(Approver):
    """Blocks the agent on a MEDIUM step until the UI resolves it (or it times out)."""

    def __init__(self, timeout: float = 300.0) -> None:
        self._event = threading.Event()
        self._decision = False
        self._timeout = timeout
        self.pending: Optional[dict[str, Any]] = None

    def approve(self, step) -> bool:
        self.pending = {
            "tool": step.tool,
            "risk": step.risk,
            "input": step.input,
            "expected": step.expected,
        }
        self._event.clear()
        got = self._event.wait(self._timeout)  # released by resolve()
        self.pending = None
        return bool(got and self._decision)

    def resolve(self, allow: bool) -> None:
        self._decision = bool(allow)
        self._event.set()


class _Session:
    def __init__(self, sid: str, message: str, approver: WebApprover) -> None:
        self.id = sid
        self.message = message
        self.approver = approver
        self.task: Optional[Task] = None
        self.error: Optional[str] = None
        self.finished = False


class AgentService:
    """Holds running chat sessions. ``build_agent(approver) -> AgentLoop`` is injected so
    tests can supply a fake-model agent."""

    def __init__(self, build_agent: Callable[[Approver], AgentLoop]) -> None:
        self._build = build_agent
        self._sessions: dict[str, _Session] = {}
        self._lock = threading.Lock()

    def start(self, message: str) -> str:
        message = (message or "").strip()
        sid = uuid.uuid4().hex[:8]
        sess = _Session(sid, message, WebApprover())
        with self._lock:
            self._sessions[sid] = sess
        threading.Thread(target=self._run, args=(sess,), daemon=True).start()
        return sid

    def _run(self, sess: _Session) -> None:
        try:
            agent = self._build(sess.approver)
            task = Task(task_id=f"web-{sess.id}", description=sess.message)
            agent.run(task)
            sess.task = task
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI, never crash
            sess.error = f"{type(exc).__name__}: {exc}"
        finally:
            sess.finished = True

    def poll(self, sid: str) -> dict[str, Any]:
        sess = self._sessions.get(sid)
        if sess is None:
            return {"state": "unknown"}
        if sess.error and sess.finished:
            return {"state": "failed", "error": sess.error}
        pending = sess.approver.pending
        if pending and not sess.finished:
            return {"state": "awaiting_approval", "pending": pending}
        if sess.finished and sess.task is not None:
            t = sess.task
            return {
                "state": t.state.value,
                "answer": t.answer,
                "error": t.error,
                "steps": [
                    {
                        "tool": s.tool,
                        "risk": s.risk,
                        "state": s.state.value,
                        "outcome": s.outcome,
                    }
                    for s in t.plan
                ],
            }
        return {"state": "running"}

    def approve(self, sid: str, allow: bool) -> bool:
        sess = self._sessions.get(sid)
        if sess is None:
            return False
        sess.approver.resolve(allow)
        return True
