"""Deterministic verifier for the demo tool (and future tools with known contracts).

For the skeleton pipeline the verifier checks that ``demo.echo`` returned exactly the
message it was given. This demonstrates verification without any external assumption.
"""

from __future__ import annotations

from core.task_manager.models import Step, StepState
from core.verifier.interface import Verifier


class ContractVerifier(Verifier):
    def verify(self, step: Step) -> None:
        # Only steps that ran successfully can be meaningfully verified.
        if step.state is not StepState.SUCCEEDED:
            step.outcome = f"Not verified: step state was {step.state.value}"
            return

        result = step.result or {}

        if step.tool in ("demo.echo", "demo.echo_guarded"):
            expected = (step.input or {}).get("message")
            echoed = result.get("echo")
            if expected is not None and echoed == expected:
                step.outcome = "Measured: tool returned the exact message."
            else:
                step.outcome = "FAILED: echo output did not match input."
            return

        # Unknown tools default to a honest, unverified outcome.
        step.outcome = "Unverified: no contract registered for this tool."