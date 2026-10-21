"""Negative/security tests for the Phase 2 foundation (SECURITY.md §8).

Covers: registry-authoritative risk (ADR-009), unknown tools, input schemas, the
approval gate (FEAT-6), and the audit log (FEAT-11) including fail-closed behaviour.
"""

from __future__ import annotations

import json

import pytest

from app.entrypoint.cli import build_pipeline
from core.brain.interface import Brain
from core.executor.simple import SimpleExecutor
from core.pipeline import Pipeline
from core.planner.interface import Planner
from core.task_manager.models import Step, StepDecision, StepState, Task, TaskState
from core.verifier.checker import ContractVerifier
from security.approvals.approver import Approver, CliApprover, DenyAllApprover
from security.audit.log import (
    REDACTED,
    AuditLog,
    JsonlAuditLog,
    MemoryAuditLog,
    sanitize,
)
from security.policy.policy import PolicyEngine
from tools.registry import Tool, ToolInputError, ToolRegistry, max_risk


# ----------------------------------------------------------------- test doubles


class _AnyBrain(Brain):
    def understand(self, task: Task) -> None:
        task.intent = {"action": "scripted"}
        task.state = TaskState.PLANNED


class _ScriptedPlanner(Planner):
    """Plans exactly the steps it is given -- stands in for a future (untrusted) LLM."""

    def __init__(self, steps: list[Step]) -> None:
        self._steps = steps

    def plan(self, task: Task) -> Task:
        task.state = TaskState.PLANNED
        task.plan = self._steps
        return task


class _RecordingApprover(Approver):
    def __init__(self, answer: bool) -> None:
        self.answer = answer
        self.asked: list[str] = []

    def approve(self, step: Step) -> bool:
        self.asked.append(step.tool)
        return self.answer


