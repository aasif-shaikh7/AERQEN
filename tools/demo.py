"""Demo (safe) tools used by the Phase 1 MVP pipeline.

``demo.echo`` is intentionally trivial. It proves the Task -> Plan -> Policy -> Execute
-> Observe -> Verify -> Report loop WITHOUT touching the filesystem, computer control,
or any external service. This satisfies CRIT-8 ("skeleton pipeline with a simple tool").

``demo.echo_guarded`` does exactly the same harmless thing but is DECLARED as MEDIUM
risk. It exists only so the approval gate (FEAT-6) can be exercised end-to-end without
giving AERQEN any real power. It is not a real MEDIUM-risk capability.
"""

from __future__ import annotations

from typing import Any

_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {"message": {"type": "string", "description": "Text to echo back."}},
    "required": ["message"],
}


def echo(message: str) -> dict[str, Any]:
    return {"echo": message, "verified": True}


def build_demo_tools(registry) -> None:
    """Register the demo tools into the given ToolRegistry."""
    from tools.registry import Tool

    registry.register(
        Tool(
            name="demo.echo",
            risk="LOW",
            description="Returns the exact message it was given (used to prove the pipeline).",
            func=echo,
            input_schema=_MESSAGE_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="demo.echo_guarded",
            risk="MEDIUM",
            description=(
                "Same as demo.echo, but declared MEDIUM risk so the approval gate can be "
                "tested. Harmless."
            ),
            func=echo,
            input_schema=_MESSAGE_SCHEMA,
        )
    )
