"""Demo (safe) tools used by the Phase 1 MVP pipeline.

``demo.echo`` is intentionally trivial. It proves the Task -> Plan -> Policy -> Execute
-> Observe -> Verify -> Report loop WITHOUT touching the filesystem, computer control,
or any external service. This satisfies CRIT-8 ("skeleton pipeline with a simple tool").
"""

from __future__ import annotations

from typing import Any


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
        )
    )