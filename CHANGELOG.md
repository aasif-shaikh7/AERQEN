# Changelog

**Document:** `CHANGELOG.md`  
**Status:** Active â€” records only what has actually been established

All notable changes to AERQEN will be documented here.

The project is currently in an early architecture and specification stage. This changelog therefore records decisions, documentation, experiments, implementation milestones, and verified results â€” not imagined functionality.

The format is inspired by Keep a Changelog. Semantic versioning will be introduced when actual releasable software versions exist.

---

## [Unreleased]

### `0.0.0-spec` â€” AERQEN project foundation

Established the initial product identity:

- Product: **AERQEN**
- Category: **AI Computer Employee**
- Primary tagline: **One Agent. Every Workflow.**
- Repository naming convention: `aerqen`

Established the initial documentation set:

- `README.md`
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
- `todo-list.md`
- `done-list.md`
- `CHANGELOG.md`

### License decision

Recorded the project owner's decision to release AERQEN under the **MIT License** (`LICENSE`).

### Repository structure and onboarding

- Created the target directory structure (`app/`, `core/`, `agents/`, `tools/`, `security/`, `memory/`, `integrations/`, `tests/`, `docs/`, `data/`).
- Added `OLLAMA_SETUP_GUIDE.md` â€” a free, non-programmer guide to setting up the local LLM (Ollama) for the accepted ADR-005 decision.

### Phase 0 owner decisions (recorded)

- **License:** MIT (`LICENSE`, `README.md`).
- **Technology stack (ADR-004):** Python 3.12+ single core; Office/Revit/Android via Python/pyRevit/responsive web UI; C#/.NET deferred.
- **AI provider (ADR-005):** Local Ollama now + provider adapter for future multi-user/cloud.
- **Deployment (ADR-006):** All-local, Phase 1; multi-user/cloud deferred to Phase 10.
- **Environment/computer/observation (ADR-007):** Windows 11 in a VirtualBox VM; `pyautogui` for input; `pywinauto`+screen capture for observation.
- **Tool/security/testing/MVP (ADR-008):** full Tool Registry + Policy + Audit; hybrid testing (unit/integration local, system/security on VM); skeleton-pipeline MVP with a simple/fake tool.
- **New setup guide:** `VM_SETUP_GUIDE.md` (beginner Windows 11 VM setup) added to the root because the owner had no prior VM experience.

### Phase 1 skeleton pipeline (CRIT-8 - accepted by owner)

Implemented the runnable Phase 1 core skeleton (`CRIT-8`). This is the first executable
milestone: it proves the full loop with a **safe demo tool** and no real computer control.
On 2026-08-23 the owner ran and confirmed the acceptance tests.

- Added the AERQEN Python packages under `core/` (task model, brain, planner, executor,
  verifier, pipeline), `security/policy/`, `tools/`, and `app/`.
- Added `app/entrypoint/cli.py` â€” a CLI that runs one task through the loop.
- Added unit tests in `tests/unit/` (`pytest`).

**Measured (recorded):**
- `python -m app.entrypoint.cli "echo hello aerqen"` -> state `done`, verifier outcome
  `Measured: tool returned the exact message.`
- `python -m pytest tests -q` -> **4 passed**.
- `python -m app.entrypoint.cli "open office"` -> state `failed` (honest unsupported-command).

**Status:** `CRIT-8` is `done` (owner-accepted). `FEAT-1/2/3/4/5/7/9` are `testing`
(implemented + tests pass, awaiting owner `done` on each; they are part of CRIT-8's build).

### Environment verification (2026-09-03)

On the dev machine (host), installed `pytest` (9.1.1)and re-ran the acceptance gate:

- `python -m pytest tests -q` -> **4 passed**
- `python -m app.entrypoint.cli "echo hello aerqen"` -> state `done`
- `python -m app.entrypoint.cli "open office"` -> state `failed` (honest unsupported-command handling..

`Ollama` and the Windows 11 VM are recorded as **not yet installed** on this machine (owner
action pending. `CRIT-7` stays `building` until the VM/Ollama setup is recorded.

### Bug fix — BUG-1 (policy-gate crash(

Found and fixed a real bug while re-verifying the Phase 1 skeleton:

- **Bug:**the policy-gate path called the undefined method ``_describe_policy_gate``, so a
  MEDIUM/HIGH-risk step crashed with ``AttributeError`` instead of reporting ``blocked``.

- **Measured reproduction:** injected a HIGH-risk step -> ``AttributeError: 'Pipeline' object has no
  attribute '_describe_policy_gate'``.
- **Fix:** renamed ``_policy_gate_summary`` -> ``_describe_policy_gate`` (matches the call site; smallest
  change..
- **Regression test added:** ``test_high_risk_step_reports_blocked_without_crash``
  (``tests/unit/test_pipeline.py``; walks the full blocked path and asserts ``blocked`` + no crash..
- **Evidence:** `python -m pytest tests -q` -> **5 passed** (was 4(.


### Product scope

Defined AERQEN as a general-purpose computer-work platform rather than a Revit-only or browser-only automation product.

The long-term scope includes:

- computer interaction
- files and documents
- browser workflows
- Office workflows
- coding
- research
- memory
- specialist application integrations
- workflow automation
- verification and recovery

### Engineering direction

Defined a modular agent architecture separating:

- task intake
- reasoning
- planning
- policy/security
- tool registry
- execution
- observation
- verification
- recovery
- memory
- audit/logging
- UI

The core rule is:

> **Understand the task. Plan the work. Execute safely. Verify the result.**

### Development model

Established a one-person development model:

- one human developer/operator
- AI used as an engineering assistant
- human owns final decisions and acceptance
- AI-generated code is treated as untrusted until reviewed and tested
- no feature is considered complete merely because code compiles

### Testing model

Established:

- unit testing
- integration testing
- system testing
- security testing
- regression testing
- manual acceptance testing

The project deliberately distinguishes **reasoned**, **reported**, **measured**, and **unverified** evidence.

### Security direction

Established risk-based action handling:

```text
LOW RISK
MEDIUM RISK
HIGH RISK
```

High-impact actions require explicit user control.

The system must not bypass authentication, CAPTCHA, access controls, or security mechanisms.

### Phase-gate rule

Phase 0 must be completed before substantial implementation.

No advanced autonomous behavior is to be built merely because it is technically interesting.

---

## Current state

**Application runtime:** Not implemented yet.

**Documentation/specification:** Established.

**Phase:** Phase 0 â€” Specification and Feasibility.

**Next milestone:** Technical feasibility review and first executable core-agent prototype.

---

## Changelog rules

1. Record what actually happened.
2. Do not rewrite history to make progress look cleaner.
3. Keep rejected approaches when they teach an engineering lesson.
4. Distinguish code/build success from real-world behavior.
5. Record important limitations.
6. If a previous claim is found to be wrong, correct it explicitly rather than silently editing history.
