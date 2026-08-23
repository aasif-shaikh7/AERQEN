"""Simple executor that runs a step through the ToolRegistry."""

from __future__ import annotations

from core.executor.interface import Executor
from core.task_manager.models import Step, StepState
from tools.registry import ToolRegistry


class SimpleExecutor(Executor):
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, step: Step) -> None:
        step.state = StepState.RUNNING
        try:
            tool = self._registry.get(step.tool)
            result = tool.run(**step.input)
            step.result = result
            step.state = StepState.SUCCEEDED
        except Exception as exc:  # noqa: BLE001 - we record, never re-raise
            step.error = f"{type(exc).__name__}: {exc}"
            step.state = StepState.FAILED