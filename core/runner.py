"""StepRunner: the ONE place where a step passes the safety gates and runs (ADR-009).

Both the fixed-plan :class:`core.pipeline.Pipeline` and the LLM
:class:`core.agent.loop.AgentLoop` use these methods, so the security logic is not
duplicated. The callers decide the ORDER (the pipeline checks every step before running
any step; the agent checks each step just before running it), but every check itself
lives here:

    decide()       policy, with risk resolved against the registry  -> audit "policy_decision"
    check_input()  tool schema validation                             (no human involved)
    approve()      human approval for CONFIRM steps                   -> audit "approval"
    execute()      audit "step_execute" (fail-closed) -> run -> verify -> audit "step_result"
"""

from __future__ import annotations

from typing import Optional

from core.executor.interface import Executor
from core.task_manager.models import Step, StepDecision, StepState, Task
from core.verifier.interface import Verifier
from security.approvals.approver import Approver, DenyAllApprover
from security.audit.log import AuditLog, MemoryAuditLog
from security.policy.policy import PolicyEngine
from tools.registry import ToolInputError, ToolRegistry


class StepRunner:
    def __init__(
        self,
        registry: ToolRegistry,
        policy: PolicyEngine,
        executor: Executor,
        verifier: Verifier,
        approver: Optional[Approver] = None,
        audit: Optional[AuditLog] = None,
    ) -> None:
        self.registry = registry
        self.policy = policy
        self.executor = executor
        self.verifier = verifier
        self.approver = approver or DenyAllApprover()
        self.audit = audit or MemoryAuditLog()

    def decide(self, task: Task, step: Step) -> StepDecision:
        step.decision = self.policy.decide_step(step, self.registry)
        self.audit.record(
            "policy_decision",
            task_id=task.task_id,
            step_id=step.step_id,
            tool=step.tool,
            risk=step.risk,
            decision=step.decision.value,
            reason=step.policy_reason,
        )
        if step.decision is StepDecision.BLOCK:
            step.state = StepState.BLOCKED
        return step.decision

    def check_input(self, step: Step) -> Optional[str]:
        """Return an error message if the input breaks the tool schema, else None."""
        try:
            self.registry.get(step.tool).validate_input(step.input)
        except ToolInputError as exc:
            step.state = StepState.FAILED
            step.error = str(exc)
            return str(exc)
        return None

    def approve(self, task: Task, step: Step) -> bool:
        approved = self.approver.approve(step)
        step.approval = "user" if approved else "denied"
        step.state = StepState.ALLOWED if approved else StepState.BLOCKED
        self.audit.record(
            "approval",
            task_id=task.task_id,
            step_id=step.step_id,
            tool=step.tool,
            approved=approved,
        )
        return approved

    def execute(self, task: Task, step: Step) -> bool:
        # Fail-closed: if this record cannot be written, the tool does not run.
        self.audit.record(
            "step_execute",
            task_id=task.task_id,
            step_id=step.step_id,
            tool=step.tool,
            input=step.input,
        )
        self.executor.execute(step)
        self.verifier.verify(step)
        self.audit.record(
            "step_result",
            task_id=task.task_id,
            step_id=step.step_id,
            tool=step.tool,
            state=step.state.value,
            outcome=step.outcome,
            error=step.error,
        )
        return self.step_ok(step)

    @staticmethod
    def step_ok(step: Step) -> bool:
        return (
            step.state is StepState.SUCCEEDED
            and bool(step.outcome)
            and "FAILED" not in step.outcome
        )
