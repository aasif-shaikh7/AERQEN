"""Sandboxed file tools for the agent loop (ADR-009).

These are the first tools that touch the real filesystem, so they are deliberately
small and locked down. Every path is resolved INSIDE a single workspace folder
(default ``data/workspace``); anything that points outside it -- an absolute path, a
drive letter, or a ``..`` that climbs above the root -- is rejected before any disk
access happens.

    files.list           LOW     list entries of a folder in the workspace (read-only)
    files.read_text      LOW     read a UTF-8 text file in the workspace (read-only)
    files.search         LOW     find files by name pattern and/or text content (read-only)
    files.make_dir       LOW     create a folder in the workspace
    files.write_text     MEDIUM  create a NEW text file (never overwrites an existing one)
    files.append_text    MEDIUM  add text to the end of a file (creates it if missing)
    files.overwrite_text MEDIUM  replace an existing file's content (old copy -> .trash)
    files.delete         MEDIUM  remove a file (moved to .trash, never truly destroyed)

``files.write_text`` is CREATE-ONLY on purpose: an agent can add a file but can never
silently clobber one the user already has. The two potentially destructive tools --
``files.overwrite_text`` and ``files.delete`` -- never destroy data permanently: the old
content is first moved into a ``.trash`` folder inside the workspace, so anything can be
recovered. Every mutating tool's verifier re-reads the result from disk, so the outcome
is Measured, not assumed.
"""

from __future__ import annotations

import fnmatch
import hashlib
import os
import shutil
import time
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
_APPEND_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File inside the workspace (created if missing)."},
        "content": {"type": "string", "description": "UTF-8 text to add to the end."},
    },
    "required": ["path", "content"],
}
_OVERWRITE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Existing file inside the workspace."},
        "content": {"type": "string", "description": "UTF-8 text that replaces the file."},
    },
    "required": ["path", "content"],
}
_DELETE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File inside the workspace to remove."}
    },
    "required": ["path"],
}
_MKDIR_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Folder path inside the workspace to create."}
    },
    "required": ["path"],
}
_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "name_glob": {
            "type": "string",
            "description": "Filename pattern, e.g. '*.txt'. Empty = match any name.",
        },
        "contains": {
            "type": "string",
            "description": "Only files whose text contains this substring. Empty = ignore content.",
        },
    },
    "required": [],
}

#: Cap on how many matches ``files.search`` returns.
MAX_SEARCH_RESULTS = 200


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
        # Binary write: store EXACTLY the bytes we were given (no OS newline translation),
        # so the recorded sha256 matches what the verifier re-reads from disk on Windows too.
        target.write_bytes(data)
        return {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "created": True,
        }

    return files_write_text


def _trash_dest(root: Path, rel: str, suffix: str = "") -> Path:
    """A fresh, non-colliding path inside ``<workspace>/.trash`` for a rescued file."""
    trash = root.resolve() / ".trash"
    trash.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    flat = rel.strip("/\\").replace("/", "_").replace("\\", "_") + suffix
    dest = trash / f"{stamp}_{flat}"
    i = 1
    while dest.exists():
        dest = trash / f"{stamp}_{i}_{flat}"
        i += 1
    return dest


