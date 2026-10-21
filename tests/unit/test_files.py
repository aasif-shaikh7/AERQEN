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


def test_make_dir_creates_folder(registry, tmp_path):
    out = registry.get("files.make_dir").run(path="reports/2026")
    assert out["created"] is True
    assert (tmp_path / "reports" / "2026").is_dir()
    # Running again is harmless and reports it already existed.
    assert registry.get("files.make_dir").run(path="reports/2026")["created"] is False


def test_append_adds_to_end(registry, tmp_path):
    registry.get("files.write_text").run(path="log.txt", content="line1\n")
    registry.get("files.append_text").run(path="log.txt", content="line2\n")
    assert registry.get("files.read_text").run(path="log.txt")["content"] == "line1\nline2\n"


def test_append_creates_when_missing(registry, tmp_path):
    registry.get("files.append_text").run(path="new.txt", content="hi")
    assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "hi"


def test_overwrite_replaces_and_backs_up(registry, tmp_path):
    registry.get("files.write_text").run(path="a.txt", content="old")
    out = registry.get("files.overwrite_text").run(path="a.txt", content="new")
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "new"
    # The previous content was rescued to .trash, not destroyed.
    backup = tmp_path / out["backup"]
    assert backup.read_text(encoding="utf-8") == "old"


def test_overwrite_requires_existing_file(registry):
    with pytest.raises(ToolError):
        registry.get("files.overwrite_text").run(path="missing.txt", content="x")


def test_delete_moves_to_trash(registry, tmp_path):
    registry.get("files.write_text").run(path="gone.txt", content="bye")
    out = registry.get("files.delete").run(path="gone.txt")
    assert not (tmp_path / "gone.txt").exists()
    # Recoverable from .trash.
    assert (tmp_path / out["moved_to_trash"]).read_text(encoding="utf-8") == "bye"


def test_delete_refuses_folders(registry, tmp_path):
    registry.get("files.make_dir").run(path="adir")
    with pytest.raises(ToolError):
        registry.get("files.delete").run(path="adir")


def test_mutating_tools_cannot_escape_workspace(registry):
    for tool in ("files.append_text", "files.overwrite_text"):
        with pytest.raises(ToolInputError):
            registry.get(tool).run(path="../evil.txt", content="x")
    with pytest.raises(ToolInputError):
        registry.get("files.delete").run(path="../evil.txt")


def test_search_by_name_and_content(registry, tmp_path):
    registry.get("files.write_text").run(path="a.txt", content="hello world")
    registry.get("files.write_text").run(path="b.txt", content="nothing here")
    registry.get("files.write_text").run(path="c.md", content="hello again")

    by_name = registry.get("files.search").run(name_glob="*.txt")
    assert set(by_name["matches"]) == {"a.txt", "b.txt"}

    by_content = registry.get("files.search").run(contains="hello")
    assert set(by_content["matches"]) == {"a.txt", "c.md"}

    both = registry.get("files.search").run(name_glob="*.txt", contains="hello")
    assert both["matches"] == ["a.txt"]


def test_search_hides_trash_and_gitkeep(registry, tmp_path):
    (tmp_path / ".gitkeep").write_text("", encoding="utf-8")
    registry.get("files.write_text").run(path="keep.txt", content="data")
    registry.get("files.delete").run(path="keep.txt")  # goes to .trash
    all_files = registry.get("files.search").run()
    assert all_files["matches"] == []  # .gitkeep and .trash are hidden


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
