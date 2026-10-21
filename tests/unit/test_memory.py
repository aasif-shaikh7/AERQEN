"""Tests for the agent memory store and tools (ADR-012)."""

from __future__ import annotations

import pytest

from core.memory.store import MAX_TEXT, MemoryStore
from core.verifier.checker import ContractVerifier
from tools.memory import build_memory_tools
from tools.registry import ToolError, ToolRegistry


@pytest.fixture()
def store(tmp_path):
    return MemoryStore(tmp_path / "mem.jsonl", max_entries=5)


# ----------------------------------------------------------------- store behaviour


def test_remember_and_recall(store):
    store.remember("the user prefers metric units", tags="prefs")
    store.remember("the project repo is AERQEN")
    hits = store.recall("metric")
    assert len(hits) == 1
    assert "metric units" in hits[0]["text"]


def test_recall_empty_query_returns_recent_newest_first(store):
    store.remember("first")
    store.remember("second")
    recent = store.recall("", limit=5)
    assert recent[0]["text"] == "second"  # newest first


def test_ids_increment_and_persist(tmp_path):
    path = tmp_path / "mem.jsonl"
    s1 = MemoryStore(path)
    a = s1.remember("a")
    b = s1.remember("b")
    assert (a["id"], b["id"]) == (1, 2)
    # A fresh store reading the same file keeps counting from where it left off.
    s2 = MemoryStore(path)
    c = s2.remember("c")
    assert c["id"] == 3
    assert [e["text"] for e in s2.all()] == ["a", "b", "c"]


def test_max_entries_drops_oldest(store):
    for i in range(7):  # store cap is 5
        store.remember(f"note {i}")
    texts = [e["text"] for e in store.all()]
    assert texts == ["note 2", "note 3", "note 4", "note 5", "note 6"]


def test_text_is_capped(store):
    entry = store.remember("x" * (MAX_TEXT + 500))
    assert len(entry["text"]) == MAX_TEXT


def test_empty_note_rejected(store):
    with pytest.raises(ValueError):
        store.remember("   ")


def test_corrupt_line_is_skipped(tmp_path):
    path = tmp_path / "mem.jsonl"
    path.write_text('{"id":1,"text":"good"}\nNOT JSON\n{"id":2,"text":"also good"}\n',
                    encoding="utf-8")
    store = MemoryStore(path)
    assert [e["text"] for e in store.all()] == ["good", "also good"]


# ----------------------------------------------------------------------- tools


@pytest.fixture()
def registry(store):
    reg = ToolRegistry()
    build_memory_tools(reg, store)
    return reg


def test_tools_are_low_risk(registry):
    for name in ("memory.remember", "memory.recall", "memory.list"):
        assert registry.get(name).risk == "LOW"


def test_remember_tool_then_recall_tool(registry):
    out = registry.get("memory.remember").run(text="deploy on fridays", tags="ops")
    assert out["saved"] is True and out["id"] == 1
    recalled = registry.get("memory.recall").run(query="fridays")
    assert recalled["count"] == 1
    assert "fridays" in recalled["results"][0]["text"]


def test_remember_tool_rejects_empty(registry):
    with pytest.raises(ToolError):
        registry.get("memory.remember").run(text="")


def test_memory_verifier_contracts(store):
    reg = ToolRegistry()
    verifier = ContractVerifier()
    build_memory_tools(reg, store, verifier=verifier)

    from core.task_manager.models import Step, StepState

    result = reg.get("memory.remember").run(text="hello memory")
    step = Step(step_id=1, tool="memory.remember", input={"text": "hello memory"},
                risk="LOW", expected="remember")
    step.result = result
    step.state = StepState.SUCCEEDED
    verifier.verify(step)
    assert step.outcome.startswith("Measured:")
