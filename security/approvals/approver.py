"""Approvers decide whether a CONFIRM-level step may run (FEAT-6; SECURITY.md).

The pipeline asks an :class:`Approver` once per CONFIRM step, BEFORE anything runs.
BLOCK steps are never shown to an approver: no human answer can unblock them.

- :class:`DenyAllApprover` is the safe default (non-interactive runs, tests, scripts).
- :class:`CliApprover` asks the person at the terminal. Only an explicit "y"/"yes"
  approves; empty input, anything else, or a closed input stream all mean NO.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from core.task_manager.models import Step

_YES = {"y", "yes", "haan", "ha"}


class Approver(ABC):
    @abstractmethod
    def approve(self, step: Step) -> bool:
        """Return True only if a human explicitly allowed this step."""


class DenyAllApprover(Approver):
    """Never approves. Used whenever nobody is present to answer."""

    def approve(self, step: Step) -> bool:
        return False


class CliApprover(Approver):
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._input = input_fn
        self._output = output_fn

    def approve(self, step: Step) -> bool:
        self._output("")
        self._output("APPROVAL NEEDED")
        self._output(f"  tool     : {step.tool}")
        self._output(f"  risk     : {step.risk}")
        self._output(f"  input    : {step.input}")
        self._output(f"  expected : {step.expected}")
        try:
            answer = self._input("Allow this step? [y/N]: ")
        except (EOFError, KeyboardInterrupt):
            self._output("  (no answer -> denied)")
            return False
        return answer.strip().lower() in _YES
