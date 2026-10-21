"""AERQEN policy engine (FEAT-5 / SECURITY.md -> Permission Levels).

Decides between ALLOW / CONFIRM / BLOCK for an action, based on a small set of rules.
This is the FIRST line of the security layering (ARCHITECTURE.md).

``decide_step`` is the entry point the pipeline uses. It resolves the step's EFFECTIVE
risk as the higher of the planner's claim and the tool's declared risk (ADR-009), so a
planner -- or a future LLM planner -- can never talk a risky tool down to LOW.
"""

from __future__ import annotations

from core.task_manager.models import Step, StepDecision
from tools.registry import ToolRegistry, max_risk, normalize_risk


# Default mapping for the Phase 1 MVP, aligned with SECURITY.md:
#   LOW    -> ALLOW   (can run automatically)
#   MEDIUM -> CONFIRM (needs evaluation / may require approval)
#   HIGH   -> BLOCK   (never in the Phase 1 skeleton)
_DEFAULT_RULE = {
    "LOW": StepDecision.ALLOW,
    "MEDIUM": StepDecision.CONFIRM,
    "HIGH": StepDecision.BLOCK,
}


class PolicyEngine:
    def __init__(self, rules: dict | None = None) -> None:
        self._rules = dict(_DEFAULT_RULE if rules is None else rules)

    def decide(self, risk: str) -> StepDecision:
        normalized = normalize_risk(risk or "LOW")
        if normalized is None:
            return StepDecision.BLOCK  # unknown risk level: fail closed
        return self._rules.get(normalized, StepDecision.BLOCK)

    def decide_step(self, step: Step, registry: ToolRegistry) -> StepDecision:
        """Resolve the effective risk of ``step`` and return the decision.

        - Unknown tool -> BLOCK (nothing outside the registry can run).
        - Unknown risk label on either side -> BLOCK.
        - Otherwise ``step.risk`` is rewritten to max(planner risk, tool risk).
        """
        if not registry.has(step.tool):
            step.policy_reason = f"tool {step.tool!r} is not in the registry"
            return StepDecision.BLOCK

        declared = registry.get(step.tool).risk
        effective = max_risk(step.risk, declared)
        if effective is None:
            step.policy_reason = f"unrecognised risk label {step.risk!r}"
            return StepDecision.BLOCK

        if effective != normalize_risk(step.risk):
            step.policy_reason = (
                f"risk raised from {step.risk!r} to {effective} (tool's declared risk)"
            )
        step.risk = effective
        return self.decide(effective)
