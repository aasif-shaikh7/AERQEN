"""Tests for the sandboxed file tools (ADR-009).

These prove the two security promises: nothing escapes the workspace folder, and
``files.write_text`` never overwrites an existing file.
"""

from __future__ import annotations

import pytest

from core.verifier.checker import ContractVerifier
from tools.files import build_file_tools
from tools.registry import ToolError, ToolInputError, ToolRegistry


@pytest.fixture()
def registry(tmp_path):
    reg = ToolRegistry()
    build_file_tools(reg, tmp_path)
    return reg


def test_registers_three_tools_with_expected_risk(tmp_path):
    reg = ToolRegistry()
    build_file_tools(reg, tmp_path)
    assert reg.get("files.list").risk == "LOW"
    assert reg.get("files.read_text").risk == "LOW"
    assert reg.get("files.write_text").risk == "MEDIUM"


def test_write_then_read_then_list(registry):
    out = registry.get("files.write_text").run(path="notes/hello.txt", content="hi there")
    assert out["created"] is True
    assert out["bytes"] == len("hi there".encode("utf-8"))

    read = registry.get("files.read_text").run(path="notes/hello.txt")
    assert read["content"] == "hi there"
    assert read["truncated"] is False

    listing = registry.get("files.list").run(path="notes")
    names = [e["name"] for e in listing["entries"]]
    assert "hello.txt" in names


def test_write_is_create_only(registry):
    registry.get("files.write_text").run(path="a.txt", content="first")
    with pytest.raises(ToolError):
        registry.get("files.write_text").run(path="a.txt", content="second")
    # The original content is untouched.
    assert registry.get("files.read_text").run(path="a.txt")["content"] == "first"


@pytest.mark.parametrize(
    "bad",
    ["../outside.txt", "../../etc/passwd", "sub/../../up.txt", "/abs.txt", "\\abs.txt", "C:\\x.txt"],
)
def test_paths_cannot_escape_the_workspace(registry, bad):
    with pytest.raises(ToolInputError):
        registry.get("files.write_text").run(path=bad, content="x")
    with pytest.raises(ToolInputError):
        registry.get("files.read_text").run(path=bad)


def test_traversal_does_not_create_a_file_outside(tmp_path):
    reg = ToolRegistry()
    build_file_tools(reg, tmp_path / "ws")
    with pytest.raises(ToolInputError):
        reg.get("files.write_text").run(path="../escaped.txt", content="x")
    assert not (tmp_path / "escaped.txt").exists()


def test_read_missing_file_errors(registry):
    with pytest.raises(ToolError):
        registry.get("files.read_text").run(path="nope.txt")


def test_write_verifier_contract_measures_the_write(tmp_path):
    reg = ToolRegistry()
    verifier = ContractVerifier()
    root = build_file_tools(reg, tmp_path, verifier=verifier)

    # Run the write exactly as the executor would, then build a step-like object.
    from core.task_manager.models import Step, StepState

    result = reg.get("files.write_text").run(path="x.txt", content="data")
    step = Step(step_id=1, tool="files.write_text", input={"path": "x.txt", "content": "data"},
                risk="MEDIUM", expected="write")
    step.result = result
    step.state = StepState.SUCCEEDED
    verifier.verify(step)
    assert step.outcome.startswith("Measured:")

    # If the file disappears, the same contract must report FAILED.
    (root / "x.txt").unlink()
    verifier.verify(step)
    assert "FAILED" in step.outcome
