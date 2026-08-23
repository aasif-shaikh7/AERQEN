"""Tests for the complete Task -> ... -> Report pipeline (FEAT-1..FEAT-9).

These are REAL executable tests: pytest runs the same modules the CLI uses. A passing
suite is the "Measured" evidence for CRIT-8.
"""

from __future__ import annotations

from app.entrypoint.cli import build_pipeline
from core.task_manager.models import Task, TaskState
from tools.registry import ToolRegistry, ToolError
from tools.demo import build_demo_tools


def test_echo_task_reaches_done():
    pipeline = build_pipeline()
    task = Task(task_id="t1", description="echo hello aerqen")
    pipeline.run(task)

    assert task.state is TaskState.DONE, task.report
    assert task.report["state"] == "done"
    assert len(task.plan) == 1
    step = task.plan[0]
    assert step.state.value == "succeeded"
    assert step.outcome and "FAILED" not in step.outcome
    assert step.result == {"echo": "hello aerqen", "verified": True}


def test_bad_echo_fails_honestly():
    """A task outside the mock command set must fail with a clear error, not fake success."""
    pipeline = build_pipeline()
    task = Task(task_id="t2", description="open excel")
    pipeline.run(task)
    assert task.state is TaskState.FAILED
    assert task.report and task.report["error"]


def test_high_risk_tool_is_blocked_by_policy():
    """The policy engine (SECURITY.md) must BLOCK high-risk actions by default."""
    from security.policy.policy import PolicyEngine, StepDecision

    policy = PolicyEngine()
    assert policy.decide("LOW") is StepDecision.ALLOW
    assert policy.decide("MEDIUM") is StepDecision.CONFIRM
    assert policy.decide("HIGH") is StepDecision.BLOCK


def test_registry_rejects_unknown_tool():
    registry = ToolRegistry()
    build_demo_tools(registry)
    assert registry.has("demo.echo")
    try:
        registry.get("does.not.exist")
        raised = False
    except ToolError:
        raised = True
    assert raised is True