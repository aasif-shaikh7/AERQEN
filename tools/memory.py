"""Memory tools (ADR-012): the agent's durable notebook, exposed as registry tools.

All three are LOW risk. Unlike the file tools, these never touch the user's workspace
files -- they read/write only the bounded :class:`~core.memory.store.MemoryStore`, so
letting the agent jot a note without an approval prompt is safe and keeps the loop usable.

    memory.remember  LOW  save a short note (optionally tagged) for later runs
    memory.recall    LOW  find saved notes matching a query (empty query = most recent)
    memory.list      LOW  list the most recent saved notes
"""

from __future__ import annotations

from typing import Any, Callable

from core.memory.store import MemoryStore
from tools.registry import Tool, ToolError

_REMEMBER_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "The note to remember (short)."},
        "tags": {"type": "string", "description": "Optional comma-separated tags."},
    },
    "required": ["text"],
}
_RECALL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "What to look for. Empty = most recent notes."},
        "limit": {"type": "integer", "description": "Max notes to return (default 5)."},
    },
    "required": [],
}
_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer", "description": "Max notes to return (default 10)."}
    },
    "required": [],
}


def _make_remember(store: MemoryStore) -> Callable[..., dict[str, Any]]:
    def memory_remember(text: str, tags: str = "") -> dict[str, Any]:
        try:
            entry = store.remember(text, tags)
        except ValueError as exc:
            raise ToolError(str(exc))
        return {"id": entry["id"], "saved": True, "total": store.count()}

    return memory_remember


def _make_recall(store: MemoryStore) -> Callable[..., dict[str, Any]]:
    def memory_recall(query: str = "", limit: int = 5) -> dict[str, Any]:
        results = store.recall(query, limit)
        return {"query": query or None, "count": len(results), "results": results}

    return memory_recall


def _make_list(store: MemoryStore) -> Callable[..., dict[str, Any]]:
    def memory_list(limit: int = 10) -> dict[str, Any]:
        entries = store.recent(limit)
        return {"count": len(entries), "entries": entries}

    return memory_list


# ---------------------------------------------------------------- verifier contracts


def _verify_remember(step) -> str:
    result = step.result or {}
    if result.get("saved") and result.get("id"):
        return f"Measured: note #{result['id']} saved ({result.get('total', '?')} total)."
    return "FAILED: memory.remember did not confirm a saved note."


def _verify_recall(step) -> str:
    result = step.result or {}
    if "results" in result:
        return f"Measured: {result.get('count', 0)} matching note(s)."
    return "FAILED: memory.recall returned no results field."


def _verify_list(step) -> str:
    result = step.result or {}
    if "entries" in result:
        return f"Measured: {result.get('count', 0)} note(s)."
    return "FAILED: memory.list returned no entries field."


def build_memory_tools(registry, store: MemoryStore, verifier=None) -> None:
    """Register the three memory tools (and their verifier contracts) into the registry."""
    registry.register(
        Tool(
            name="memory.remember",
            risk="LOW",
            description="Save a short note to remember for later runs. Optionally tag it.",
            func=_make_remember(store),
            input_schema=_REMEMBER_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="memory.recall",
            risk="LOW",
            description="Find notes you saved earlier. Empty query returns the most recent notes.",
            func=_make_recall(store),
            input_schema=_RECALL_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="memory.list",
            risk="LOW",
            description="List your most recent saved notes.",
            func=_make_list(store),
            input_schema=_LIST_SCHEMA,
        )
    )

    if verifier is not None:
        verifier.register("memory.remember", _verify_remember)
        verifier.register("memory.recall", _verify_recall)
        verifier.register("memory.list", _verify_list)
