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
| `ADR-004` | Python-centric technology stack (Phase 0) | Accepted |
| `ADR-005` | AI provider: local Ollama now, provider adapter for future | Accepted |
| `ADR-006` | All-local deployment (Phase 1) | Accepted |

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

## ADR-004 — Python-centric technology stack (Phase 0 acceptance)

**Status:** Accepted
**Date:** 2026-08-23 (recorded from owner decision)

**Context**
`CRIT-7` required choosing the initial technology stack before substantial code. The
project owner requested a free, student-friendly, single-language solution covering AI,
Windows automation, Office, Revit, and Android/phone control.

**Decision**
Use **Python 3.12+** as the single core language:
- AI core agent → Python
- Office / documents → Python (`openpyxl`, `python-docx`, `python-pptx`)
- Revit → `pyRevit` (Python) instead of a separate C#/.NET core
- Windows automation → Python libraries (kept behind the security layer)
- Android / phone control → Responsive Web UI (PWA) in the phone browser; separate native app deferred

**Alternatives considered (and rejected for now)**
- **C#/.NET as core language** — rejected: adds a second language to learn for no Phase 1 benefit; deferred to optional specialist modules.
- **Native Kotlin Android app now** — rejected: the security model (human must stay in control) is served by a responsive web UI; native app adds complexity before the product is stable.
- **TypeScript/Node.js core** — rejected: weaker Windows desktop automation suite vs Python.

**Consequences**
- **Positive:** one language, 100% free tooling, matches the student/non-programmer owner, covers all scopes.
- **Neutral/trading:** some specialist native performance deferred.

**References:** CRIT-7, `TECHNOLOGY_SELECTION.md`, `FOLDER_STRUCTURE.md`.

---

## ADR-005 — AI provider: local Ollama now, provider adapter for future

**Status:** Accepted
**Date:** 2026-08-23 (recorded from owner decision)

**Context**
`CRIT-7` required an AI provider strategy. The owner is a student with no official student
email (so cloud free-tiers are not a reliable free dependency) and no multi-user server
budget yet. The long-term product may need multi-user/cloud, but it is not affordable now.

**Decision**
- **Phase 1 default:** Local **Ollama** (open-source, offline, free, no API key) for the Brain/Planner.
- **Provider abstraction:** All provider-specific AI code lives in `integrations/ai/` behind a provider **adapter**. The Brain/Planner must depend on this adapter interface, never on a specific vendor.
- **Multi-user / cloud:** Deferred. When a server budget or cloud requirement exists, add a new adapter (e.g. self-hosted `ollama serve`, or a paid cloud API) without changing core.

**Alternatives considered (rejected for now)**
- **Cloud free-tier only** — rejected: the owner has no official student email, so this is not a reliable free path.
- **Native Kotlin/Android multi-user backend now** — out of scope; deferred.

**Consequences**
- **Positive:** zero cost, offline privacy, no secret/API-key exposure for the core path; future cloud/multi-user is an isolated addition.
- **Negative/trading:** small local models may be less capable than large cloud models; performance depends on the user's machine.

**References:** `CRIT-7`, `integrations/ai/` (FOLDER_STRUCTURE.md), `SECURITY.md` (secrets).

---

## ADR-006 — All-local deployment (Phase 1)

**Status:** Accepted
**Date:** 2026-08-23 (recorded from owner decision)

**Context**
`CRIT-7` required deciding local vs cloud responsibilities. The owner is a single user with
no server budget and prefers free, private, offline-first operation.

**Decision**
In Phase 1, everything runs **locally on the Windows machine**:
- Python core agent, AI via local Ollama, responsive web UI, and all tools run on the device.
- Access is `localhost`; optionally exposed on the LAN so a phone/browser on the same network can control it.
- No cloud server in Phase 1. Multi-user / cloud is deferred to Phase 10 (Advanced Autonomy in `ROADMAP.md`).

**Alternatives considered (rejected for now)**
- **Cloud-hosted agent now** — rejected: no server budget, privacy/cost trade-offs, and no student-email cloud tier.

**Consequences**
- **Positive:** zero cost, offline privacy, simple single-machine setup.
- **Negative/trading:** no remote/internet access until a later phase; capacity limited to one machine.

**References:** `CRIT-7`, `ROADMAP.md` (Phase 10), `TECHNOLOGY_SELECTION.md` (section 4).

---

## ADR rules

1. Do not rewrite an accepted ADR in place. Mark it `Superseded` and add the new decision.
2. Record rejected alternatives; they teach the next decision.
3. A decision is `Accepted` only when the project owner has made and recorded it.
4. Link each ADR to the roadmap/todo IDs it affects.