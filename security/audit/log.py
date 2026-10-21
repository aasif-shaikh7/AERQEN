"""Audit log (FEAT-11; SECURITY.md §3 Secrets, §7 Data minimization).

Every important decision and action is written as one JSON line (JSONL), so the log can
be read by a human or by a script.

Rules enforced here, not left to callers:
- Values under secret-looking keys (password, token, api_key, cookie, ...) become "***".
- Long strings are truncated, so the log never becomes a copy of user data.
- Writing is FAIL-CLOSED: if the audit record cannot be written, ``record`` raises. The
  pipeline writes the "about to execute" record before running a tool, so an action that
  cannot be audited does not happen.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REDACTED = "***"
MAX_STRING = 200

_SECRET_KEY = re.compile(
    r"pass(word|wd)?|secret|token|api[_-]?key|auth|cookie|credential|private[_-]?key",
    re.IGNORECASE,
)


def sanitize(value: Any, max_string: int = MAX_STRING) -> Any:
    """Return a copy of ``value`` with secrets redacted and long strings truncated."""
    if isinstance(value, dict):
        return {
            str(k): REDACTED if _SECRET_KEY.search(str(k)) else sanitize(v, max_string)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize(v, max_string) for v in value]
    if isinstance(value, str) and len(value) > max_string:
        return value[:max_string] + f"...(+{len(value) - max_string} chars)"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return sanitize(str(value), max_string)


class AuditLog(ABC):
    @abstractmethod
    def record(self, event: str, **fields: Any) -> None:
        """Record one event. Must raise if the event could not be stored."""


class JsonlAuditLog(AuditLog):
    """Appends sanitized events to a JSONL file (default: ``data/logs/audit.jsonl``)."""

    def __init__(self, path: str | Path = "data/logs/audit.jsonl") -> None:
        self.path = Path(path)

    def record(self, event: str, **fields: Any) -> None:
        entry = {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            **sanitize(fields),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


class MemoryAuditLog(AuditLog):
    """Keeps sanitized events in a list. Used by tests."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, event: str, **fields: Any) -> None:
        self.events.append({"event": event, **sanitize(fields)})

    def names(self) -> list[str]:
        return [e["event"] for e in self.events]
