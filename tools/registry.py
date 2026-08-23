"""Tool Registry (ARCHITECTURE.md -> Tool Registry; FEAT-4).

Registry holds a controlled list of tools. Each tool defines its name, a short
description, input/output notes, and its risk level. The Executor asks the registry
to run a tool by name -- the registry is the only place a tool is bound to code.
"""

from __future__ import annotations

from typing import Any, Callable


class ToolError(RuntimeError):
    """Raised when a tool cannot be found or fails to run."""


ToolFunc = Callable[..., dict[str, Any]]


class Tool:
    def __init__(
        self,
        name: str,
        risk: str,
        description: str,
        func: ToolFunc,
    ) -> None:
        self.name = name
        self.risk = risk.upper()
        self.description = description
        self._func = func

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return self._func(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ToolError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise ToolError(f"Unknown tool: {name}")
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def names(self) -> list[str]:
        return sorted(self._tools)