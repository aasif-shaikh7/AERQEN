# AERQEN — Architecture Decision Log

**Document:** `ARCHITECTURE_DECISION_LOG.md`
**Status:** Active — the record of significant decisions and rejected approaches.

This log exists because `CHANGELOG.md` and `AI_DEVELOPMENT_GUIDE.md` require that decisions
and rejected approaches be recorded rather than silently changed. It complements the
changelog: the changelog records *what happened*, this log records *why a decision was made*.

Each entry is called an **ADR** (Architecture Decision Record) and has its own status.

---

## Status vocabulary

| Status | Meaning |
|---|---|
| **Proposed** | Being considered; not yet accepted. |
| **Accepted** | Chosen and recorded; may be revisited only through a new decision. |
| **Superseded** | Replaced by a later decision; retained for history and lessons. |
| **Rejected** | Considered and deliberately not chosen. |

---

## Template for a new ADR

When a decision is made or a meaningful alternative is rejected, copy this template.

```markdown
## ADR-### — <Short title>

**Status:** Proposed | Accepted | Superseded | Rejected
**Date:** YYYY-MM-DD
**Owner:** Human developer

### Context
What situation forced this decision? What are the constraints (one-person project, Windows target, security-first)?

### Decision
What was decided in one or two sentences.

### Alternatives considered
List the meaningful alternatives and why each was rejected.

### Consequences
What improves because of this decision, and what becomes harder or is traded away?

### References
PRD / ARCHITECTURE / SECURITY / ROADMAP / todo-list IDs that relate to this decision.
```

Do not edit history. If a decision changes, mark the old one `Superseded` and add a new entry.

---

## Decision Index

| ADR | Title | Status |
|---|---|---|
| `ADR-001` | Modular agent architecture with strict module boundaries | Accepted |
| `ADR-002` | Security-first with LOW / MEDIUM / HIGH risk model | Accepted |
| `ADR-003` | Target repository structure and module layout | Accepted |
| `ADR-004` | (Reserved) Phase 0 technology stack selection | Pending |

---

## ADR-001 — Modular agent architecture with strict module boundaries

**Status:** Accepted
**Owner:** Project owner (recorded from `ARCHITECTURE.md`)

### Context
The product must stay maintainable by one developer with AI help, and must not let an
LLM become an unrestricted computer controller. Modules must not silently take over
responsibilities that belong elsewhere.

### Decision made
Separate the system into bounded modules: Brain, Planner, Policy/Security, Tool Registry,
Executor, Computer Control, Observation, Verifier, Recovery, Memory, Audit/Logging, and UI.
Each module exposes an explicit interface and must not reach into another module's
responsibility.

### Consequences
- **Positive:** clear responsibilities, easier testing, safer evolution.
- **More complex:** more files and interface work early; this is acceptable by design.

**References:** `ARCHITECTURE.md`, `FOLDER_STRUCTURE.md`, `PRD.md`.

---

## ADR-002 — Security-first action handling with risk levels

**Status:** Accepted
**Date:** Recorded in `SECURITY.md`

**Context**
AERQEN must be useful computer software without becoming unrestricted control software.

**Decision made**
Classify actions as `LOW`, `MEDIUM`, or `HIGH` risk. High-impact actions require explicit
human confirmation. The agent must never bypass authentication, CAPTCHA, or access controls.

**Consequences**
- **Positive:** safety by default; the human stays in control of high-impact actions.
- **Negative:** some workflows require approval steps and cannot be fully autonomous.

**References:** `SECURITY.md`.

---

## ADR-003 — Repository structure with separated module directories

**Status:** Accepted

**Context**
`FOLDER_STRUCTURE.md` defines the target layout so that capabilities map to folders and
are not scattered.

**Decision made**
Use the `aerqen/` root described in `FOLDER_STRUCTURE.md`, with `app/`, `core/`, `agents/`,
`tools/`, `security/`, `memory/`, `integrations/`, `tests/`, `docs/`, and `data/` divisions.
Add a directory only when a real requirement or architectural boundary justifies it.

**Consequences**
- **Positive:** predictable placement of new code.
- **Negative:** requires discipline not to create unneeded modules.

**References:** `FOLDER_STRUCTURE.md`, `AERQEN_BRAND_GUIDE.md` (repository naming).

---

## ADR-004 — Phase 0 technology stack selection (reserved)

**Status:** Pending
**Date:** — 

This ADR is reserved for the outcome of `CRIT-7` in `todo-list.md`. Until the feasibility
review is measured and recorded, no technology choice is locked. See the working record in
`TECHNOLOGY_SELECTION.md`.

---

## ADR rules

1. Do not rewrite an accepted ADR in place. Mark it `Superseded` and add the new decision.
2. Record rejected alternatives; they teach the next decision.
3. A decision is `Accepted` only when the project owner has made and recorded it.
4. Link each ADR to the roadmap/todo IDs it affects.