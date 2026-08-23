"""AERQEN policy engine (FEAT-5 / SECURITY.md -> Permission Levels).

Decides between ALLOW / CONFIRM / BLOCK for an action's risk level, based on a small
set of rules. This is the FIRST line of the security layering (ARCHITECTURE.md).
"""

from __future__ import annotations

from core.task_manager.models import StepDecision


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
        normalized = (risk or "LOW").upper()
        return self._rules.get(normalized, StepDecision.BLOCK)