# AERQEN — Phase 0 Technology Selection (Working Record)

**Document:** `TECHNOLOGY_SELECTION.md`
**Status:** Working draft — fills in during `CRIT-7` (Phase 0 feasibility review)
**Companion to:** `ARCHITECTURE_DECISION_LOG.md` → `ADR-004`

> **Rule:** Unknowns are experiments, not assumptions. Nothing here is a final decision
> until the project owner measures and records it.

---

## Purpose

Before substantial application code is written, AERQEN must answer the feasibility
questions in `README.md` ("Current Next Step") and `CRIT-7` in `todo-list.md`. This
document is the structured working record for that review.

---

## Decision record format

For each area below, complete the same fields:

| Field | What to record |
|---|---|
| **Requirements** | Why this is needed. |
| **Candidate options** | What is being considered. |
| **Decision** | What was chosen (or `TBD`). |
| **Reasoning / evidence** | Measured, Reported, Reasoned, or Unverified. |
| **Risk / consequences** | What it costs or what could go wrong. |
| **Owner approval** | Project owner records the decision (`Accepted` / `Rejected`). |

---

## Feasibility questions to resolve

### 1. Target environment
- **Question:** What Windows version(s), hardware, and permissions is the first milestone built and tested on?
- **Candidate options:** Windows 10 / Windows 11; virtual machine vs physical machine.
- **Decision (owner-approved, recorded):** **Windows 11 running inside a Virtual Machine (VM) — e.g. VirtualBox** for development and testing, so a failure cannot harm the real machine's data.
  - Owner has no prior VM experience → a beginner `VM_SETUP_GUIDE.md` is provided in the repo root.
- **Reasoning / evidence:** `Reasoned` — VM isolates testing risk while using the same Windows 11 target as the real product.
- **Risk:** VM is slightly slower than the physical machine; requires installing a hypervisor first.
- **Owner:** recorded (Approved).

### 2. Language and runtime
- **Question:** What language/language runtime hosts the agent?
- **Considerations:** suitability for Windows automation, AI SDKs, test tooling, one-developer maintainability.
- **Decision (owner-approved, recorded):** **Python 3.12+** as the single core language.
- **Component decisions:**
  - AI core agent: **Python** (largest AI ecosystem, free, best for one-developer + AI-assist).
  - Office (Excel/Word/PPT): **Python** via `openpyxl`, `python-docx`, `python-pptx` (free).
  - Revit: **`pyRevit`** (Python) — no separate C#/.NET needed for Revit.
  - Windows automation: **Python** libraries.
  - Android/phone control: **Responsive Web UI (PWA)** — works in the Android browser without Kotlin; native Android deferred to a later phase.
  - C#/.NET: **deferred** optional module (Phase 8 specialist, if ever needed) — not part of the Phase 1 core.
- **Reasoning / evidence:** `Reasoned` (architecture review) — Python covers all stated scopes with free tooling and one language to learn.
- **Risk:** A single-language choice trades some native Windows/Revit performance for simplicity. Revisit only with a documented decision.
- **Owner:** recorded (Approved).

---

### 3. AI model/provider strategy
- **Question:** Which AI model/provider powers the Brain/Planner? Local, cloud, or hybrid?
- **Decision (owner-approved, recorded):** Local **Ollama** (open-source) as Phase 1 default — single-user, offline, free, no API key.
  - Multi-user / cloud: deferred until server budget/requirement exists; `integrations/ai/` provider adapter means the Brain/Planner do not change when a provider is added.
  - No student email → cloud free-tier is not a reliable free dependency.
- **Reasoning / evidence:** `Reasoned` (cost + privacy + no-student-email constraint).
- **Risk:** small local models may underperform large cloud models on complex/long tasks.
- **Owner:** recorded (Approved).

---

### 4. Local vs cloud responsibilities
- **Question:** What runs on the machine vts. what requires a remote service?
- **Decision (owner-approved, recorded):** **All-local (Phase 1).** The entire agent runtime — Python core, AI via Ollama, responsive web UI, tools — runs on the Windows machine. Access is `localhost` (and optionally LAN for phone/browser testing).
  - Multi-user / cloud: deferred to Phase 10 (see `ROADMAP.md` Advanced Autonomy).
- **Reasoning / evidence:** `Reasoned` — matches the single-user, free, privacy-first model; no server budget now.
- **Risk:** no remote access until a later phase; a phone on the same LAN uses `localhost/LAN`, not the internet.
- **Owner:** recorded (Approved).

