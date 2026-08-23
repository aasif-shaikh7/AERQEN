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
| `done` | `CRIT-1`, `CRIT-2`, `CRIT-3`, `CRIT-4`, `CRIT-5`, `CRIT-6` — documentation/specification established; `CRIT-8` — skeleton pipeline accepted (owner-verified, 4 tests passed) |
| `testing` | `FEAT-1`, `FEAT-2`, `FEAT-3`, `FEAT-4`, `FEAT-5`, `FEAT-7`, `FEAT-9` — implemented, unit tests pass, owner acceptance pending |
| `building` | `CRIT-7` (decisions recorded; dev environment setup still in progress) |
| `pending` | Phase 1 dev environment install + acceptance gate; `FEAT-6` (approval UI, Phase 2); `FEAT-8` (real observation, Phase 3) |
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

No implementation bugs have been recorded yet.

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

**Phase:** `testing`

Create a structured representation of a user task, its state, inputs, outputs, permissions, and result.

**Implemented:** `core/task_manager/models.py` (`Task`, `Step`, state enums). Covered by unit tests.

---

## `FEAT-2` — Brain interface

**Phase:** `testing`

Convert natural-language input into structured task understanding without directly executing computer actions.

**Implemented:** `core/brain/interface.py` + `core/brain/mock.py` (deterministic MVP brain). Real LLM brain is deferred to the Ollama integration.

---

## `FEAT-3` — Planner

**Phase:** `testing`

Create explicit, inspectable plans with steps, dependencies, required tools, and expected outcomes.

**Implemented:** `core/planner/interface.py` + `core/planner/naive.py`. Covered by unit tests.

---

## `FEAT-4` — Tool registry

**Phase:** `testing`

Create a controlled registry describing what each tool can do, its inputs, risk level, permissions, and output.

**Implemented:** `tools/registry.py` (Tool/ToolRegistry) + `tools/demo.py`. Covered by unit tests.

---

## `FEAT-5` — Security policy engine

**Phase:** `testing`

Evaluate actions before execution and decide:

```text
ALLOW
CONFIRM
BLOCK
```

**Implemented:** `security/policy/policy.py` (PolicyEngine). HIGH risk defaults to BLOCK
for the MVP; CONFIRM is surfaced but no interactive approval UI exists yet (see FEAT-6).
Covered by unit tests.

---

## `FEAT-6` — Approval system

**Phase:** `pending`

Provide human approval gates for high-impact actions.

**Status note:** The policy engine emits `CONFIRM`, but there is no interactive approval
UI yet. This is intentionally deferred past the Phase 1 skeleton MVP (the MVP has no
MEDIUM/HIGH tool to approve). It becomes `building` in Phase 2 (Safe Tool System).

---

## `FEAT-7` — Executor

**Phase:** `testing`

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

**Phase:** `testing`

Determine whether an action actually achieved its intended result.

**Implemented:** `core/verifier/interface.py` + `core/verifier/checker.py` (ContractVerifier).
Covered by unit tests.

---

## `FEAT-10` — Recovery engine

**Phase:** `pending`

Classify failures and perform bounded recovery attempts before safely stopping.

---

## `FEAT-11` — Audit logging

**Phase:** `pending`

Record important decisions, approvals, actions, failures, and results without exposing secrets.

---

## `FEAT-12` — Basic computer-control tools

**Phase:** `pending`

Introduce controlled mouse, keyboard, window, and screen capabilities only after the security and verification foundations exist.

---

## `FEAT-13` — File/document tools

**Phase:** `pending`

Add safe filesystem and document operations with explicit destructive-action policies.

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

**Phase:** `pending`

Add user, project, and task memory with retention and privacy controls.

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
