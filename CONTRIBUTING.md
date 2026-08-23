# AERQEN — Contributing Guide

**Document:** `CONTRIBUTING.md`
**Status:** Active

This is a one-person project: one human developer/operator supported by AI engineering
assistance. This guide applies to both the human and any AI asked to work on the repository.

---

## 1. Read these first

Before writing or changing anything, read in this order:

1. `README.md`
2. `PRD.md`
3. `ARCHITECTURE.md`
4. `FOLDER_STRUCTURE.md`
5. `SECURITY.md`
6. `ROADMAP.md`
7. `DEVELOPMENT_AND_TESTING.md`
8. `AI_DEVELOPMENT_GUIDE.md`
9. The existing implementation and tests

The repository itself is the source of truth. Do not rely on memory of what a module "should" do.

---

## 2. Who does what

**Human developer controls:**

- product requirements
- architecture decisions
- approvals
- secrets
- actual test execution
- release decisions
- final acceptance

**AI assistant may:**

- design, explain, and generate code
- review existing code
- propose tests
- diagnose errors
- improve documentation

**AI assistant must not:**

- invent test results or claim success without evidence
- hide failures
- silently change requirements
- expose secrets
- bypass security controls
- weaken security to make a feature work

---

## 3. The working queue

Nothing is built that is not on `todo-list.md`.

- New requirements, bugs, and ideas get an ID (`CRIT-*`, `FEAT-*`, `BUG-*`) **before** implementation.
- Work is never deleted from the queue to make it look shorter; use `superseded` instead.
- An item is `done` only when its acceptance criteria pass and the evidence is recorded in `done-list.md`.

---

## 4. Change procedure

Every meaningful change must answer:

1. **Reason** — why is this change needed?
2. **Expected behavior** — what should happen after the change?
3. **Implementation** — what exactly changes, and which files?
4. **Tests** — what test proves it? (Unit, Integration, System, Security, Regression, Manual)
5. **Result** — what actually happened when it was run?
6. **Known limitations** — what is still unknown or not covered?

Use the evidence vocabulary from `GLOSSARY.md`:

> **Measured / Reported / Reasoned / Unverified**

---

## 5. Before you code (state your plan)

Write down:

- Requirement
- Current behavior
- Desired behavior
- Files likely to change
- Test plan
- Risks

## 6. After you code (report what happened)

Write down:

- What changed
- Why
- Exact files changed
- How to run
- How to test
- Expected result
- Known limitations

---

## 7. Small, traceable commits

Prefer small commits named after the phase and the concern, for example:

- `phase-1-core`
- `phase-1-fix-task-validation`
- `phase-2-tool-registry`

One logical change per commit. Do not bundle unrelated edits.

---

## 8. Testing rules

- A feature is **not** complete because it compiles, "looks correct," or an AI says it works.
- A feature is complete when its acceptance criteria pass and the result is recorded.
- Never claim "tested," "verified," or "works" unless a real test was performed.
- After a meaningful change, re-run previous tests (regression testing).
- If you cannot run the test yourself, say exactly that:
  > Not executed by me; you need to run this test.

---

## 9. When something breaks

1. Stop adding new functionality.
2. Reproduce the problem.
3. Identify the failing layer.
4. Determine whether it is a regression.
5. Apply the smallest safe fix.
6. Add or update a test.
7. Re-run previous tests.
8. Document the change in `CHANGELOG.md` and record a `BUG-*` entry.

---

## 10. Documentation

- Keep documents in sync when code changes.
- Update `CHANGELOG.md` for decisions and confirmed results.
- Update the roadmap only through documented decisions.
- Add any new term to `GLOSSARY.md` in the same review that introduces it.
- Record architecture decisions in `ARCHITECTURE_DECISION_LOG.md`.

---

## 11. Security

Never weaken security to ship a feature. If a needed feature conflicts with `SECURITY.md`,
explain the conflict and propose a safe alternative instead of silently changing the policy.

---

## 12. License note

A license has not been chosen yet. Do not add a license claim until the project owner makes
and records that decision.