"""MemoryStore (ADR-012): a tiny durable notebook, backed by a JSONL file.

This is deliberately simple and bounded, not a vector database. Each entry is one short
note the agent chose to keep. The store:

- caps each note's length (`MAX_TEXT`) and the total number of notes (`max_entries`),
  dropping the oldest when full, so memory can never grow without limit;
- keeps notes as plain data (search is case-insensitive substring matching) so there is
  nothing opaque for a human to audit;
- is safe to read when the file is missing or a line is corrupt (bad lines are skipped).

Memory is the agent's OWN scratchpad. It is not the file sandbox and never touches the
user's workspace files.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

#: Hard cap on a single note's length, so one call cannot store a whole document.
MAX_TEXT = 1000


class MemoryStore:
    def __init__(self, path: str | Path = "data/memory/memory.jsonl", max_entries: int = 200) -> None:
        self.path = Path(path)
        self.max_entries = max(1, int(max_entries))

    # ------------------------------------------------------------------ reading

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        entries: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # skip a corrupt line rather than crash
            if isinstance(obj, dict) and "text" in obj:
                entries.append(obj)
        return entries

    def all(self) -> list[dict[str, Any]]:
        """Every note, oldest first."""
        return self._load()

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """The most recent notes, newest first."""
        limit = max(1, int(limit))
        return list(reversed(self._load()))[:limit]

    def recall(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Notes relevant to ``query`` (case-insensitive keyword match), newest first.

        A note matches if the whole query is a substring of it, OR if any meaningful word
        (3+ letters) of the query appears in it. This keeps a natural-language question like
        "who is the user named Aasif?" matching a note that says "the user's name is Aasif".
        An empty query returns the most recent notes, so "what do you remember?" works.
        """
        limit = max(1, int(limit))
        q = (query or "").strip().lower()
        newest_first = list(reversed(self._load()))
        if not q:
            return newest_first[:limit]

        words = {w.strip("?.,!:;\"'()") for w in q.split()}
        words = {w for w in words if len(w) >= 3}
        hits = []
        for e in newest_first:
            haystack = (str(e.get("text", "")) + " " + str(e.get("tags", ""))).lower()
            if q in haystack or any(w in haystack for w in words):
                hits.append(e)
            if len(hits) >= limit:
                break
        return hits

    # ------------------------------------------------------------------ writing

    def remember(self, text: str, tags: str = "") -> dict[str, Any]:
        """Append a note and return it. Enforces the length and count caps."""
        text = (text or "").strip()
        if not text:
            raise ValueError("cannot remember an empty note")
        if len(text) > MAX_TEXT:
            text = text[:MAX_TEXT]

        entries = self._load()
        next_id = (max((int(e.get("id", 0)) for e in entries), default=0)) + 1
        entry = {
            "id": next_id,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "text": text,
            "tags": (tags or "").strip(),
        }
        entries.append(entry)
        # Keep only the newest ``max_entries`` notes.
        if len(entries) > self.max_entries:
            entries = entries[-self.max_entries :]

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        return entry

    def count(self) -> int:
        return len(self._load())
