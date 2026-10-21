"""Tool Registry (ARCHITECTURE.md -> Tool Registry; FEAT-4).

Registry holds a controlled list of tools. Each tool defines its name, a short
description, an input schema, and its risk level. The Executor asks the registry
to run a tool by name -- the registry is the only place a tool is bound to code.

Two security rules live here (ADR-009):

1. A tool's declared ``risk`` is the authority. A planner (and later an LLM) may only
   RAISE a step's risk, never lower it below the tool's declared level.
2. A tool never runs with input that does not match its schema. ``Tool.run`` validates
   every call, so the contract holds even if a caller forgets to pre-check.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

#: Allowed risk levels, lowest first (matches SECURITY.md).
RISK_LEVELS: tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")


class ToolError(RuntimeError):
    """Raised when a tool cannot be found or fails to run."""


class ToolInputError(ToolError):
    """Raised when a tool call does not match the tool's input schema."""


ToolFunc = Callable[..., dict[str, Any]]

# JSON-schema type name -> Python types accepted for it. ``bool`` is excluded from the
# numeric types on purpose (in Python ``True`` is an ``int``).
_TYPE_CHECKS: dict[str, Callable[[Any], bool]] = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


def normalize_risk(risk: Optional[str]) -> Optional[str]:
    """Return the canonical risk name, or ``None`` if it is not a known level."""
    normalized = (risk or "").strip().upper()
    return normalized if normalized in RISK_LEVELS else None


def max_risk(*risks: Optional[str]) -> Optional[str]:
    """Return the highest of the given risks; ``None`` if any of them is unknown.

    Unknown risk is treated as "cannot be classified", which the policy BLOCKs.
    """
    normalized = [normalize_risk(r) for r in risks]
    if not normalized or any(r is None for r in normalized):
        return None
    return max(normalized, key=RISK_LEVELS.index)


def validate_schema(schema: dict[str, Any]) -> None:
    """Check that a tool's input schema uses the small supported JSON-schema subset."""
    if schema.get("type") != "object":
        raise ValueError("Tool input schema must have type 'object'.")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise ValueError("Tool input schema 'properties' must be a dict.")
    for name, spec in properties.items():
        if spec.get("type") not in _TYPE_CHECKS:
            raise ValueError(f"Unsupported type for parameter {name!r}: {spec.get('type')!r}")
    for name in schema.get("required", []):
        if name not in properties:
            raise ValueError(f"Required parameter {name!r} is not declared in properties.")


class Tool:
    def __init__(
        self,
        name: str,
        risk: str,
        description: str,
        func: ToolFunc,
        input_schema: Optional[dict[str, Any]] = None,
    ) -> None:
        normalized = normalize_risk(risk)
        if normalized is None:
            raise ValueError(f"Tool {name!r} has invalid risk {risk!r}; use one of {RISK_LEVELS}.")
        schema = input_schema or {"type": "object", "properties": {}, "required": []}
        validate_schema(schema)

        self.name = name
        self.risk = normalized
        self.description = description
        self.input_schema = schema
        self._func = func

    def validate_input(self, kwargs: dict[str, Any]) -> None:
        """Raise :class:`ToolInputError` if ``kwargs`` breaks the input schema.

        Unknown parameters are rejected (no ``additionalProperties``), so a caller
        cannot smuggle extra arguments into the tool function.
        """
        if not isinstance(kwargs, dict):
            raise ToolInputError(f"{self.name}: input must be a dict, got {type(kwargs).__name__}.")
        properties = self.input_schema.get("properties", {})

        unknown = sorted(set(kwargs) - set(properties))
        if unknown:
            raise ToolInputError(f"{self.name}: unknown parameter(s) {unknown}.")

        missing = [p for p in self.input_schema.get("required", []) if p not in kwargs]
        if missing:
            raise ToolInputError(f"{self.name}: missing required parameter(s) {missing}.")

        for key, value in kwargs.items():
            expected = properties[key]["type"]
            if not _TYPE_CHECKS[expected](value):
                raise ToolInputError(
                    f"{self.name}: parameter {key!r} must be {expected}, got {type(value).__name__}."
                )

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.validate_input(kwargs)
        return self._func(**kwargs)

    def describe(self) -> dict[str, Any]:
        """A machine-readable description (used later to show tools to an LLM)."""
        return {
            "name": self.name,
            "description": self.description,
            "risk": self.risk,
            "input_schema": self.input_schema,
        }


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

    def describe_all(self) -> list[dict[str, Any]]:
        return [self._tools[n].describe() for n in self.names()]
