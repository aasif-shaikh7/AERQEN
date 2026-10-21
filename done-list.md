# AERQEN — Done List

**Document:** `done-list.md`  
**Status:** Active — the receipt of completed work  
**Companion to:** `todo-list.md`, which holds everything not yet finished

---

## How to read this

`todo-list.md` is the queue. This is the receipt.

An item moves here only when its acceptance criteria are satisfied and the required evidence exists.

For the software itself:

> **Compiles is not done.**

A compiler proves that code is syntactically/build-wise acceptable. It does not prove that the computer task works correctly.

Each entry records:

1. What was requested.
2. What was established.
3. How it is known.
4. What it costs or what remains limited.

### Evidence vocabulary

- **Measured** — actually executed and observed.
- **Reported** — observed by the project owner but not independently reproduced.
- **Reasoned** — technically justified but not executed.
- **Unverified** — no sufficient evidence yet.

---

## Completed documentation foundation

### `CRIT-1` — Product requirements established

**Closed:** Phase 0

**Built:** `PRD.md`

The product vision defines AERQEN as a general-purpose AI Computer Employee capable of task understanding, planning, controlled execution, observation, verification, recovery, memory, and security.

**How it is known:** Documentation reviewed for internal consistency.

**Cost:** Runtime behavior has not yet been implemented.

---

### `CRIT-2` — Architecture established

**Closed:** Phase 0

**Built:** `ARCHITECTURE.md`

The architecture separates:
- UI
- brain
- planner
- policy/security
- tools
- executor
- computer control
- observation
- verifier
- recovery
- memory
- audit/logging

**How it is known:** Architecture document exists and defines module boundaries.

**Cost:** Boundaries are not yet enforced by compiled code.

---

### `CRIT-3` — Security policy established

**Closed:** Phase 0

**Built:** `SECURITY.md`

Risk levels, approval gates, secret handling, browser safety, code execution safety, data minimization, security testing, and incident response are defined.

**How it is known:** Policy is documented.

**Cost:** Policy enforcement is not yet implemented.

---

### `CRIT-4` — One-person development/testing process established

**Closed:** Phase 0

**Built:** `DEVELOPMENT_AND_TESTING.md`

The project defines one human developer/operator assisted by AI. The human remains responsible for actual testing, approvals, secrets, and release decisions.

**How it is known:** Process documented.

**Cost:** No runtime test suite exists yet.

---

### `CRIT-5` — AI development guide established

**Closed:** Phase 0

**Built:** `AI_DEVELOPMENT_GUIDE.md`

AI contributors are instructed to inspect the repository before coding, make small changes, preserve working architecture, explain changes, and never invent test results.

**How it is known:** Development contract documented.

**Cost:** AI compliance must be enforced by process and review.

---

### `CRIT-6` — Roadmap established

**Closed:** Phase 0

**Built:** `ROADMAP.md`

Development is divided into phase gates from specification through core agent, safe tools, computer control, files/documents, browser, coding, memory, specialist integrations, reliability, and only then advanced autonomy.

**How it is known:** Roadmap documented.

**Cost:** Ordering may change when real feasibility evidence is discovered; changes must be recorded.

---

## No runtime features are claimed complete

At the start of implementation, this section intentionally remains mostly empty.

When a feature is completed, its entry should answer:

> **What was built, how was it tested, what evidence proves it, and what limitations remain?**

That rule exists specifically to prevent AERQEN from developing a changelog full of claims that were never executed.
## Phase 1 skeleton pipeline (CRIT-8 - done)

**Owner accepted this milestone on 2026-08-23** after running and confirming the manual
tests, matching `todo-list.md` -> `CRIT-8`.

**Measured evidence (recorded):**
- `python -m app.entrypoint.cli "echo hello aerqen"` -> state `done`, verifier outcome
  `Measured: tool returned the exact message.`
- `python -m pytest tests -q` -> **4 passed** (covers the full loop, policy, registry).
- `python -m app.entrypoint.cli "open office"` -> state `failed` (honest unsupported-command).

**Built:**
- `core/task_manager/models.py` — Task/Step models + states
- `core/brain/` (interface + mock) — task understanding
- `core/planner/` (interface + naive) — task planning
- `core/executor/` (interface + simple) — execution
- `core/verifier/` (interface + checker) — verification
- `security/policy/policy.py` — ALLOW / CONFIRM / BLOCK engine
- `tools/registry.py` + `tools/demo.py` — controlled demo tool
- `core/pipeline.py` — orchestrator
- `app/entrypoint/cli.py` — CLI entry point

**Limitations (recorded honestly):**
- The mock brain only understands the `echo <command>` set (real LLM brain deferred).
- No computer control, filesystem mutation, or external service.
- No interactive approval UI (FEAT-6) and no real screen observation (FEAT-8) — both are
  explicit later-phase capabilities.

**Limitations:**
- The mock brain only understands the `echo <command>` set (real LLM brain deferred).
- No computer control, filesystem mutation, or external service.
- No interactive approval UI (FEAT-6) and no real screen observation (FEAT-8) — both are
  explicit later-phase capabilities.

---

## Phase 2 foundation — safety gates (FEAT-1..7, FEAT-9, FEAT-11 — done)

**Owner accepted this milestone on 2026-10-21** (ADR-009 Accepted), matching
`todo-list.md` state table and PR #1.

**What was requested:** make risk authoritative so a planner/LLM cannot talk a risky tool
down to LOW; fix the order of the safety gates; make the approval and audit gates real.

**What was established:**
- A tool's declared risk in the registry is authoritative; effective risk =
  `max(planner risk, tool risk)`. Unknown tools and unknown risk labels are BLOCKed.
