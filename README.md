# AERQEN

## AI Computer Employee

> **One Agent. Every Workflow.**

AERQEN is an AI Computer Employee designed to understand natural-language tasks, plan workflows, use approved tools, interact with the computer, verify results, recover from failures, and assist with a broad range of digital work.

AERQEN is being built as a modular platform rather than a single-purpose automation script.

---

## Project Status

**Stage:** Phase 1 — Core Agent (skeleton pipeline) in progress  
**Runtime:** Minimal runnable skeleton pipeline (Python). Basic loop works; acceptance pending.  
**Development model:** One human developer (testing/decisions) + AI engineering lead

This repository is specification-first, but Phase 1 has produced a runnable skeleton that
implements the core loop with a safe demo tool.

Do not assume a capability exists merely because it appears in the roadmap.

---

## Vision

The long-term goal is to let a user give AERQEN a goal such as:

> "Create a monthly Excel report from these files, check the numbers, and prepare a summary."

AERQEN should eventually be able to:

1. Understand the request.
2. Break it into a plan.
3. Determine which tools are required.
4. Apply security and permission policies.
5. Ask for approval when necessary.
6. Execute approved actions.
7. Observe the resulting computer/application state.
8. Verify important outcomes.
9. Recover from recoverable failures.
10. Report what actually happened.

The product is intended to work across many kinds of computer tasks rather than being tied to one application.

---

## Core Philosophy

```text
UNDERSTAND
     ↓
PLAN
     ↓
POLICY CHECK
     ↓
EXECUTE
     ↓
OBSERVE
     ↓
VERIFY
     ↓
RECOVER OR REPORT
```

### The central promise

> **If AERQEN says a task is complete, it should be able to explain what it did and how the result was verified.**

---

## What AERQEN Is Not

AERQEN is not intended to be:

- an unrestricted shell
- a blind mouse macro
- a chatbot that claims success without checking
- a system that bypasses security
- an autonomous financial operator
- a CAPTCHA solver
- a credential-stealing system
- a destructive computer-control tool

The human remains in control of high-impact actions.

---

## Planned Capabilities

### Core
- Task understanding
- Planning
- Tool selection
- Execution
- Observation
- Verification
- Recovery

### Computer
- Mouse control
- Keyboard control
- Window/application control
- Screen observation

### Work
- Files
- PDF
- Word
- Excel
- PowerPoint
- Browser
- Research
- Coding

### Specialist
- Revit
- AutoCAD
- Engineering workflows
- Other professional applications

Specialist capabilities are intended to remain modular.

---

## Architecture

```text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │       UI        │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Task Intake    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Brain       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Planner     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Security/Policy │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Tool Registry  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Executor     │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Computer / External Tool │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │   Observation   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Verifier     │
                         └──────┬─────┬────┘
                                │     │
                         success│     │failure
                                │     ▼
                                │  Recovery
                                │     │
                                └─────┬┘
                                      ▼
                                ┌───────────┐
                                │  Result   │
                                └───────────┘
```

---

## Repository Structure

```text
aerqen/
│
├── README.md
├── PRD.md
├── ARCHITECTURE.md
├── FOLDER_STRUCTURE.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── ROADMAP.md
├── DEVELOPMENT_AND_TESTING.md
├── AI_DEVELOPMENT_GUIDE.md
├── GLOSSARY.md
├── CONTRIBUTING.md
├── ARCHITECTURE_DECISION_LOG.md
├── TECHNOLOGY_SELECTION.md
├── AERQEN_BRAND_GUIDE.md
├── OLLAMA_SETUP_GUIDE.md
├── VM_SETUP_GUIDE.md
├── PHASE1_TESTING_GUIDE.md
├── CHANGELOG.md
├── todo-list.md
├── done-list.md
│
├── app/
├── core/
├── agents/
├── tools/
├── computer/
├── memory/
├── security/
├── integrations/
├── tests/
├── docs/
└── data/
```

See `FOLDER_STRUCTURE.md` for the detailed structure and module responsibilities.

---

## Development Rules

This is a one-person development project supported by AI.

### Human developer

The human developer controls:

- product requirements
- architecture decisions
- approvals
- secrets
- actual testing
- release decisions

### AI assistant

AI may:

- design
- explain
- generate code
- review code
- propose tests
- diagnose errors
- improve documentation

