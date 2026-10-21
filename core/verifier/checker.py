"""Deterministic verifier (FEAT-8).

A tool's contract is a small function ``fn(step) -> str`` that inspects the step's
result and returns a short evidence verdict (per GLOSSARY: Measured / Reasoned / ...).
A verdict that contains ``"FAILED"`` marks the step as failed (see StepRunner.step_ok).

Tools register their contract with :meth:`register` (the file tools do this when they
are built). ``demo.echo`` / ``demo.echo_guarded`` keep a built-in contract so the
Phase 1 tests need no changes. A tool with no contract gets an honest "Unverified".
"""

from __future__ import annotations

from typing import Callable

from core.task_manager.models import Step, StepState
from core.verifier.interface import Verifier

Contract = Callable[[Step], str]


class ContractVerifier(Verifier):
    def __init__(self) -> None:
        self._contracts: dict[str, Contract] = {}

    def register(self, tool_name: str, fn: Contract) -> None:
        """Bind a verification contract to a tool name (last registration wins)."""
        self._contracts[tool_name] = fn

    def verify(self, step: Step) -> None:
        # Only steps that ran successfully can be meaningfully verified.
        if step.state is not StepState.SUCCEEDED:
            step.outcome = f"Not verified: step state was {step.state.value}"
            return

        contract = self._contracts.get(step.tool)
        if contract is not None:
            step.outcome = contract(step)
            return

        # Built-in contract for the demo tools (kept so Phase 1 tests are unchanged).
        if step.tool in ("demo.echo", "demo.echo_guarded"):
            result = step.result or {}
            expected = (step.input or {}).get("message")
            echoed = result.get("echo")
            if expected is not None and echoed == expected:
                step.outcome = "Measured: tool returned the exact message."
            else:
                step.outcome = "FAILED: echo output did not match input."
            return

        # Unknown tools default to an honest, unverified outcome.
        step.outcome = "Unverified: no contract registered for this tool."
