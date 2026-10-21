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
from core.runner import StepRunner
from core.task_manager.models import (
    Step,
    StepDecision,
    Task,
    TaskState,
)
from core.verifier.interface import Verifier
from security.approvals.approver import Approver, DenyAllApprover
from security.audit.log import AuditLog, MemoryAuditLog
from security.policy.policy import PolicyEngine
from tools.registry import ToolRegistry


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
        self._registry = registry
        # Safe defaults: nobody approves anything, audit kept in memory only.
        self._approver = approver or DenyAllApprover()
        self._audit = audit or MemoryAuditLog()
        # The gates live in ONE place, shared with the agent loop. The runner and the
        # pipeline must share the same audit + approver instances, so events land in the
        # same log and the same person is asked to approve.
        self._runner = StepRunner(
            registry=registry,
            policy=policy,
            executor=executor,
            verifier=verifier,
            approver=self._approver,
            audit=self._audit,
        )

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

        # 3. Policy check on every step (risk resolved against the registry).
        # The runner writes one "policy_decision" audit record per step, in order.
        task.state = TaskState.EXECUTING
        for step in task.plan:
            self._runner.decide(task, step)

        blocked = [s for s in task.plan if s.decision is StepDecision.BLOCK]
        if blocked:
            # The runner already marked each blocked step BLOCKED.
            task.state = TaskState.BLOCKED
            task.error = self._describe_policy_gate(blocked, [])
            return self._report(task)

        # 4. Input check (before asking any human). The runner marks the step FAILED.
        for step in task.plan:
            input_error = self._runner.check_input(step)
            if input_error is not None:
                task.error = f"Invalid tool input: {input_error}"
                return self._finish_failed(task)

        # 5. Approval for CONFIRM steps (runner writes one "approval" record each).
        needs_confirm = [s for s in task.plan if s.decision is StepDecision.CONFIRM]
        for step in needs_confirm:
            if not self._runner.approve(task, step):
                task.state = TaskState.BLOCKED
                task.error = self._describe_policy_gate([], [step], denied=True)
                return self._report(task)

        # 6. Execute + observe + verify, in order; stop at the first failure.
        for step in task.plan:
            if not self._runner.execute(task, step):
                task.state = TaskState.FAILED
                task.error = (
                    f"Step {step.step_id} ({step.tool}) failed: {step.error or step.outcome}"
                )
                return self._report(task)

        task.state = TaskState.DONE
        return self._report(task)

    # ------------------------------------------------------------------ helpers

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
