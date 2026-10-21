"""A naive deterministic planner for the Phase 1 MVP.

It maps the small set of mock-brain intents to explicit steps. Later planners may be
LLM-driven, but they will still return :class:`Step` objects via the same interface.
"""

from __future__ import annotations

from core.planner.interface import Planner
from core.task_manager.models import Step, StepState, Task, TaskState


class NaivePlanner(Planner):
    def plan(self, task: Task) -> Task:
        task.state = TaskState.PLANNED
        intent = task.intent or {}
        action = intent.get("action")

        if action == "echo":
            message = intent.get("message", "")
            task.plan = [
                Step(
                    step_id=1,
                    tool="demo.echo",
                    input={"message": message},
                    risk="LOW",
                    expected="tool returns {echo: <same message>}",
                    state=StepState.PENDING,
                )
            ]
        elif action == "guarded_echo":
            message = intent.get("message", "")
            task.plan = [
                Step(
                    step_id=1,
                    tool="demo.echo_guarded",
                    input={"message": message},
                    # The planner only proposes a risk. The policy engine raises it to
                    # the tool's declared level if this is lower (ADR-009).
                    risk="MEDIUM",
                    expected="tool returns {echo: <same message>} after user approval",
                    state=StepState.PENDING,
                )
            ]
        else:
            task.state = TaskState.FAILED
            task.error = f"NaivePlanner has no plan for intent {action!r}."

        return task