class _Counter:
    """A tool function that counts how often it really ran."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, message: str) -> dict:
        self.calls += 1
        return {"echo": message, "verified": True}


_SCHEMA = {
    "type": "object",
    "properties": {"message": {"type": "string"}},
    "required": ["message"],
}


def _registry(counter: _Counter, risk: str = "MEDIUM", name: str = "demo.echo_guarded"):
    registry = ToolRegistry()
    registry.register(Tool(name=name, risk=risk, description="t", func=counter, input_schema=_SCHEMA))
    return registry


def _step(tool="demo.echo_guarded", risk="LOW", message="hi", input_=None) -> Step:
    return Step(
        step_id=1,
        tool=tool,
        input=input_ if input_ is not None else {"message": message},
        risk=risk,
        expected="echo",
    )


def _pipeline(registry, steps, approver=None, audit=None) -> Pipeline:
    return Pipeline(
        brain=_AnyBrain(),
        planner=_ScriptedPlanner(steps),
        policy=PolicyEngine(),
        executor=SimpleExecutor(registry),
        verifier=ContractVerifier(),
        registry=registry,
        approver=approver,
        audit=audit,
    )


# ------------------------------------------------- risk comes from the registry


def test_planner_cannot_lower_tool_risk():
    """A planner (later: an LLM) claiming LOW for a MEDIUM tool must still need approval."""
    counter = _Counter()
    approver = _RecordingApprover(answer=False)
    task = Task(task_id="r1", description="x")
    _pipeline(_registry(counter), [_step(risk="LOW")], approver=approver).run(task)

    step = task.plan[0]
    assert step.risk == "MEDIUM"
    assert step.decision is StepDecision.CONFIRM
    assert "raised" in (step.policy_reason or "")
    assert approver.asked == ["demo.echo_guarded"]
    assert task.state is TaskState.BLOCKED
    assert counter.calls == 0


def test_unknown_tool_is_blocked_and_never_runs():
    counter = _Counter()
    task = Task(task_id="r2", description="x")
    _pipeline(_registry(counter), [_step(tool="shell.run", risk="LOW")]).run(task)
    assert task.state is TaskState.BLOCKED
    assert "not in the registry" in task.error
    assert counter.calls == 0


def test_unrecognised_risk_label_is_blocked():
    counter = _Counter()
    task = Task(task_id="r3", description="x")
    _pipeline(_registry(counter, risk="LOW"), [_step(risk="TINY")]).run(task)
    assert task.state is TaskState.BLOCKED
    assert counter.calls == 0


def test_max_risk_and_tool_risk_validation():
    assert max_risk("low", "MEDIUM") == "MEDIUM"
    assert max_risk("HIGH", "LOW") == "HIGH"
    assert max_risk("LOW", "nonsense") is None
    with pytest.raises(ValueError):
        Tool(name="bad", risk="SOMEWHAT", description="", func=lambda: {})


# ------------------------------------------------------------- input schemas


@pytest.mark.parametrize(
    "bad_input, fragment",
    [
        ({}, "missing required"),
        ({"message": 5}, "must be string"),
        ({"message": "hi", "path": "C:/Windows"}, "unknown parameter"),
    ],
)
def test_invalid_input_never_reaches_tool_or_approver(bad_input, fragment):
    counter = _Counter()
    approver = _RecordingApprover(answer=True)
    task = Task(task_id="s1", description="x")
    _pipeline(_registry(counter), [_step(input_=bad_input)], approver=approver).run(task)

    assert task.state is TaskState.FAILED
    assert fragment in task.error
    assert approver.asked == []  # human is not bothered with a broken step
    assert counter.calls == 0


def test_tool_run_validates_even_when_called_directly():
    counter = _Counter()
    tool = _registry(counter, risk="LOW").get("demo.echo_guarded")
    with pytest.raises(ToolInputError):
        tool.run(message=["not", "a", "string"])
    assert counter.calls == 0


def test_bad_schema_is_rejected_at_registration():
    with pytest.raises(ValueError):
        Tool(name="t", risk="LOW", description="", func=lambda: {},
             input_schema={"type": "object", "properties": {}, "required": ["x"]})


# ------------------------------------------------------------- approval gate


def test_approved_step_runs_and_is_verified():
    counter = _Counter()
    task = Task(task_id="a1", description="x")
    _pipeline(_registry(counter), [_step()], approver=_RecordingApprover(True)).run(task)
    assert task.state is TaskState.DONE, task.report
    assert task.plan[0].approval == "user"
    assert counter.calls == 1


def test_denied_step_does_not_run():
    counter = _Counter()
    task = Task(task_id="a2", description="x")
    _pipeline(_registry(counter), [_step()], approver=_RecordingApprover(False)).run(task)
    assert task.state is TaskState.BLOCKED
    assert task.plan[0].approval == "denied"
    assert "DENIED" in task.error
    assert counter.calls == 0


def test_default_approver_denies():
    counter = _Counter()
    task = Task(task_id="a3", description="x")
    _pipeline(_registry(counter), [_step()]).run(task)
    assert task.state is TaskState.BLOCKED
    assert counter.calls == 0
    assert DenyAllApprover().approve(_step()) is False


def test_blocked_step_is_never_offered_for_approval():
    """If any step is HIGH/BLOCK, nobody is asked anything and nothing runs."""
    counter = _Counter()
    registry = _registry(counter)  # MEDIUM tool
    registry.register(Tool(name="danger", risk="HIGH", description="", func=counter, input_schema=_SCHEMA))
    approver = _RecordingApprover(answer=True)
    steps = [_step(), Step(step_id=2, tool="danger", input={"message": "x"}, risk="LOW", expected="")]
    task = Task(task_id="a4", description="x")
    _pipeline(registry, steps, approver=approver).run(task)

    assert task.state is TaskState.BLOCKED
    assert approver.asked == []
    assert counter.calls == 0


@pytest.mark.parametrize(
    "answer, expected",
    [("y", True), ("YES", True), (" haan ", True), ("", False), ("n", False), ("maybe", False)],
)
def test_cli_approver_requires_explicit_yes(answer, expected):
    out: list[str] = []
    approver = CliApprover(input_fn=lambda _prompt: answer, output_fn=out.append)
    assert approver.approve(_step()) is expected
    assert any("demo.echo_guarded" in line for line in out)


def test_cli_approver_closed_input_means_no():
    def closed(_prompt):
        raise EOFError

    assert CliApprover(input_fn=closed, output_fn=lambda _l: None).approve(_step()) is False


def test_cli_guarded_echo_is_blocked_without_a_human():
    """End-to-end through the real CLI wiring: default approver denies."""
    task = Task(task_id="a5", description="guarded echo hello")
    build_pipeline().run(task)
    assert task.state is TaskState.BLOCKED
    assert task.plan[0].tool == "demo.echo_guarded"
    assert task.plan[0].result is None


def test_cli_guarded_echo_runs_when_approved():
    task = Task(task_id="a6", description="guarded echo hello")
    build_pipeline(approver=_RecordingApprover(True)).run(task)
    assert task.state is TaskState.DONE, task.report
    assert task.plan[0].result == {"echo": "hello", "verified": True}


# ------------------------------------------------------------------ audit log


def test_audit_records_full_lifecycle_in_order():
    audit = MemoryAuditLog()
    counter = _Counter()
    task = Task(task_id="l1", description="x")
    _pipeline(_registry(counter), [_step()], approver=_RecordingApprover(True), audit=audit).run(task)
    assert audit.names() == [
        "task_received",
        "policy_decision",
        "approval",
        "step_execute",
        "step_result",
        "task_finished",
    ]
    assert audit.events[-1]["state"] == "done"


def test_audit_redacts_secrets_and_truncates():
    clean = sanitize({
        "api_key": "sk-123",
        "nested": {"Password": "p@ss", "user": "zaid"},
        "items": [{"auth_token": "t"}],
        "body": "x" * 500,
    })
    assert clean["api_key"] == REDACTED
    assert clean["nested"] == {"Password": REDACTED, "user": "zaid"}
    assert clean["items"] == [{"auth_token": REDACTED}]
    assert len(clean["body"]) < 260 and clean["body"].endswith("chars)")


def test_jsonl_audit_writes_one_json_object_per_line(tmp_path):
    path = tmp_path / "logs" / "audit.jsonl"
    log = JsonlAuditLog(path)
    log.record("one", token="secret-value", n=1)
    log.record("two")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(l)["event"] for l in lines] == ["one", "two"]
    assert "secret-value" not in path.read_text(encoding="utf-8")


class _FailingAudit(AuditLog):
    """Audit storage that breaks right before a tool would run."""

    def __init__(self) -> None:
        self.inner = MemoryAuditLog()

    def record(self, event: str, **fields) -> None:
        if event == "step_execute":
            raise OSError("disk full")
        self.inner.record(event, **fields)


def test_audit_failure_fails_closed():
    """If the action cannot be audited, it must not happen."""
    counter = _Counter()
    task = Task(task_id="l2", description="x")
    pipeline = _pipeline(_registry(counter, risk="LOW"), [_step()], audit=_FailingAudit())
    with pytest.raises(OSError):
        pipeline.run(task)
    assert counter.calls == 0
    assert task.plan[0].state is StepState.PENDING
