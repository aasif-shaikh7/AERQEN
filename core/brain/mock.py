"""Mock brain: deterministic understanding for the Phase 1 skeleton pipeline.

Because the local Ollama model (ADR-005) is not assumed to be installed yet, this mock
understands a small, safe command set. The interface is identical to the future LLM
brain, so swapping it later does not touch the rest of the pipeline.
"""

from __future__ import annotations

from core.brain.interface import Brain
from core.task_manager.models import Task, TaskState


class MockBrain(Brain):
    """Understands a constrained command set for the MVP loop."""

    def understand(self, task: Task) -> None:
        task.state = TaskState.UNDERSTANDING
        description = task.description.strip()
        lower = description.lower()

        # "guarded echo <msg>": same as echo, but routed to a MEDIUM-risk demo tool so
        # the approval gate (FEAT-6) can be tried by hand. Checked before "echo ".
        if lower.startswith("guarded echo "):
            message = description[len("guarded echo ") :].strip()
            if not message:
                task.state = TaskState.FAILED
                task.error = "guarded echo command requires a message."
                return
            task.intent = {"action": "guarded_echo", "message": message}
            task.state = TaskState.PLANNED
            return

        if lower.startswith("echo "):
            message = description[len("echo ") :].strip()
            if not message:
                task.state = TaskState.FAILED
                task.error = "echo command requires a message."
                return
            task.intent = {"action": "echo", "message": message}
            task.state = TaskState.PLANNED
            return

        task.state = TaskState.FAILED
        task.error = (
            f"Unsupported task (MVP mock brain knows only 'echo <message>' and "
            f"'guarded echo <message>'). "
            f"Got: {description!r}"
        )