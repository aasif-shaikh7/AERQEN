"""AERQEN CLI entry point (Phase 1 skeleton).

Run from the repo root:

    python -m app.entrypoint.cli "echo hello aerqen"
    python -m app.entrypoint.cli "guarded echo hello"   # asks for approval (y/N)

This builds the pipeline with the mock brain and demo tools, runs one task, and prints
a small report. Decisions and actions are appended to ``data/logs/audit.jsonl``
(secrets redacted). No real computer control or external service is used, so it is
safe to test as-is. If no one is at the terminal, approvals are denied automatically.
"""

from __future__ import annotations

import sys
import uuid

if __package__ in (None, ""):
    # Allow running as ``python app/entrypoint/cli.py`` from the repo root.
    sys.path.insert(0, ".")

from core.brain.mock import MockBrain
from core.executor.simple import SimpleExecutor
from core.pipeline import Pipeline
from core.planner.naive import NaivePlanner
from core.task_manager.models import Task
from core.verifier.checker import ContractVerifier
from security.approvals.approver import Approver, CliApprover, DenyAllApprover
from security.audit.log import AuditLog, JsonlAuditLog
from security.policy.policy import PolicyEngine
from tools.demo import build_demo_tools
from tools.registry import ToolRegistry


def build_pipeline(
    approver: Approver | None = None,
    audit: AuditLog | None = None,
) -> Pipeline:
    """Build the pipeline. Defaults are the safe ones: deny approvals, audit in memory."""
    registry = ToolRegistry()
    build_demo_tools(registry)

    return Pipeline(
        brain=MockBrain(),
        planner=NaivePlanner(),
        policy=PolicyEngine(),
        executor=SimpleExecutor(registry),
        verifier=ContractVerifier(),
        registry=registry,
        approver=approver,
        audit=audit,
    )


def render_report(task: Task) -> str:
    lines = [
        "AERQEN Phase 1 MVP - pipeline report",
        f"  task      : {task.task_id}",
        f"  request   : {task.description!r}",
        f"  state     : {task.state.value}",
    ]
    if task.intent:
        lines.append(f"  intent    : {task.intent}")
    for step in task.plan:
        lines.append(
            f"  step      : {step.tool} (risk {step.risk}, {step.decision.value}) "
            f"-> {step.state.value}"
        )
        if step.approval:
            lines.append(f"    approval: {step.approval}")
        if step.outcome:
            lines.append(f"    outcome : {step.outcome}")
        if step.result is not None:
            lines.append(f"    result  : {step.result}")
    if task.error:
        lines.append(f"  error     : {task.error}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2

    # Only ask a human when one can actually answer at this terminal.
    approver = CliApprover() if sys.stdin.isatty() else DenyAllApprover()
    pipeline = build_pipeline(approver=approver, audit=JsonlAuditLog())
    # Unique id per run so separate runs can be told apart in the audit log.
    task = Task(task_id=f"task-{uuid.uuid4().hex[:8]}", description=" ".join(argv))
    pipeline.run(task)
    print(render_report(task))
    return 0 if task.state.value in ("done", "blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())