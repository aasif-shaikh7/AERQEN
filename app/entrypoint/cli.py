"""AERQEN CLI entry point.

Run from the repo root:

    python -m app.entrypoint.cli "echo hello aerqen"
    python -m app.entrypoint.cli "guarded echo hello"      # asks for approval (y/N)
    python -m app.entrypoint.cli --agent "list my files"   # real LLM agent (Ollama)

Default (no flag): the fixed-plan pipeline with the mock brain and demo tools -- no LLM,
no filesystem, totally safe to test. ``--agent`` runs the LLM agent loop, which can use
the sandboxed file tools inside ``data/workspace`` only; writes still need approval.

Decisions and actions are appended to ``data/logs/audit.jsonl`` (secrets redacted). If
no one is at the terminal, approvals are denied automatically.
"""

from __future__ import annotations

import sys
import uuid

if __package__ in (None, ""):
    # Allow running as ``python app/entrypoint/cli.py`` from the repo root.
    sys.path.insert(0, ".")

from app.configuration.settings import Settings, load_settings
from core.agent.loop import AgentLoop
from core.memory.store import MemoryStore
from core.brain.mock import MockBrain
from core.executor.simple import SimpleExecutor
from core.pipeline import Pipeline
from core.planner.naive import NaivePlanner
from core.runner import StepRunner
from core.task_manager.models import Task
from core.verifier.checker import ContractVerifier
from integrations.ai.ollama import OllamaProvider
from security.approvals.approver import Approver, CliApprover, DenyAllApprover
from security.audit.log import AuditLog, JsonlAuditLog
from security.policy.policy import PolicyEngine
from tools.demo import build_demo_tools
from tools.files import build_file_tools
from tools.memory import build_memory_tools
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


def build_agent(
    approver: Approver | None = None,
    audit: AuditLog | None = None,
    settings: Settings | None = None,
) -> AgentLoop:
    """Build the LLM agent loop with the sandboxed file tools and an Ollama provider."""
    settings = settings or load_settings()
    registry = ToolRegistry()
    verifier = ContractVerifier()
    # File tools register their own verifier contracts; they live only in the workspace.
    build_file_tools(registry, settings.workspace, verifier=verifier)
    # Memory tools + a durable store the agent can read across runs (ADR-012).
    memory = MemoryStore(settings.memory_path, max_entries=settings.memory_max)
    build_memory_tools(registry, memory, verifier=verifier)

    runner = StepRunner(
        registry=registry,
        policy=PolicyEngine(),
        executor=SimpleExecutor(registry),
        verifier=verifier,
        approver=approver,
        audit=audit,
    )
    provider = OllamaProvider(
        base_url=settings.ollama_url,
        model=settings.ollama_model,
        timeout=settings.llm_timeout,
    )
    return AgentLoop(
        provider=provider,
        runner=runner,
        max_steps=settings.max_steps,
        memory=memory,
        memory_recall=settings.memory_recall,
    )


def render_report(task: Task, title: str = "AERQEN pipeline report") -> str:
    lines = [
        title,
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
    if task.answer:
        lines.append(f"  answer    : {task.answer}")
    if task.error:
        lines.append(f"  error     : {task.error}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    agent_mode = False
    if argv and argv[0] == "--agent":
        agent_mode = True
        argv = argv[1:]

    if not argv:
        print(__doc__)
        return 2

    # Only ask a human when one can actually answer at this terminal.
    approver = CliApprover() if sys.stdin.isatty() else DenyAllApprover()
    audit = JsonlAuditLog()
    # Unique id per run so separate runs can be told apart in the audit log.
    task = Task(task_id=f"task-{uuid.uuid4().hex[:8]}", description=" ".join(argv))

    if agent_mode:
        build_agent(approver=approver, audit=audit).run(task)
        print(render_report(task, title="AERQEN agent report"))
    else:
        build_pipeline(approver=approver, audit=audit).run(task)
        print(render_report(task))

    return 0 if task.state.value in ("done", "blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())