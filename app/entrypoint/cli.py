"""AERQEN CLI entry point (Phase 1 skeleton).

Run from the repo root:

    python -m app.entrypoint.cli "echo hello aerqen"

This builds the pipeline with the mock brain and demo tool, runs one task, and prints
a small report. No real computer control, filesystem mutation, or external service
is used, so it is safe to test as-is.
"""

from __future__ import annotations

import sys

if __package__ in (None, ""):
    # Allow running as ``python app/entrypoint/cli.py`` from the repo root.
    sys.path.insert(0, ".")

from core.brain.mock import MockBrain
from core.executor.simple import SimpleExecutor
from core.pipeline import Pipeline
from core.planner.naive import NaivePlanner
from core.task_manager.models import Task
from core.verifier.checker import ContractVerifier
from security.policy.policy import PolicyEngine
from tools.demo import build_demo_tools
from tools.registry import ToolRegistry


def build_pipeline() -> Pipeline:
    registry = ToolRegistry()
    build_demo_tools(registry)

    return Pipeline(
        brain=MockBrain(),
        planner=NaivePlanner(),
        policy=PolicyEngine(),
        executor=SimpleExecutor(registry),
        verifier=ContractVerifier(),
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
        lines.append(f"  step      : {step.tool} -> {step.state.value}")
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

    pipeline = build_pipeline()
    task = Task(task_id="mvp-1", description=" ".join(argv))
    pipeline.run(task)
    print(render_report(task))
    return 0 if task.state.value in ("done", "blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())