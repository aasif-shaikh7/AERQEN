"""Pipeline orchestrator (ARCHITECTURE.md high-level flow; CRIT-8).

Runs a task through: Task -> Understand (Brain) -> Plan (Planner) -> Policy Check
(Security) -> Execute (Executor) -> Observe -> Verify (Verifier) -> Report.

In the skeleton MVP, policy CONFIRM is treated as not-approved (steps remain pending/
booltagged) and BLOCKED steps stop the pipeline. A real approval UI is a later phase.
"""

from __future__ import annotations

from core.brain.interface import Brain
from core.executor.interface import Executor
from core.planner.interface import Planner
from core.task_manager.models import (
    StepDecision,
    StepState,
    Task,
    TaskState,
)
from core.verifier.interface import Verifier
from security.policy.policy import PolicyEngine


class Pipeline:
    def __init__(
        self,
        brain: Brain,
        planner: Planner,
        policy: PolicyEngine,
        executor: Executor,
        verifier: Verifier,
    ) -> None:
        self._brain = brain
        self._planner = planner
        self._policy = policy
        self._executor = executor
        self._verifier = verifier

    def run(self, task: Task) -> Task:
        # 1. Understand
        self._brain.understand(task)
        if task.state is TaskState.FAILED:
            return self._finish_failed(task)

        # 2. Plan
        self._planner.plan(task)
        if task.state is TaskState.FAILED:
            return self._finish_failed(task)

        # 3. Policy check on every step
        task.state = TaskState.EXECUTING
        for step in task.plan:
            step.decision = self._policy.decide(step.risk)

        blocked = [s for s in task.plan if s.decision is StepDecision.BLOCK]
        needs_confirm = [s for s in task.plan if s.decision is StepDecision.CONFIRM]

        for step in task.plan:
            if step.decision is StepDecision.BLOCK:
                step.state = StepState.BLOCKED

        if blocked or needs_confirm:
            task.state = TaskState.BLOCKED
            task.error = self._describe_policy_gate(blocked, needs_confirm)
            return self._report(task)

        # 4. Execute + observe + verify for allowed steps
        for step in task.plan:
            self._executor.execute(step)
            self._verifier.verify(step)

        ok = all(
            s.state is StepState.SUCCEEDED and s.outcome and "FAILED" not in s.outcome
            for s in task.plan
        )
        task.state = TaskState.DONE if ok else TaskState.FAILED
        if not ok:
            task.error = "One or more steps failed verification."
        return self._report(task)

    def _finish_failed(self, task: Task) -> Task:
        task.state = TaskState.FAILED
        return self._report(task)

    @staticmethod
    def _describe(step) -> str:
        return f"{step.tool} risk={step.risk}"

    def _describe_policy_gate(self, blocked, confirm) -> str:
        parts = []
        if blocked:
            parts.append("BLOCKED: " + "; ".join(self._describe(s) for s in blocked))
        if confirm:
            parts.append("CONFIRM: " + "; ".join(self._describe(s) for s in confirm))
        return " ".join(parts)

    def _report(self, task: Task) -> Task:
        task.report = {
            "task_id": task.task_id,
            "description": task.description,
            "state": task.state.value,
            "intent": task.intent,
            "error": task.error,
            "steps": [
                {
                    "tool": s.tool,
                    "risk": s.risk,
                    "decision": s.decision.value,
                    "state": s.state.value,
                    "outcome": s.outcome,
                    "result": s.result,
                }
                for s in task.plan
            ],
        }
        return task