AI must not:

- invent test results
- claim code works without evidence
- hide failures
- silently change requirements
- expose secrets
- bypass security controls

---

## Testing Rule

A feature is not complete because:

- the code looks correct
- an AI says it works
- the project compiles
- a single screenshot looks good

A feature is complete when its acceptance criteria pass and the result is recorded.

The project uses:

- Unit tests
- Integration tests
- System tests
- Security tests
- Regression tests
- Manual acceptance tests

---

## Development Workflow

```text
Requirement
    ↓
Specification
    ↓
Architecture
    ↓
Small implementation
    ↓
Test
    ↓
Observe actual result
    ↓
Fix
    ↓
Regression test
    ↓
Document
    ↓
Accept
    ↓
Next task
```

Never skip the testing gate merely to move faster.

---

## Roadmap

### Phase 0 — Specification and Feasibility
Define and validate the technical foundation.

### Phase 1 — Core Agent
Build the task → plan → execute → verify pipeline.

### Phase 2 — Safe Tool System
Introduce tools, permissions, policies, approvals, and audit logs.

### Phase 3 — Computer Observation and Control
Introduce controlled Windows interaction.

### Phase 4 — Files and Documents
Files, PDF, Word, Excel, PowerPoint.

### Phase 5 — Browser Agent
Safe browser workflows.

### Phase 6 — Coding Agent
Code generation, testing, debugging, and controlled patches.

### Phase 7 — Memory
User/project/task memory.

### Phase 8 — Specialist Integrations
Revit, AutoCAD, engineering, and other applications.

### Phase 9 — Reliability
Recovery, observability, performance, regression, security hardening.

### Phase 10 — Advanced Autonomy
Long-running workflows, scheduling, multi-agent behavior, and broader autonomy.

A later phase must not be considered complete until the required tests pass.

See `ROADMAP.md`.

---

## Security

AERQEN follows a security-first approach.

High-impact actions may require explicit approval, including:

- deletion
- irreversible changes
- external communication
- purchases
- account/security changes
- sensitive-data transfers
- destructive system commands

AERQEN must not bypass authentication, CAPTCHA, access controls, or other security mechanisms.

See `SECURITY.md`.

---

## AI Development

Any AI asked to work on this repository must first read:

1. `PRD.md`
2. `ARCHITECTURE.md`
3. `FOLDER_STRUCTURE.md`
4. `SECURITY.md`
5. `ROADMAP.md`
6. `DEVELOPMENT_AND_TESTING.md`
7. `AI_DEVELOPMENT_GUIDE.md`
8. Existing implementation and tests

The repository itself is the source of truth.

See `AI_DEVELOPMENT_GUIDE.md`.

---

## Brand

**AERQEN**

**Category:** AI Computer Employee

**Tagline:** One Agent. Every Workflow.

**Core philosophy:**

> Understand the task. Plan the work. Execute safely. Verify the result.

See `AERQEN_BRAND_GUIDE.md`.

---

## Current Next Step

**Phase 0 feasibility is recorded.** All nine questions below are now answered in
`TECHNOLOGY_SELECTION.md` (ADR-004..ADR-008): target environment, language/runtime, AI
provider, local-vs-cloud, computer control, observation, secure tool execution, testing
environment, and the minimum viable core loop.

**Phase 1 skeleton pipeline is implemented** (see `CHANGELOG.md`). The immediate next
steps are:

1. **Owner acceptance gate:** run the CLI + test suite once and confirm (see `CRIT-8`).
   - `python -m app.entrypoint.cli "echo hello aerqen"`
   - `python -m pytest tests -q`
2. **Set up the real dev environment** using `VM_SETUP_GUIDE.md` (Windows 11 VM) and
   `OLLAMA_SETUP_GUIDE.md` (local AI). When done, record it under `CRIT-7` in `todo-list.md`.
3. After acceptance + environment, continue Phase 1 toward a real LLM brain (via the
   `integrations/ai` provider adapter) and the first real controlled tool.

Only after the owner confirms the executable milestone should the next capability be added.

---

## License

AERQEN is released under the **MIT License**. See `LICENSE`.

**Owner decision (recorded):** MIT License chosen by project owner.

---

## Project Principle

> **Build small. Test honestly. Verify everything important. Never hide failure.**
