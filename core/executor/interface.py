"""Executor interface: runs approved tool actions and returns structured results."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.task_manager.models import Step


class Executor(ABC):
    @abstractmethod
    def execute(self, step: Step) -> None:
        """Run the step's tool and store the result.

        This never assumes success: it records either a result or an error on the step.
        """