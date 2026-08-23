"""Verifier interface: checks whether an action achieved its intended result."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.task_manager.models import Step


class Verifier(ABC):
    @abstractmethod
    def verify(self, step: Step) -> None:
        """Set ``step.outcome`` to a short evidence verdict and mark success/failure."""