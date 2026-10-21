"""Tests for the LLM agent loop (ADR-005 / ADR-009).

A :class:`FakeProvider` stands in for the model so the loop can be tested without Ollama:
it replays a scripted list of replies. One live test at the end actually talks to Ollama
and is skipped automatically when Ollama is not running.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.agent.loop import AgentLoop
from core.executor.simple import SimpleExecutor
from core.runner import StepRunner
from core.task_manager.models import Task, TaskState
from core.verifier.checker import ContractVerifier
from integrations.ai.provider import LLMProvider, LLMReply, ToolCall
from security.approvals.approver import Approver, DenyAllApprover
from security.audit.log import MemoryAuditLog
from security.policy.policy import PolicyEngine
from tools.files import build_file_tools
from tools.registry import Tool, ToolRegistry


# ----------------------------------------------------------------- test doubles


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, replies: list[LLMReply], available: bool = True) -> None:
        self._replies = list(replies)
        self._available = available
        self.calls: list[tuple[list[dict[str, Any]], list[dict[str, Any]]]] = []

    def is_available(self) -> bool:
        return self._available

    def chat(self, messages, tools) -> LLMReply:
        self.calls.append((list(messages), tools))
        if not self._replies:
            return LLMReply(content="(no more scripted replies)")
        return self._replies.pop(0)


class AllowApprover(Approver):
    def approve(self, step) -> bool:
        return True


def _call(model_tool: str, **args) -> LLMReply:
    return LLMReply(tool_calls=[ToolCall(name=model_tool, arguments=dict(args))])


def _build_agent(tmp_path, replies, approver=None, max_steps=8, extra_tools=None):
    registry = ToolRegistry()
    verifier = ContractVerifier()
    build_file_tools(registry, tmp_path, verifier=verifier)
    for tool in extra_tools or []:
        registry.register(tool)
    audit = MemoryAuditLog()
    runner = StepRunner(
        registry=registry,
        policy=PolicyEngine(),
        executor=SimpleExecutor(registry),
        verifier=verifier,
        approver=approver or DenyAllApprover(),
        audit=audit,
    )
    provider = FakeProvider(replies)
    agent = AgentLoop(provider=provider, runner=runner, max_steps=max_steps)
    return agent, provider, audit, tmp_path


# ----------------------------------------------------------------------- tests


def test_final_answer_with_no_tools(tmp_path):
    agent, provider, audit, _ = _build_agent(
        tmp_path, [LLMReply(content="nothing to do here")]
    )
    task = Task(task_id="t1", description="say hi")
    agent.run(task)
    assert task.state is TaskState.DONE
    assert task.answer == "nothing to do here"
    assert task.plan == []
    assert "agent_final_answer" in audit.names()


def test_agent_writes_file_after_approval(tmp_path):
    replies = [
        _call("files_write_text", path="out.txt", content="hello world"),
        LLMReply(content="I created out.txt for you."),
    ]
    agent, provider, audit, ws = _build_agent(tmp_path, replies, approver=AllowApprover())
    task = Task(task_id="t2", description="write hello world to out.txt")
    agent.run(task)

    assert task.state is TaskState.DONE
    assert task.answer == "I created out.txt for you."
    assert (ws / "out.txt").read_text(encoding="utf-8") == "hello world"
    # The full gate sequence was audited for the MEDIUM-risk write.
    names = audit.names()
    for expected in ("policy_decision", "approval", "step_execute", "step_result"):
        assert expected in names
    assert task.plan[0].outcome.startswith("Measured:")


def test_write_is_blocked_when_approval_denied(tmp_path):
    replies = [_call("files_write_text", path="out.txt", content="x")]
    agent, provider, audit, ws = _build_agent(tmp_path, replies, approver=DenyAllApprover())
    task = Task(task_id="t3", description="write a file")
    agent.run(task)

    assert task.state is TaskState.BLOCKED
    assert not (ws / "out.txt").exists()
    approval_events = [e for e in audit.events if e["event"] == "approval"]
    assert approval_events and approval_events[0]["approved"] is False


def test_unknown_tool_is_fed_back_not_executed(tmp_path):
    replies = [
        _call("do_some_magic", target="world"),
        LLMReply(content="okay, I will stop"),
    ]
    agent, provider, audit, _ = _build_agent(tmp_path, replies)
    task = Task(task_id="t4", description="do magic")
    agent.run(task)

    assert task.state is TaskState.DONE
    assert "agent_unknown_tool" in audit.names()
    # The second model call saw the error fed back as an untrusted tool message.
    second_messages = provider.calls[1][0]
    tool_msgs = [m for m in second_messages if m["role"] == "tool"]
    assert tool_msgs and "unknown tool" in tool_msgs[-1]["content"]


def test_bad_input_is_fed_back_then_corrected(tmp_path):
    replies = [
        _call("files_write_text", path="a.txt"),  # missing required 'content'
        _call("files_write_text", path="a.txt", content="fixed"),
        LLMReply(content="done, file written"),
    ]
    agent, provider, audit, ws = _build_agent(tmp_path, replies, approver=AllowApprover())
    task = Task(task_id="t5", description="write a.txt")
    agent.run(task)

    assert task.state is TaskState.DONE
    assert (ws / "a.txt").read_text(encoding="utf-8") == "fixed"
    assert len(provider.calls) == 3


def test_agent_reads_then_summarizes(tmp_path):
    # A read-only "read this file and tell me about it" flow: LOW tool, no approval.
    (tmp_path / "data.txt").write_text("apples oranges bananas", encoding="utf-8")
    replies = [
        _call("files_read_text", path="data.txt"),
        LLMReply(content="The file lists three fruits: apples, oranges and bananas."),
    ]
    agent, provider, audit, _ = _build_agent(tmp_path, replies, approver=DenyAllApprover())
    task = Task(task_id="t-sum", description="read data.txt and summarize it")
    agent.run(task)

    assert task.state is TaskState.DONE
    assert "fruits" in task.answer
    # A LOW read never triggers an approval prompt.
    assert "approval" not in audit.names()
    assert task.plan[0].tool == "files.read_text"
    assert task.plan[0].outcome.startswith("Measured:")


def test_reaching_step_budget_fails(tmp_path):
    replies = [_call("files_list", path=".") for _ in range(5)]
    agent, provider, audit, _ = _build_agent(tmp_path, replies, max_steps=2)
    task = Task(task_id="t6", description="keep listing")
    agent.run(task)

    assert task.state is TaskState.FAILED
    assert "budget" in (task.error or "")
    assert "agent_max_steps" in audit.names()


def test_high_risk_tool_is_blocked(tmp_path):
    danger = Tool(
        name="danger.wipe",
        risk="HIGH",
        description="pretend-dangerous tool (never actually runs in tests)",
        func=lambda: {"done": True},
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    replies = [_call("danger_wipe")]
    agent, provider, audit, _ = _build_agent(
        tmp_path, replies, approver=AllowApprover(), extra_tools=[danger]
    )
    task = Task(task_id="t7", description="wipe everything")
    agent.run(task)

    assert task.state is TaskState.BLOCKED
    # Policy was consulted and the step was never executed.
    assert "policy_decision" in audit.names()
    assert "step_execute" not in audit.names()


def test_memory_is_recalled_into_the_prompt(tmp_path):
    from core.memory.store import MemoryStore

    mem = MemoryStore(tmp_path / "mem.jsonl")
    mem.remember("the user's name is Aasif", tags="profile")

    registry = ToolRegistry()
    verifier = ContractVerifier()
    build_file_tools(registry, tmp_path, verifier=verifier)
    audit = MemoryAuditLog()
    runner = StepRunner(registry, PolicyEngine(), SimpleExecutor(registry), verifier,
                        DenyAllApprover(), audit)
    provider = FakeProvider([LLMReply(content="Hi Aasif!")])
    agent = AgentLoop(provider=provider, runner=runner, memory=mem, memory_recall=5)

    task = Task(task_id="t-mem", description="who is the user named Aasif?")
    agent.run(task)

    # The saved note was injected as a system context message before the model ran.
    system_msgs = [m for m in provider.calls[0][0] if m["role"] == "system"]
    assert any("Aasif" in m["content"] for m in system_msgs)
    assert "agent_memory_recall" in audit.names()


def test_no_memory_means_no_recall_block(tmp_path):
    # Agent without a memory store must still work and inject no recall block.
    agent, provider, audit, _ = _build_agent(tmp_path, [LLMReply(content="ok")])
    task = Task(task_id="t-nomem", description="hello")
    agent.run(task)
    system_msgs = [m for m in provider.calls[0][0] if m["role"] == "system"]
    assert len(system_msgs) == 1  # only the base system prompt
    assert "agent_memory_recall" not in audit.names()


def test_llm_unavailable_fails_cleanly(tmp_path):
    registry = ToolRegistry()
    verifier = ContractVerifier()
    build_file_tools(registry, tmp_path, verifier=verifier)
    runner = StepRunner(registry, PolicyEngine(), SimpleExecutor(registry), verifier,
                        DenyAllApprover(), MemoryAuditLog())
    agent = AgentLoop(provider=FakeProvider([], available=False), runner=runner)
    task = Task(task_id="t8", description="anything")
    agent.run(task)
    assert task.state is TaskState.FAILED
    assert "not reachable" in (task.error or "")


# -------------------------------------------------------------- live Ollama test


def _ollama_or_skip():
    from app.configuration.settings import load_settings
    from integrations.ai.ollama import OllamaProvider

    settings = load_settings()
    provider = OllamaProvider(
        base_url=settings.ollama_url, model=settings.ollama_model, timeout=settings.llm_timeout
    )
    if not provider.is_available():
        pytest.skip("Ollama is not running; skipping live model test.")
    return provider


@pytest.mark.live
def test_live_agent_writes_a_file(tmp_path):
    provider = _ollama_or_skip()
    registry = ToolRegistry()
    verifier = ContractVerifier()
    build_file_tools(registry, tmp_path, verifier=verifier)
    runner = StepRunner(registry, PolicyEngine(), SimpleExecutor(registry), verifier,
                        AllowApprover(), MemoryAuditLog())
    agent = AgentLoop(provider=provider, runner=runner, max_steps=6)

    task = Task(
        task_id="live1",
        description=(
            "Create a text file named greeting.txt in the workspace containing exactly: "
            "Hello from AERQEN. Then tell me you are done."
        ),
    )
    agent.run(task)
    assert task.state in (TaskState.DONE, TaskState.BLOCKED, TaskState.FAILED)
    # If it finished, the file must really exist (verifier re-read it).
    if task.state is TaskState.DONE and task.plan:
        assert (tmp_path / "greeting.txt").exists()
