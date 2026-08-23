"""AERQEN: core task data model and lifecycle states.

This is the structured representation FEAT-1 in ``todo-list.md``. It is deliberately
kept free of any LLM or tool dependency so that every layer can read/write it safely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class TaskState(str, Enum):
    """High-level lifecycle of a task through the pipeline."""

    RECEIVED = "received"
    UNDERSTANDING = "understanding"
    PLANNED = "planned"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class StepDecision(str, Enum):
    """Outcome of the policy check for one step (per SECURITY.md / FEAT-5)."""

    ALLOW = "allow"
    CONFIRM = "confirm"
    BLOCK = "block"


class StepState(str, Enum):
    """Lifecycle of a single planned step."""

    PENDING = "pending"
    ALLOWED = "allowed"
    CONFIRM = "confirmed"
    BLOCKED = "blocked"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Step:
    """One planned action with its tool binding and expected outcome."""

    step_id: int
    tool: str
    input: dict[str, Any]
    risk: str  # LOW | MEDIUM | HIGH (matches SECURITY.md)
    expected: str  # human-readable description of a successful outcome
    decision: StepDecision = StepDecision.ALLOW
    state: StepState = StepState.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

    # Confidence/evidence from the verifier (Measured/Reasoned/... per GLOSSARY).
    outcome: Optional[str] = None


@dataclass
class Task:
    """The structured representation of a user request moving through the loop."""

    task_id: str
    description: str
    state: TaskState = TaskState.RECEIVED
    intent: Optional[dict[str, Any]] = None
    plan: list[Step] = field(default_factory=list)
    report: Optional[dict[str, Any]] = None
    error: Optional[str] = None