"""Provider-neutral LLM interface (ADR-005: provider adapter in ``integrations/ai/``).

The agent loop depends only on this file. Adding a cloud provider later means writing one
more ``LLMProvider`` subclass; nothing in ``core/`` changes.

Messages are plain dicts with ``role`` ("system" | "user" | "assistant" | "tool") and
``content``. An assistant message may carry ``tool_calls`` (list of :class:`ToolCall`);
a tool message carries ``tool_name``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class LLMError(RuntimeError):
    """The model could not be reached or returned something unusable."""


@dataclass
class ToolCall:
    name: str
    arguments: Any  # should be a dict; validated by the tool schema, never trusted


@dataclass
class LLMReply:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMProvider(ABC):
    #: Human-readable id for reports/audit, e.g. "ollama:qwen2.5:7b".
    name: str = "llm"

    @abstractmethod
    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMReply:
        """Send the conversation and the available tools; return the model's reply.

        ``tools`` items look like ``{"name", "description", "parameters"}`` (JSON schema).
        Must raise :class:`LLMError` on any transport or format failure.
        """

    def is_available(self) -> bool:
        """Cheap reachability check. Default: assume available."""
        return True