### 5. Computer-control technology
- **Question:** How does AERQEN read controlled mouse/keyboard/window actions safely on Windows?
- **Considerations:** must satisfy `SECURITY.md` computer-control safety.
- **Decision (owner-approved, recorded):** **Python `pyautogui`** as the Phase 1 mouse/keyboard control library — simple, free, learning-friendly, and appropriate for the VM test environment.
- **Reasoning / evidence:** `Reasoned` — simplest Python path for mouse/keyboard; deep window control (`pywinauto`) is kept for observation (see §6) rather than core input control in Phase 1.
- **Risk:** `pyautogui` is screen-coordinate based; must always be used behind the permission/policy layer (`SECURITY.md`).
- **Owner:** recorded (Approved).

### 6. Observation technology
- **Question:** How does AERQEN capture and interpret application/computer screen state?
- **Decision (owner-approved, recorded):** **Screen capture + window-state reading via Python `pywinauto`** — screenshots (to see content) plus window/control state (to read the actual application state) for deeper observation.
- **Reasoning / evidence:** `Reasoned` — combining screen pixels with window-state gives both visual and structural understanding as required by `ARCHITECTURE.md` (Observation).
- **Risk:** window-state reliability depends on the target app; must not be used to bypass auth or access controls (`SECURITY.md`).
- **Owner:** recorded (Approved).

### 7. Secure tool-execution strategy
- **Question:** How are tools registered, permission-checked, approved, and audited before/after execution?
- **Decision (owner-approved, recorded):** **Full architecture-faithful design**: a Tool Registry + Policy/Security Engine (ALLOW / CONFIRM / BLOCK) + Approval gates + Audit Log, per `SECURITY.md`.
- **Reasoning / evidence:** `Reasoned` — directly matches the security model and `ARCHITECTURE.md` module boundaries; Phase 2 will implement it fully, but the design decision is fixed now.
- **Risk:** most complex of the tool decisions; built incrementally behind the `security/` boundary.
- **Owner:** recorded (Approved).

### 8. Testing environment
- **Question:** In what controlled environment are tests run safely (so a failure cannot harm real data)?
- **Decision (owner-approved, recorded):** **Hybrid — Unit + Integration tests run on the local machine; System + Security tests run inside the Windows 11 VM** (§1). This keeps fast feedback on the real machine while isolating risky full-system tests in the VM.
- **Reasoning / evidence:** `Reasoned` — local unit/integration is fast; VM isolates system/security tests from real data (aligns with §1 and `SECURITY.md`).
- **Risk:** VM must be running for system/security tests.
- **Owner:** recorded (Approved).

### 9. Minimum viable core loop
- **Question:** What is the smallest runnable `Task → Understand → Plan → Policy Check → Execute → Observe → Verify → Report` milestone?
- **Decision (owner-approved, recorded):** **A "skeleton pipeline" MVP**: run a text task through the whole loop using a simple/fake tool (no real computer control). This proves the pipeline (Task → Understand → Plan → Policy Check → Execute a stub tool → Observe → Verify → Report) before any real capability is attached.
- **Reasoning / evidence:** `Reasoned` — proving the loop's plumbing with a fake tool isolates the core-agent architecture from tool complexity (matches `todo-list.md` CRIT-8).
- **Risk:** a stub only proves flow, not a real-world result; this is intentional for the Phase 1 milestone.
- **Owner:** recorded (Approved).

---

## Open risks / unknowns to test

Record every technical unknown that might change the architecture. Examples:

- Reliability of capturing target application state automatically (mouse-keyboard coordinates).
- Whether the AI provider choice meets verification/observability needs at acceptable cost.
- Whether local-only operation is feasible or a cloud service is required.
- Whether the secure tool-execution model stays safe while running controlled system calls.

---

## Status labels

Mark each area with the best available evidence word:

- **Measured** — actually tested and observed.
- **Reported** — observed by owner, not reproduced.
- **Reasoned** — technically justified, not tested.
- **Unverified** — no evidence yet.

Format your entry:

```markdown
Area: <question>
Decision: <option or TBD>
Evidence: Unverified
Reasoning: <short technical note>
Risk: <what could go wrong>
Owner: <pending / recorded>
Closed: No  (set to Yes when the owner approves)
```

---

## Rules

1. `TBD` is honest until measured. Do not pretend a choice is final.
2. When a decision is made it be rewritten in `ARCHITECTURE_DECISION_LOG.md` as `ADR-004`+.
3. A choice is `Accepted` only after the project owner records it.
4. Remove nothing; mark choices `Rejected` with the reason if they are dropped.