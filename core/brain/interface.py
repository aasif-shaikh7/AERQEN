"""Brain interface (ARCHITECTURE.md -> Brain).

The brain turns unstructured user intent into structured task information. It must NOT
directly control hardware, files, or the network. This interface stays stable so a
real LLM-backed brain can later replace the mock via the integrations/ai adapter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.task_manager.models import Task


class Brain(ABC):
    """Contract for converting a task description into a structured intent."""

    @abstractmethod
    def understand(self, task: Task) -> None:
        """Populate ``task.intent`` from ``task.description``.

        Must set task.state to UNDERSTANDING on entry and move it to PLANNED (or
        FAILED) when understanding finishes.
        """