def _make_mkdir(root: Path) -> Callable[..., dict[str, Any]]:
    def files_make_dir(path: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if target.exists() and not target.is_dir():
            raise ToolError(f"A file already exists at that path: {path!r}")
        existed = target.is_dir()
        target.mkdir(parents=True, exist_ok=True)
        return {"path": path, "created": not existed}

    return files_make_dir


def _make_append(root: Path) -> Callable[..., dict[str, Any]]:
    def files_append_text(path: str, content: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if target.exists() and not target.is_file():
            raise ToolError(f"Not a file: {path!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        # Binary append: add exactly these bytes, no newline translation.
        with target.open("ab") as fh:
            fh.write(content.encode("utf-8"))
        data = target.read_bytes()
        return {
            "path": path,
            "appended_bytes": len(content.encode("utf-8")),
            "total_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    return files_append_text


def _make_overwrite(root: Path) -> Callable[..., dict[str, Any]]:
    def files_overwrite_text(path: str, content: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if not target.exists() or not target.is_file():
            raise ToolError(
                f"No such file to overwrite: {path!r} (use files.write_text to create it)."
            )
        # Rescue the previous version before replacing it -- nothing is ever lost.
        backup = _trash_dest(root, path, suffix=".bak")
        shutil.copy2(str(target), str(backup))
        data = content.encode("utf-8")
        target.write_bytes(data)  # exact bytes, no newline translation
        return {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "backup": str(backup.relative_to(root.resolve())).replace("\\", "/"),
        }

    return files_overwrite_text


def _make_delete(root: Path) -> Callable[..., dict[str, Any]]:
    def files_delete(path: str) -> dict[str, Any]:
        target = _safe_path(root, path)
        if not target.exists():
            raise ToolError(f"No such file in workspace: {path!r}")
        if not target.is_file():
            raise ToolError(f"Only files can be deleted, not folders: {path!r}")
        dest = _trash_dest(root, path)
        shutil.move(str(target), str(dest))
        return {
            "path": path,
            "deleted": True,
            "moved_to_trash": str(dest.relative_to(root.resolve())).replace("\\", "/"),
        }

    return files_delete


def _make_search(root: Path) -> Callable[..., dict[str, Any]]:
    def files_search(name_glob: str = "", contains: str = "") -> dict[str, Any]:
        root_r = root.resolve()
        matches: list[str] = []
        for p in sorted(root_r.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root_r)).replace("\\", "/")
            if rel == ".gitkeep" or rel.startswith(".trash/"):
                continue  # never surface the rescue bin or the git placeholder
            if name_glob and not fnmatch.fnmatch(p.name, name_glob):
                continue
            if contains:
                try:
                    if contains not in p.read_text(encoding="utf-8", errors="replace"):
                        continue
                except OSError:
                    continue
            matches.append(rel)
            if len(matches) >= MAX_SEARCH_RESULTS:
                break
        return {
            "name_glob": name_glob or None,
            "contains": contains or None,
            "count": len(matches),
            "matches": matches,
        }

    return files_search


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


def _verify_search(step) -> str:
    result = step.result or {}
    if "matches" in result:
        return f"Measured: {result.get('count', 0)} file(s) matched."
    return "FAILED: files.search returned no matches field."


def _resolve_or_fail(root: Path, step):
    """Helper for the hash/existence contracts. Returns (target, None) or (None, verdict)."""
    rel = (step.input or {}).get("path")
    if not rel:
        return None, "FAILED: no path recorded."
    try:
        return _safe_path(root, rel), None
    except ToolInputError:
        return None, "FAILED: recorded path is outside the workspace."


def _make_verify_hash(root: Path, action: str) -> Callable[..., str]:
    """Contract for tools that end with a known file whose sha256 we recorded."""

    def verify(step) -> str:
        target, bad = _resolve_or_fail(root, step)
        if bad:
            return bad
        if not target.exists():
            return f"FAILED: file is missing after {action}."
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual == (step.result or {}).get("sha256"):
            return f"Measured: file re-read from disk; sha256 matches after {action}."
        return f"FAILED: file content hash does not match after {action}."

    return verify


def _make_verify_delete(root: Path) -> Callable[..., str]:
    def verify(step) -> str:
        target, bad = _resolve_or_fail(root, step)
        if bad:
            return bad
        if target.exists():
            return "FAILED: file is still present after delete."
        return "Measured: file removed from its path (moved to .trash)."

    return verify


def _make_verify_mkdir(root: Path) -> Callable[..., str]:
    def verify(step) -> str:
        target, bad = _resolve_or_fail(root, step)
        if bad:
            return bad
        return "Measured: folder exists." if target.is_dir() else "FAILED: folder was not created."

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
            name="files.search",
            risk="LOW",
            description=(
                "Find files in the workspace by filename pattern (e.g. '*.txt') and/or by a "
                "substring of their text content. Read-only."
            ),
            func=_make_search(root),
            input_schema=_SEARCH_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="files.make_dir",
            risk="LOW",
            description="Create a folder (and any parents) inside the workspace.",
            func=_make_mkdir(root),
            input_schema=_MKDIR_SCHEMA,
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
    registry.register(
        Tool(
            name="files.append_text",
            risk="MEDIUM",
            description=(
                "Add text to the END of a file in the workspace (creates it if missing). "
                "Needs approval (MEDIUM risk)."
            ),
            func=_make_append(root),
            input_schema=_APPEND_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="files.overwrite_text",
            risk="MEDIUM",
            description=(
                "Replace the entire content of an EXISTING file. The old version is saved to "
                ".trash first, so it can be recovered. Needs approval (MEDIUM risk)."
            ),
            func=_make_overwrite(root),
            input_schema=_OVERWRITE_SCHEMA,
        )
    )
    registry.register(
        Tool(
            name="files.delete",
            risk="MEDIUM",
            description=(
                "Remove a file from the workspace. It is moved to .trash (not destroyed), so "
                "it can be recovered. Folders are not deleted. Needs approval (MEDIUM risk)."
            ),
            func=_make_delete(root),
            input_schema=_DELETE_SCHEMA,
        )
    )

    if verifier is not None:
        verifier.register("files.list", _verify_list)
        verifier.register("files.read_text", _verify_read)
        verifier.register("files.search", _verify_search)
        verifier.register("files.make_dir", _make_verify_mkdir(root))
        verifier.register("files.write_text", _make_verify_hash(root, "write"))
        verifier.register("files.append_text", _make_verify_hash(root, "append"))
        verifier.register("files.overwrite_text", _make_verify_hash(root, "overwrite"))
        verifier.register("files.delete", _make_verify_delete(root))

    return root.resolve()
