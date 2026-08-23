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
