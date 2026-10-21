# AERQEN — To-do List

**Document:** `todo-list.md`  
**Status:** Active — the single work queue. Nothing is started that is not on it.  
**Owner of priority:** The project owner. This document orders and describes; it does not decide.  
**Current stage:** Phase 0 — Specification and Feasibility

---

## How to read this

Six sections define the queue.

| § | Section | What belongs in it |
|---|---|---|
| 1 | **Critical** | Work that blocks the first usable AERQEN milestone. |
| 2 | **Errors and bugs** | Something is wrong in an implemented feature. |
| 3 | **Features** | New capability that can be built and tested independently. |
| 4 | **Working now** | Functionality actually implemented and verified. |
| 5 | **Pending scope** | Agreed future direction that is not yet started. |
| 6 | **Owner's list** | New requirements supplied by the project owner. |

Every entry has an ID such as `CRIT-1`, `BUG-1`, or `FEAT-1`.

### Evidence vocabulary

- **Measured** — actually tested and observed, with the result recorded.
- **Reported** — the project owner observed it, but it has not been independently reproduced.
- **Reasoned** — supported by documented technical reasoning, but not yet observed.
- **Unverified** — intended or believed, with no test evidence yet.

### Phase vocabulary

| Phase | Meaning |
|---|---|
| `pending` | Not started. |
| `building` | Currently being implemented. |
| `testing` | Implemented and waiting for actual test execution. |
| `superseded` | Replaced by a better decision; retained for history. |
| `done` | Acceptance criteria passed and evidence recorded in `done-list.md`. |
| `blocked` | Cannot proceed until a named dependency/decision is resolved. |

An item is never deleted merely to make the queue look shorter.

**Anything new is recorded here first.** Requirements, bugs, ideas, and technical discoveries receive an ID before implementation.

---

## State of the queue — Phase 0

| Phase | Items |
|---|---|
| `done` | `CRIT-1`..`CRIT-6` — documentation/specification established; `CRIT-8` — skeleton pipeline accepted (owner-verified, 4 tests passed); `FEAT-1`, `FEAT-2`, `FEAT-3`, `FEAT-4`, `FEAT-5`, `FEAT-6`, `FEAT-7`, `FEAT-9`, `FEAT-11` — safety-gate foundation (owner accepted 2026-10-21); `LLM-1` (agent loop + Ollama) and `FEAT-13` (sandboxed file tools) — owner accepted 2026-10-21. See `done-list.md`. |
| `testing` | `FEAT-17` agent memory (ADR-012): durable JSONL notebook + remember/recall/list tools + auto-recall; `UI-1` local web chat (ADR-013): browser chat for PC + phone, token-gated, web approvals — 83 tests pass + live HTTP demo (2026-10-21), owner acceptance pending |
| `building` | `CRIT-7` (decisions recorded; dev environment setup still in progress) |
| `pending` | Phase 1 dev environment install + acceptance gate; `FEAT-8` (real observation, Phase 3) |
| `blocked` | Public brand/legal clearance before commercial launch |
| `superseded` | — |

---

# 1. Critical

## `CRIT-1` — Freeze the product requirements

**Phase:** `done`

The product definition must clearly establish AERQEN as a general-purpose AI Computer Employee rather than a single-purpose chatbot or automation script.

**Source:** `PRD.md`

**Acceptance:** Product scope, goals, non-goals, UX, success criteria, and quality requirements are documented.

---

## `CRIT-2` — Establish the modular architecture

**Phase:** `done`

AERQEN must separate reasoning, planning, tools, execution, observation, verification, recovery, memory, security, logging, and UI.

**Source:** `ARCHITECTURE.md`

**Acceptance:** Responsibilities and boundaries are documented before implementation begins.

---

## `CRIT-3` — Establish the security model

**Phase:** `done`

AERQEN must not become unrestricted computer-control software merely because a capability is technically possible.

**Source:** `SECURITY.md`

**Acceptance:** Risk levels, approvals, secrets handling, computer-control safety, code execution rules, and incident response are documented.

---

## `CRIT-4` — Establish one-person development and testing rules

**Phase:** `done`

The project has one human developer/operator assisted by AI.

The human remains responsible for decisions, approvals, secrets, actual test execution, and release acceptance.

**Source:** `DEVELOPMENT_AND_TESTING.md`

---

## `CRIT-5` — Establish AI development rules

**Phase:** `done`

Any AI working on the repository must read the project documents before coding, preserve working architecture, avoid invented test claims, make small changes, and provide exact testing instructions.

**Source:** `AI_DEVELOPMENT_GUIDE.md`

---

## `CRIT-6` — Establish a phase-gated roadmap

**Phase:** `done`

