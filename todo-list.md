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
| `done` | `CRIT-1`, `CRIT-2`, `CRIT-3`, `CRIT-4`, `CRIT-5`, `CRIT-6` — documentation/specification established |
| `testing` | — |
| `building` | — |
| `pending` | Phase 0 feasibility gate, technology selection, development environment, first executable skeleton |
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

**Phase:** `pending`

Before substantial coding:
- inspect the target Windows environment
- select the initial technology stack
- identify required external services
- decide what can run locally
- identify optional dependencies
- define the minimum executable prototype
- identify technical unknowns that must be tested before architecture is locked

**Rule:** Unknowns are experiments, not assumptions.

---

## `CRIT-8` — Define the first executable milestone

**Phase:** `pending`

The first executable milestone must prove the core loop:

```text
Task
→ Understand
→ Plan
→ Policy Check
→ Execute
→ Observe
→ Verify
→ Report
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

**Phase:** `pending`

Create a structured representation of a user task, its state, inputs, outputs, permissions, and result.

---

## `FEAT-2` — Brain interface

**Phase:** `pending`

Convert natural-language input into structured task understanding without directly executing computer actions.

---

## `FEAT-3` — Planner

**Phase:** `pending`

Create explicit, inspectable plans with steps, dependencies, required tools, and expected outcomes.

---

## `FEAT-4` — Tool registry

**Phase:** `pending`

Create a controlled registry describing what each tool can do, its inputs, risk level, permissions, and output.

---

## `FEAT-5` — Security policy engine

**Phase:** `pending`

Evaluate actions before execution and decide:

```text
ALLOW
CONFIRM
BLOCK
```

---

## `FEAT-6` — Approval system

**Phase:** `pending`

Provide human approval gates for high-impact actions.

---

## `FEAT-7` — Executor

**Phase:** `pending`

Execute approved tool actions and return structured results.

---

## `FEAT-8` — Observation layer

**Phase:** `pending`

Observe relevant application/computer state after actions.

---

## `FEAT-9` — Verification engine

**Phase:** `pending`

Determine whether an action actually achieved its intended result.

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