- Every tool declares an input schema; unknown/missing/mistyped parameters are rejected.
- Fixed gate order: Policy → Input check → Approval → (audit `step_execute`) → Execute → Verify.
- Fail-closed JSONL audit with secret redaction and string truncation; `DenyAllApprover` default.

**How it is known (Measured, 2026-10-21):** `python -m pytest tests -q` → **31 passed**.
Mutation check: removing the registry term from the risk rule makes 6 tests fail. CLI:
`guarded echo hello` with no answer → `blocked` / `approval: denied`; the audit file held the
expected event sequence.

**Built:** `tools/registry.py`, `security/policy/policy.py`, `security/approvals/approver.py`,
`security/audit/log.py`, `core/pipeline.py`, `tools/demo.py`, `tests/security/test_safety_gates.py`.

**Limitations:** the brain/planner were still the mock/naive ones at this stage (the LLM agent
is the next entry). No overwrite/delete tools; no computer control.

---

## Phase 2 — first LLM agent loop + sandboxed file tools (LLM-1, FEAT-13 — done)

**Owner accepted this milestone on 2026-10-21** (ADR-005 / ADR-010 Accepted), matching
`todo-list.md` state table and PR #2. The owner also ran the agent himself and confirmed it.

**What was requested:** turn AERQEN into a real agent — a local LLM that chooses tools and
actually does work — without weakening any of the safety gates.

**What was established:**
- `core/runner.py` (`StepRunner`) is the single home for the gates; both `core/pipeline.py`
  (refactored) and `core/agent/loop.py` use it, so the two cannot drift apart.
- The agent asks Ollama (`integrations/ai/`, stdlib only) for one tool per turn, runs it through
  the gates, and feeds the result back labelled UNTRUSTED. Bounded by `AERQEN_MAX_STEPS` (8).
- Sandboxed file tools (`tools/files.py`): `files.list` / `files.read_text` (LOW) and
  `files.write_text` (MEDIUM, create-only), confined to `AERQEN_WORKSPACE`. Traversal, absolute
  paths and drive letters are rejected; the write is verified by re-read + sha256.
- CLI `--agent` flag; the default pipeline is unchanged.

**How it is known (Measured, 2026-10-21 — NVIDIA 597.16 / T1000, qwen2.5:7b):**
`python -m pytest tests -q -m "not live"` → **51 passed**; the `live` Ollama test → **1 passed**.
Owner run (`task-9a7d3180`): the agent chose `files.write_text`, approval was granted, and
`data/workspace/notes.txt` was created with content `hello` and a matching sha256
(audit outcome *"Measured: file re-read from disk; sha256 matches"*). A separate run with no
approval was `blocked` and created no file — both the yes and no paths verified.

**Built:** `integrations/ai/provider.py`, `integrations/ai/ollama.py`, `core/agent/loop.py`,
`core/runner.py`, `tools/files.py`, `core/verifier/checker.py` (contract registration),
`app/configuration/settings.py`, `app/entrypoint/cli.py` (`--agent`),
`tests/unit/test_files.py`, `tests/unit/test_agent_loop.py`.

**Limitations (recorded honestly):**
- `files.write_text` is create-only — the agent cannot yet edit or delete a file.
- Only the three file tools exist; no web/browser, computer control, or memory yet.
- Agent quality depends on the local model; a model that never stops calling tools will hit the
  step budget and fail rather than finish.

---

## Phase 2 — file superpowers (FEAT-13 extension, ADR-011 — done)

**Owner accepted on 2026-10-21** (ADR-011 Accepted) after running the agent himself.

**What was requested:** let the agent do real file work — edit, add to, remove, search, and make
folders — without weakening the sandbox or risking the loss of the user's data.

**What was established:**
- New tools, all confined to `AERQEN_WORKSPACE`: `files.search` + `files.make_dir` (LOW), and
  `files.append_text` / `files.overwrite_text` / `files.delete` (MEDIUM — approval + audit).
- **Nothing is destroyed permanently:** `files.delete` moves the file into a workspace `.trash`
  folder; `files.overwrite_text` copies the previous version to `.trash` before replacing it.
  `files.delete` refuses folders; search/list hide `.trash` and `.gitkeep`.
- Writes store **exact bytes** (binary, no OS newline translation). A live run on Windows exposed
  that text-mode writes translated `\n`→`\r\n`, which broke the sha256 verifier on files with
  newlines; fixed before acceptance.

**How it is known (Measured, 2026-10-21 — qwen2.5:7b):**
`python -m pytest tests -q -m "not live"` → **62 passed**; the `live` Ollama test → **1 passed**.
Live multi-step agent run chained `files.write_text` → `files.append_text` → `files.read_text`
and summarized (`shopping.txt` → `buy milk\nbuy eggs\n`, 18 bytes, each mutating step
sha256-verified). Owner run (`task-0fa0a379`): `files.make_dir` ran automatically (LOW), then
`files.write_text` asked for approval (MEDIUM) and created `notes/today.txt` = `hello` — confirming
the risk tiering (LOW auto, MEDIUM asks) end to end.

**Built:** `tools/files.py` (new tools + `.trash` helper + exact-byte writes), verifier contracts
in `core/verifier/checker.py` via `tools/files.py`, `tests/unit/test_files.py`,
`tests/unit/test_agent_loop.py` (read→summarize flow).

**Limitations (recorded honestly):**
- No binary/document formats yet (PDF/Office); UTF-8 text only.
- `.trash` has no auto-purge, and overwrite keeps only a single point-in-time backup (no full
  version history).
