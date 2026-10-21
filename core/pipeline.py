"""Pipeline orchestrator (ARCHITECTURE.md high-level flow; CRIT-8).

Runs a task through:

    Task -> Understand (Brain) -> Plan (Planner) -> Policy Check -> Input Check
         -> Approval -> Execute -> Observe -> Verify -> Report

Gate order matters and is fixed:

1. Policy (per step). Effective risk = max(planner claim, tool's declared risk). Unknown
   tools are BLOCKed. If ANY step is BLOCKed the task stops; nobody is asked to approve.
2. Input check. Every remaining step's input must match its tool's schema. Invalid
   input fails the task before a human is bothered with an approval prompt.
3. Approval. Each CONFIRM step goes to the Approver. One denial stops the task.
4. Execute in plan order. An audit record is written BEFORE each tool runs (fail-closed),
   and execution stops at the first step that fails or fails verification.
"""

from __future__ import annotations

from typing import Optional

from core.brain.interface import Brain
from core.executor.interface import Executor
from core.planner.interface import Planner
from core.task_manager.models import (
    Step,
    StepDecision,
    StepState,
    Task,
    TaskState,
)
from core.verifier.interface import Verifier
from security.approvals.approver import Approver, DenyAllApprover
from security.audit.log import AuditLog, MemoryAuditLog
from security.policy.policy import PolicyEngine
from tools.registry import ToolInputError, ToolRegistry


class Pipeline:
    def __init__(
        self,
        brain: Brain,
        planner: Planner,
        policy: PolicyEngine,
        executor: Executor,
        verifier: Verifier,
        registry: ToolRegistry,
        approver: Optional[Approver] = None,
        audit: Optional[AuditLog] = None,
    ) -> None:
        self._brain = brain
        self._planner = planner
        self._policy = policy
        self._executor = executor
        self._verifier = verifier
        self._registry = registry
        # Safe defaults: nobody approves anything, audit kept in memory only.
        self._approver = approver or DenyAllApprover()
        self._audit = audit or MemoryAuditLog()

    def run(self, task: Task) -> Task:
        self._audit.record("task_received", task_id=task.task_id, description=task.description)

        # 1. Understand
        self._brain.understand(task)
        if task.state is TaskState.FAILED:
            return self._finish_failed(task)

        # 2. Plan
        self._planner.plan(task)
        if task.state is TaskState.FAILED:
            return self._finish_failed(task)
        if not task.plan:
            task.error = "Planner produced no steps."
            return self._finish_failed(task)

        # 3. Policy check on every step (risk resolved against the registry)
        task.state = TaskState.EXECUTING
        for step in task.plan:
            step.decision = self._policy.decide_step(step, self._registry)
            self._audit.record(
                "policy_decision",
                task_id=task.task_id,
                step_id=step.step_id,
                tool=step.tool,
                risk=step.risk,
                decision=step.decision.value,
                reason=step.policy_reason,
            )

        blocked = [s for s in task.plan if s.decision is StepDecision.BLOCK]
        if blocked:
            for step in blocked:
                step.state = StepState.BLOCKED
            task.state = TaskState.BLOCKED
            task.error = self._describe_policy_gate(blocked, [])
            return self._report(task)

        # 4. Input check (before asking any human)
        for step in task.plan:
            try:
                self._registry.get(step.tool).validate_input(step.input)
            except ToolInputError as exc:
                step.state = StepState.FAILED
                step.error = str(exc)
                task.error = f"Invalid tool input: {exc}"
                return self._finish_failed(task)

        # 5. Approval for CONFIRM steps
        needs_confirm = [s for s in task.plan if s.decision is StepDecision.CONFIRM]
        for step in needs_confirm:
            approved = self._approver.approve(step)
            step.approval = "user" if approved else "denied"
            self._audit.record(
                "approval",
                task_id=task.task_id,
                step_id=step.step_id,
                tool=step.tool,
                approved=approved,
            )
            if not approved:
                step.state = StepState.BLOCKED
                task.state = TaskState.BLOCKED
                task.error = self._describe_policy_gate([], [step], denied=True)
                return self._report(task)
            step.state = StepState.ALLOWED

        # 6. Execute + observe + verify, in order; stop at the first failure
        for step in task.plan:
            # Fail-closed: if this record cannot be written, the tool does not run.
            self._audit.record(
                "step_execute",
                task_id=task.task_id,
                step_id=step.step_id,
                tool=step.tool,
                input=step.input,
            )
            self._executor.execute(step)
            self._verifier.verify(step)
            self._audit.record(
                "step_result",
                task_id=task.task_id,
                step_id=step.step_id,
                tool=step.tool,
                state=step.state.value,
                outcome=step.outcome,
                error=step.error,
            )
            if not self._step_ok(step):
                task.state = TaskState.FAILED
                task.error = (
                    f"Step {step.step_id} ({step.tool}) failed: {step.error or step.outcome}"
                )
                return self._report(task)

        task.state = TaskState.DONE
        return self._report(task)

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _step_ok(step: Step) -> bool:
        return (
            step.state is StepState.SUCCEEDED
            and bool(step.outcome)
            and "FAILED" not in step.outcome
        )

    def _finish_failed(self, task: Task) -> Task:
        task.state = TaskState.FAILED
        return self._report(task)

    @staticmethod
    def _describe(step: Step) -> str:
        text = f"{step.tool} risk={step.risk}"
        if step.policy_reason:
            text += f" ({step.policy_reason})"
        return text

    def _describe_policy_gate(self, blocked, confirm, denied: bool = False) -> str:
        parts = []
        if blocked:
            parts.append("BLOCKED: " + "; ".join(self._describe(s) for s in blocked))
        if confirm:
            label = "DENIED" if denied else "CONFIRM"
            parts.append(f"{label}: " + "; ".join(self._describe(s) for s in confirm))
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
                    "approval": s.approval,
                    "state": s.state.value,
                    "outcome": s.outcome,
                    "result": s.result,
                }
                for s in task.plan
            ],
        }
        self._audit.record(
            "task_finished",
            task_id=task.task_id,
            state=task.state.value,
            error=task.error,
        )
        return task
