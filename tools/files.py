"""Sandboxed file tools for the agent loop (ADR-009).

These are the first tools that touch the real filesystem, so they are deliberately
small and locked down. Every path is resolved INSIDE a single workspace folder
(default ``data/workspace``); anything that points outside it -- an absolute path, a
drive letter, or a ``..`` that climbs above the root -- is rejected before any disk
access happens.

    files.list       LOW     list entries of a folder in the workspace (read-only)
    files.read_text  LOW     read a UTF-8 text file in the workspace (read-only)
    files.write_text MEDIUM  create a NEW text file (never overwrites an existing one)

``files.write_text`` is CREATE-ONLY on purpose: an agent can add a file but can never
silently destroy one the user already has. Its verifier re-reads the file and compares
the sha256, so "written" is Measured, not assumed.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Callable

from tools.registry import Tool, ToolError, ToolInputError

#: Cap on how much text ``files.read_text`` returns, so a huge file cannot flood the
#: model's context (or the audit log). The reply flags when it was truncated.
MAX_READ_CHARS = 20_000

_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Folder inside the workspace. Default '.'."}
    },
    "required": [],
}
_READ_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File inside the workspace to read."}
    },
    "required": ["path"],
}
_WRITE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "New file path inside the workspace."},
        "content": {"type": "string", "description": "UTF-8 text to write."},
    },
    "required": ["path", "content"],
}


def _safe_path(root: Path, rel: str) -> Path:
    """Resolve ``rel`` under ``root`` or raise :class:`ToolInputError`.

    Rejects absolute paths, Windows drive letters, and any path that escapes the
    workspace via ``..``. The containment check is done on the *resolved* path, so
    symlink / ``..`` tricks cannot slip through.
    """
    if not isinstance(rel, str) or not rel.strip():
        raise ToolInputError("path must be a non-empty string.")
    # Reject obvious escapes up front (clear message, before touching the disk).
    if os.path.isabs(rel) or ":" in rel or rel.startswith(("/", "\\")):
        raise ToolInputError(f"path must be relative to the workspace: {rel!r}")

    root_resolved = root.resolve()
    full = (root_resolved / rel).resolve()
    try:
        full.relative_to(root_resolved)
    except ValueError:
        raise ToolInputError(f"path escapes the workspace: {rel!r}")
    return full


def _make_list(root: Path) -> Callable[..., dict[str, Any]]:
    def files_list(path: str = ".") -> dict[str, Any]:
        target = _safe_path(root, path)
        if not target.exists():
            raise ToolError(f"No such path in workspace: {path!r}")
        if not target.is_dir():
            raise ToolError(f"Not a folder: {path!r}")
        entries = [
            {"name": child.name, "type": "dir" if child.is_dir() else "file"}
            for child in sorted(target.iterdir(), key=lambda c: c.name)
        ]
        return {"path": path, "count": len(entries), "entries": entries}

    return files_list


def _make_read(root: Path) -> Callable[..., dict[str, Any]]:
    def files_read_text(path: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if not target.exists() or not target.is_file():
            raise ToolError(f"No such file in workspace: {path!r}")
        text = target.read_text(encoding="utf-8", errors="replace")
        truncated = len(text) > MAX_READ_CHARS
        return {
            "path": path,
            "content": text[:MAX_READ_CHARS],
            "truncated": truncated,
            "bytes": target.stat().st_size,
        }

    return files_read_text


def _make_write(root: Path) -> Callable[..., dict[str, Any]]:
    def files_write_text(path: str, content: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if target.exists():
            raise ToolError(f"Refusing to overwrite existing file (create-only): {path!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8")
        target.write_text(content, encoding="utf-8")
        return {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "created": True,
        }

    return files_write_text


# ---------------------------------------------------------------- verifier contracts
# Each returns a short evidence verdict string for ContractVerifier. A string that
# contains "FAILED" marks the step as failed (see StepRunner.step_ok).


def _verify_list(step) -> str:
    result = step.result or {}
    if "entries" in result:
        return f"Measured: listed {result.get('count', 0)} entr(y/ies)."
    return "FAILED: files.list returned no entries field."


def _verify_read(step) -> str:
    result = step.result or {}
    if "content" in result:
        note = " (truncated)" if result.get("truncated") else ""
        return f"Measured: read {result.get('bytes', 0)} bytes{note}."
    return "FAILED: files.read_text returned no content."


def _make_verify_write(root: Path) -> Callable[..., str]:
    def verify(step) -> str:
        result = step.result or {}
        rel = (step.input or {}).get("path")
        if not rel:
            return "FAILED: no path recorded for files.write_text."
        try:
            target = _safe_path(root, rel)
        except ToolInputError:
            return "FAILED: recorded path is outside the workspace."
        if not target.exists():
            return "FAILED: file was not created on disk."
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual == result.get("sha256"):
            return "Measured: file re-read from disk; sha256 matches what was written."
        return "FAILED: file content hash does not match after write."

    return verify


def build_file_tools(registry, workspace: str | Path, verifier=None) -> Path:
    """Register the sandboxed file tools and (optionally) their verifier contracts.

    The workspace folder is created if missing. Returns the resolved workspace path so
    callers (and tests) know exactly where the sandbox lives.
    """
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)

    registry.register(
        Tool(
            name="files.list",
            risk="LOW",
            description="List the files and folders inside a workspace folder. Read-only.",
            func=_make_list(root),
            input_schema=_LIST_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="files.read_text",
            risk="LOW",
            description="Read a UTF-8 text file from the workspace. Read-only.",
            func=_make_read(root),
            input_schema=_READ_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="files.write_text",
            risk="MEDIUM",
            description=(
                "Create a NEW UTF-8 text file in the workspace. Never overwrites an "
                "existing file. Needs approval (MEDIUM risk)."
            ),
            func=_make_write(root),
            input_schema=_WRITE_SCHEMA,
        )
    )

    if verifier is not None:
        verifier.register("files.list", _verify_list)
        verifier.register("files.read_text", _verify_read)
        verifier.register("files.write_text", _make_verify_write(root))

    return root.resolve()
