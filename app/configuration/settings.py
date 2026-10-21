"""AERQEN settings (small, safe, local).

Phase 1 has no secrets. Future provider credentials must come from environment
variables (per SECURITY.md / secrets rule), never hard-coded here.

The LLM and agent settings (Phase 2, ADR-005) all read from environment variables so
the same code runs against a local Ollama or one on another PC on the LAN, and so an
operator can tighten the step budget without touching code:

    AERQEN_OLLAMA_URL    default http://127.0.0.1:11434
    AERQEN_OLLAMA_MODEL  default qwen2.5:7b
    AERQEN_WORKSPACE     default data/workspace  (the only folder file tools may touch)
    AERQEN_MAX_STEPS     default 8               (hard cap on agent loop iterations)
    AERQEN_LLM_TIMEOUT   default 120             (seconds per model call)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _int_env(name: str, default: int) -> int:
    """Read a positive integer from the environment; fall back on anything unusable."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _float_env(name: str, default: float) -> float:
    """Read a positive float from the environment; fall back on anything unusable."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


@dataclass
class Settings:
    app_name: str = field(default="aerqen")
    log_level: str = field(default_factory=lambda: os.getenv("AERQEN_LOG_LEVEL", "INFO"))

    # LLM provider (ADR-005)
    ollama_url: str = field(
        default_factory=lambda: os.getenv("AERQEN_OLLAMA_URL", "http://127.0.0.1:11434")
    )
    ollama_model: str = field(
        default_factory=lambda: os.getenv("AERQEN_OLLAMA_MODEL", "qwen2.5:7b")
    )

    # Agent loop + file sandbox (ADR-009)
    workspace: str = field(default_factory=lambda: os.getenv("AERQEN_WORKSPACE", "data/workspace"))
    max_steps: int = field(default_factory=lambda: _int_env("AERQEN_MAX_STEPS", 8))
    llm_timeout: float = field(default_factory=lambda: _float_env("AERQEN_LLM_TIMEOUT", 120.0))

    # Agent memory (ADR-012): a small durable notebook the agent reads/writes across runs.
    memory_path: str = field(
        default_factory=lambda: os.getenv("AERQEN_MEMORY", "data/memory/memory.jsonl")
    )
    memory_max: int = field(default_factory=lambda: _int_env("AERQEN_MEMORY_MAX", 200))
    memory_recall: int = field(default_factory=lambda: _int_env("AERQEN_MEMORY_RECALL", 5))


def load_settings() -> Settings:
    return Settings()