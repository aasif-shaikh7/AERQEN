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


### Dev environment — Ollama + VirtualBox installed (2026-09-03(

On the dev machine (host(, per owner coordination:

- `Ollama 0.33.2` installed via `winget`;; **Measured:** `ollama --version` -> `version is 0.33.2`.
- Model `qwen2.5:7b` (4.7 GB) downloaded;; **Measured answer:** `ollama run qwen2.5:7b "What is  ️5+7?"` -> `12`.
- `VirtualBox 7.2.16` installed via `winget`;; **Measured:** `VBoxManage.exe --version` -> `7.2.16r174877`.
- VM `AERQEN-Win11` created + configured via `VBoxManage`;; **Measured:** `.vbox` XML: EFI, TPM 2.0,
  4096 MB RAM,  ️4 CPUs, NAT, SATA controller + 50 GB disk + DVD slot attached. Secure Boot is not
  exposed by this VirtualBox build (known limitation;; Windows 11 setup proceeds via registry bypass(.

**Remaining owner action:**
- Downloadthe Windows  ️11 ISO, ~6 GB (, official Microsoft site(;, then send me the path so I can attach
  it to the VM (SATA port 1, DVD(.
- Run Windows setup inside the VM per `VM_SETUP_GUIDE.md`; then record `CRIT-7` as done in `todo-list.md`.


### Phase 2 foundation — safety gates (2026-10-21; owner accepted 2026-10-21)

- **Registry-authoritative risk (ADR-009, proposed):** the effective risk of a step is now
  `max(planner risk, tool's declared risk)`. Unknown tools and unrecognised risk labels are blocked.
- **Tool input schemas (FEAT-4):** every tool declares its parameters. Unknown, missing or
  wrongly typed parameters are rejected before approval and again inside `Tool.run`.
- **Approval gate (FEAT-6):** `security/approvals/approver.py` provides `DenyAllApprover` (default)
  and `CliApprover` (needs an explicit y/yes). New harmless demo command `guarded echo <msg>`
  uses a MEDIUM-declared tool so the gate can be tried by hand.
- **Audit log (FEAT-11):** `security/audit/log.py` writes JSONL to `data/logs/audit.jsonl`,
  redacts secret-looking keys, truncates long strings, and fails closed.
- **Pipeline:** fixed gate order. Execution now stops at the first failed step. CLI task ids are unique per run.
- **Tests:** strengthened the BUG-1 regression test, which had started to pass for the wrong reason
  (empty registry), and added `tests/security/test_safety_gates.py`.
- **Evidence (Measured, 2026-10-21):** `python -m pytest tests -q` -> **31 passed**. Mutation check:
  removing the registry term from the risk rule makes 6 tests fail. CLI: `echo hello aerqen` -> `done`;
  `guarded echo hello` with no answer -> `blocked` / `approval: denied`; `open office` -> `failed`.
  The audit file contained the expected event sequence.

### Phase 2 — first LLM agent loop (2026-10-21; owner accepted 2026-10-21)

- **Shared gate runner (ADR-010, proposed):** `core/runner.py` (`StepRunner`) holds the gate logic
  once; `core/pipeline.py` was refactored to use it, so the fixed-plan pipeline and the new agent
  cannot drift apart. The 31 foundation tests still pass unchanged after the refactor.
- **LLM provider adapter (ADR-005):** `integrations/ai/provider.py` defines a provider-neutral
  interface; `integrations/ai/ollama.py` talks to Ollama's `/api/chat` using only the standard
  library (urllib). URL and model come from env (`AERQEN_OLLAMA_URL`, `AERQEN_OLLAMA_MODEL`).
- **Agent loop:** `core/agent/loop.py` asks the model for one tool per turn, runs it through the
  gates, feeds the (untrusted) result back, and stops on a final answer, a BLOCK, a denial, or the
  `AERQEN_MAX_STEPS` budget (default 8). Tool output is labelled untrusted before re-entering the prompt.
- **Sandboxed file tools (ADR-010):** `tools/files.py` adds `files.list` / `files.read_text` (LOW)
  and `files.write_text` (MEDIUM, create-only). All paths are confined to `AERQEN_WORKSPACE`
  (default `data/workspace`); traversal, absolute paths and drive letters are rejected. The write
  verifier re-reads the file and compares sha256.
- **CLI:** new `--agent` flag runs the LLM loop; the default (no flag) pipeline is unchanged.
- **Tests:** added `tests/unit/test_files.py` (sandbox + create-only) and
  `tests/unit/test_agent_loop.py` (a `FakeProvider` drives the loop; one `live` test talks to real
  Ollama and skips when it is down).
- **Evidence (Measured, 2026-10-21, NVIDIA 597.16 / T1000, qwen2.5:7b):**
  `python -m pytest tests -q -m "not live"` -> **51 passed**; the `live` test -> **1 passed** (12.9s).
  Live CLI/demo run: the agent called `files.write_text`, approval was granted, and the file was
  re-read with a matching sha256 (`report.txt` -> `AERQEN is alive.`). With no approver the same
  write was `blocked` / `approval: denied` and no file was created.

### Phase 2 — file superpowers (2026-10-21; owner accepted 2026-10-21)

- **New file tools (ADR-011, proposed):** `files.search` and `files.make_dir` (LOW),
  `files.append_text`, `files.overwrite_text`, `files.delete` (MEDIUM, approval + audit).
- **Recoverable by design:** `files.delete` moves the file into a workspace `.trash` folder;
  `files.overwrite_text` backs up the previous version to `.trash` before replacing it. Nothing
  is permanently destroyed. `files.delete` refuses folders; search/list hide `.trash`/`.gitkeep`.
- **Exact-byte writes:** write/overwrite/append now write bytes directly (no OS newline
  translation), fixing a Windows CRLF issue that made the sha256 verifier report a false failure
  on files containing newlines — caught by a live multi-step run, not assumed.
- **"Read and summarize"** needs no new tool: the agent reads with `files.read_text` and answers.
- **Tests:** +11 (file tools + an agent read→summarize flow). `pytest -m "not live"` -> **62 passed**.
- **Evidence (Measured, 2026-10-21, qwen2.5:7b):** a live agent task chained
  `files.write_text` → `files.append_text` → `files.read_text` and summarized the result;
  `shopping.txt` ended as `buy milk\nbuy eggs\n` (18 bytes), every mutating step sha256-verified.

### Phase 2 — agent memory (2026-10-21; owner acceptance pending)

- **Durable memory (ADR-012, proposed):** `core/memory/store.py` (`MemoryStore`) is a small
  bounded JSONL notebook at `AERQEN_MEMORY` (default `data/memory/memory.jsonl`), separate from
  the file workspace. Notes are length-capped and the store keeps only the newest
  `AERQEN_MEMORY_MAX` (default 200); corrupt lines are skipped.
- **Tools (all LOW):** `memory.remember`, `memory.recall`, `memory.list` (`tools/memory.py`).
- **Auto-recall:** the agent loop injects the most relevant saved notes (keyword match, newest
  first, `AERQEN_MEMORY_RECALL` default 5) into the prompt as its own notes / data — never as
  instructions — at the start of each task. If the wording/language keyword-matches nothing, it
  falls back to the most recent notes, so memory works regardless of how the user phrases the
  question. The system prompt also tells the agent to save user facts and use recalled notes.
  Memory failures never break a task.
- **Tests:** +15 (store behaviour, tools, and two agent auto-recall tests). `pytest -m "not live"`
  -> **75 passed**.
- **Evidence (Measured, 2026-10-21, qwen2.5:7b):** run 1 saved "my favourite colour is blue" via
  `memory.remember`; a separate run 2 (new agent, same file) auto-recalled it and answered
  "your favourite colour is blue".

### Phase 2 — local web chat UI (2026-10-21; owner acceptance pending)

- **Browser chat (ADR-013, proposed):** `app/web/server.py` is a stdlib-only HTTP server that
  serves a single mobile-first chat page and a small JSON API. `app/web/service.py`
  (`AgentService`) runs each message through the same `AgentLoop`/`StepRunner`.
- **Works on PC and phone:** binds to the LAN so a phone on the same WiFi can open it; the
  server prints a link for the PC and one for the phone. `chat.bat` starts it with one click.
- **Safety intact:** MEDIUM steps pause for an Allow/Deny tap in the UI (`WebApprover`), and a
  per-session **token** (in the link) stops other devices on the network from driving the agent.
- **Tests:** +7 (service approval flow + a real HTTP round-trip with a fake model).
  `pytest -m "not live"` -> **83 passed**.
- **Evidence (Measured, 2026-10-21, qwen2.5:7b):** over HTTP, "what is my favourite colour" ->
  "Your favourite colour is blue"; "create webtest.txt ..." paused for approval, Allow was
  tapped, and the file was created.

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
