"""Planner interface (ARCHITECTURE.md -> Planner, FEAT-3)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.task_manager.models import Task


class Planner(ABC):
    """Turns an understood task into explicit steps and dependencies."""

    @abstractmethod
    def plan(self, task: Task) -> Task:
        """Build ``task.plan`` and return the task.

        Planner reads ``task.intent`` and must never execute anything itself.
        """