Development must proceed through explicit phases and must not jump to advanced autonomy before the underlying tools, security, observation, and verification systems are stable.

**Source:** `ROADMAP.md`

---

## `CRIT-7` — Complete Phase 0 feasibility review

**Phase:** `building`

Before substantial coding:
- inspect the target Windows environment
- select the initial technology stack
- identify required external services
- decide what can run locally
- identify optional dependencies
- define the minimum executable prototype
- identify technical unknowns that must be tested before architecture is locked

**Recorded (owner-approved):** Full technology selection is now documented in
`TECHNOLOGY_SELECTION.md` and `ARCHITECTURE_DECISION_LOG.md` (ADR-004 .. ADR-008).
No section remains an open `TBD`.

**Still open:** the actual development environment (Windows 11 VM, Ollama, Python libs)
must be installed and verified by the owner using `VM_SETUP_GUIDE.md` and
`OLLAMA_SETUP_GUIDE.md`. This part stays `pending` until the owner records it.
**Environment status on the dev machine (Measured 2026-09-03(:**
- `Python 3.12.10` — installed and verified (`python --version`..
- `pytest` (9.1.1) — installed;; the acceptance-gate commands re-run green:
  - `python -m pytest tests -q` -> **5 passed** (0.04s..
  - `python -m app.entrypoint.cli "echo hello aerqen"` -> state `done`.
  - `python -m app.entrypoint.cli "open office"` -> state `failed` (honest unsupported-command handling..
- `Ollama` `0.33.2` — installed via `winget`;; **Measured:** `ollama --version` -> `version is 0.33.2`.
- Model `qwen2.5:7b` (4.7 GB) — downloaded;; **Measured:** `ollama list` lists it. AI-reply test
  (`ollama run qwen2.5:7b`) -> `12` (measured;; non-interactive run(.
- `VirtualBox` `7.2.16r174877` — installed via `winget`;; **Measured:** `VBoxManage.exe --version` -> `7.2.16r174877`.
- VM `AERQEN-Win11` — created + configured via `VBoxManage`;; **Measured:** `.vbox` XML shows EFI, TPM 2.0,
  ️4096 MB RAM,  ️4 CPUs, NAT, SATA controller + 50 GB disk + DVD slot attached. Secure Boot is not
  exposed by this VirtualBox build (known limitation;; Windows 11 setup proceeds via registry bypass(.
- Windows  ️11 ISO download — **owner action pending** (official Microsoft route, ~6 GB;; attach to the VM per `VM_SETUP_GUIDE.md` and run Windows setup(; VM already created+configured(.

**Rule:** Unknowns are experiments, not assumptions.

---

## `CRIT-8` — Define the first executable milestone

**Phase:** `done`

The Phase 1 skeleton pipeline is implemented and **accepted by the owner on 2026-08-23**. Measured evidence:

```text
python -m app.entrypoint.cli "echo hello aerqen"
  -> state : done
  -> outcome : Measured: tool returned the exact message.

python -m pytest tests -q
  -> 4 passed

python -m app.entrypoint.cli "open office"
  -> state : failed  (honest unsupported-command handling)
```

The core loop is proven:

```text
Task → Understand → Plan → Policy Check → Execute → Observe → Verify → Report
```

Run it with:

```text
python -m app.entrypoint.cli "echo hello aerqen"
```

No unrestricted computer control is required for this milestone.

---

# 2. Errors and bugs

### `BUG-1` — Pipeline crashes (AttributeError( at the policy gate on a CONFIRM/BLOCK step

**Phase:** `done` (fixed + tests pass; awaiting owner acceptance(.



**Reproduction (Measured 2026-09-03(:** A plan containing a MEDIUM or HIGH-risk step enters
the policy-gate path, which calls ``self._describe_policy_gate(...)`` — a method that was never
defined. Reproduced by injecting a HIGH-risk step:

```text
CRASH: AttributeError 'Pipeline' object has no attribute '_describe_policy_gate'
```

**Expected:** the task reports ``blocked`` with a clear ``BLOCKED: ...`` / ``CONFIRM: ...`` summary — no crash.
**Actual (measured):** ``AttributeError: 'Pipeline' object has no attribute '_describe_policy_gate'``.
**Suspected cause:** naming mismatch:the call site uses ``_describe_policy_gate``; the definition was
written as ``_policy_gate_summary``.
**Fix (implemented):** renamed the definition to ``_describe_policy_gate`` (one-line change; smallest possible(.
**Regression test:** ``test_high_risk_step_reports_blocked_without_crash`` in ``tests/unit/test_pipeline.py``.



**Evidence:** `python -m pytest tests -q` -> **5 passed** (was 4(.

When the first implementation begins, every real failure must receive a `BUG-*` ID and include:
- reproduction steps
- expected result
- actual result
- evidence
- suspected cause
- fix
- regression test

---

# 3. Features

## `FEAT-1` — Core task model

**Phase:** `done`

Create a structured representation of a user task, its state, inputs, outputs, permissions, and result.

**Implemented:** `core/task_manager/models.py` (`Task`, `Step`, state enums). Covered by unit tests.

---

## `FEAT-2` — Brain interface

**Phase:** `done`

Convert natural-language input into structured task understanding without directly executing computer actions.

**Implemented:** `core/brain/interface.py` + `core/brain/mock.py` (deterministic MVP brain). Real LLM brain is deferred to the Ollama integration.

---

## `FEAT-3` — Planner

**Phase:** `done`

Create explicit, inspectable plans with steps, dependencies, required tools, and expected outcomes.

**Implemented:** `core/planner/interface.py` + `core/planner/naive.py`. Covered by unit tests.

---

## `FEAT-4` — Tool registry

**Phase:** `done`

Create a controlled registry describing what each tool can do, its inputs, risk level, permissions, and output.

**Implemented:** `tools/registry.py` (Tool/ToolRegistry) + `tools/demo.py`. Covered by unit tests.

**2026-10-21:** every tool now declares an input schema, and `Tool.run` rejects unknown, missing or wrongly typed
parameters. The declared risk is validated and is authoritative (ADR-009). Tests: `tests/security/test_safety_gates.py`.

---

## `FEAT-5` — Security policy engine

**Phase:** `done`

Evaluate actions before execution and decide:

```text
ALLOW
CONFIRM
BLOCK
```

**Implemented:** `security/policy/policy.py` (PolicyEngine). HIGH risk defaults to BLOCK
for the MVP; CONFIRM steps go to the approval gate (FEAT-6).
Covered by unit tests.

**2026-10-21:** `PolicyEngine.decide_step` resolves the effective risk as max(planner, tool). Unknown tools
and unrecognised risk labels are BLOCKed (ADR-009, proposed).

---

## `FEAT-6` — Approval system

**Phase:** `done`

Provide human approval gates for high-impact actions.

**Implemented (2026-10-21):** `security/approvals/approver.py`: `DenyAllApprover` (default) and `CliApprover`
(terminal y/N; only an explicit y/yes approves, and EOF means no). The pipeline asks before anything runs.
A BLOCK step is never offered for approval.
**Try it:** `python -m app.entrypoint.cli "guarded echo hello"`, then answer `y` (expected `done`) or press Enter (expected `blocked`).
**Limitation:** CLI only. There is no web UI yet, and HIGH stays BLOCK (SECURITY.md lets HIGH run with explicit
confirmation; enabling that is a separate owner decision).

---

## `FEAT-7` — Executor

**Phase:** `done`

Execute approved tool actions and return structured results.

**Implemented:** `core/executor/interface.py` + `core/executor/simple.py`. Covered by unit tests.

---

## `FEAT-8` — Observation layer

**Phase:** `pending`

Observe relevant application/computer state after actions.

**Phase note:** The MVP's observation equals the tool's returned result (Executor output).
Real screen/window-state observation (pywinauto + screen capture, per ADR-007) is a Phase 3
capability and remains `pending`. FEAT-7 covers result capture for now.

---

## `FEAT-9` — Verification engine

**Phase:** `done`

Determine whether an action actually achieved its intended result.

**Implemented:** `core/verifier/interface.py` + `core/verifier/checker.py` (ContractVerifier).
Covered by unit tests.

---

## `FEAT-10` — Recovery engine

**Phase:** `pending`

Classify failures and perform bounded recovery attempts before safely stopping.

---

## `FEAT-11` — Audit logging

**Phase:** `done`

**Implemented (2026-10-21):** `security/audit/log.py` writes JSONL to `data/logs/audit.jsonl` (gitignored).
Secret-looking keys are redacted, strings are truncated to 200 characters, and writing is fail-closed.
**Limitation:** no rotation or retention policy yet.

Record important decisions, approvals, actions, failures, and results without exposing secrets.

---

## `FEAT-12` — Basic computer-control tools

**Phase:** `pending`

Introduce controlled mouse, keyboard, window, and screen capabilities only after the security and verification foundations exist.

---

## `FEAT-13` — File/document tools

**Phase:** `done` (create-only subset, ADR-010; mutation + search extension ADR-011 — owner accepted 2026-10-21)

First sandboxed file tools shipped and accepted (ADR-010): `files.list` / `files.read_text` (LOW)
and `files.write_text` (MEDIUM, create-only), confined to `AERQEN_WORKSPACE`. Traversal, absolute
paths and drive letters are rejected; the write verifier re-reads and compares sha256.

Extension in `testing` (ADR-011, owner acceptance pending): `files.search` + `files.make_dir`
(LOW) and `files.append_text` / `files.overwrite_text` / `files.delete` (MEDIUM). Destructive
actions are recoverable — delete and overwrite route the old content into a workspace `.trash`
folder. Writes store exact bytes (no newline translation). Still pending for a later pass:
binary/document formats (PDF/Office), `.trash` auto-purge, and full version history.

**Implemented:** `tools/files.py`, verifier contracts in `core/verifier/checker.py`,
tests in `tests/unit/test_files.py` and `tests/unit/test_agent_loop.py`.

---

## `LLM-1` — LLM agent loop (Ollama)

**Phase:** `done`

The first real agent: a model picks one tool per turn and each turn passes the shared safety
gates (`core/runner.py`), with untrusted tool output and a bounded step budget (ADR-005/ADR-010).

**Implemented:** `integrations/ai/provider.py`, `integrations/ai/ollama.py`, `core/agent/loop.py`,
`core/runner.py` (shared by the refactored `core/pipeline.py`), `--agent` flag in
`app/entrypoint/cli.py`, settings in `app/configuration/settings.py`, tests in
`tests/unit/test_agent_loop.py`.

**Evidence (Measured, 2026-10-21):** 52 tests pass (51 fake-provider + 1 live Ollama); a live run
created a file via `files.write_text` after approval with a matching sha256, and the same write
was `blocked` when no one approved.

---

## `FEAT-14` — Browser agent

**Phase:** `pending`

Add browser navigation and interaction with authentication, CAPTCHA, privacy, and data-transfer safeguards.

---

## `FEAT-15` — Office automation

**Phase:** `pending`

Add document, spreadsheet, and presentation workflows.

---

## `FEAT-16` — Coding agent

**Phase:** `pending`

Inspect projects, generate code, run tests, diagnose errors, and create controlled patches.

---

## `FEAT-17` — Memory

**Phase:** `testing` (first version, ADR-012)

First durable memory shipped (ADR-012): a bounded JSONL notebook (`core/memory/store.py`) plus
`memory.remember` / `memory.recall` / `memory.list` tools (LOW), with auto-recall into the prompt
at the start of each task. Retention is a size cap (oldest dropped). Still pending for a later
pass: per-user/project scoping, secret redaction in notes, and smarter (embedding) recall.

**Implemented:** `core/memory/store.py`, `tools/memory.py`, auto-recall in `core/agent/loop.py`,
settings in `app/configuration/settings.py`, tests in `tests/unit/test_memory.py` and
`tests/unit/test_agent_loop.py`.

---

## `FEAT-18` — Specialist integrations

**Phase:** `pending`

Add specialist modules such as Revit, AutoCAD, engineering workflows, or other applications without changing the core architecture.

---

## `FEAT-19` — Long-running workflows

**Phase:** `pending`

Only after reliability and recovery are established.

---

## `FEAT-20` — Advanced autonomy

**Phase:** `pending`

Scheduled tasks, multi-agent workflows, and broader autonomous execution are explicitly late-stage capabilities.

---

# 4. Working now

No runtime feature is claimed as working yet.

The following are established documentation artifacts:

- `PRD.md`
- `ARCHITECTURE.md`
- `FOLDER_STRUCTURE.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `ROADMAP.md`
- `DEVELOPMENT_AND_TESTING.md`
- `AI_DEVELOPMENT_GUIDE.md`
- `AERQEN_BRAND_GUIDE.md`
- `GLOSSARY.md`
- `CONTRIBUTING.md`
- `ARCHITECTURE_DECISION_LOG.md`
- `TECHNOLOGY_SELECTION.md`
- `README.md`
- `todo-list.md`
- `done-list.md`
- `CHANGELOG.md`

These are documentation deliverables, not proof that the application itself works.

---

# 5. Pending scope

The following are intentionally deferred until the core is proven:

- multi-agent collaboration
- autonomous scheduling
- advanced computer vision
- autonomous external communication
- autonomous financial actions
- unrestricted system administration
- cloud backend
- commercial distribution
- public app-store release

---

# 6. Owner's list

Reserved for new requirements supplied by the project owner.

New requirements must be added here before implementation.

---

## Queue rules

1. Do not build work that is not listed.
2. Do not mark work `done` because code compiles.
3. Do not mark work `done` because an AI says it should work.
4. A real test result is required.
5. Regression testing is required after meaningful changes.
6. If a new discovery changes architecture, record it before coding around it.
7. If the owner changes scope, update the queue and roadmap rather than silently changing implementation.
