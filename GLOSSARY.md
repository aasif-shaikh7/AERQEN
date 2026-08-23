# AERQEN — Glossary of Terms

**Document:** `GLOSSARY.md`
**Status:** Active — the shared vocabulary used across the repository.

This glossary helps the non-programmer developer, the AI assistant, and any future
contributor use the same words with the same meaning. If a term is ever used differently
in another document, that document is considered wrong unless this glossary is updated.

---

## Product Terms

| Term | Meaning |
|---|---|
| **AERQEN** | The product and brand name (pronounced *Air-ken*). Technical identifiers may use lowercase `aerqen`. |
| **AI Computer Employee** | The product category: software that understands natural-language tasks, plans work, uses approved tools, verifies results, and reports honestly. |
| **Agent** | The overall AERQEN process that carries a task from understanding to reported result. |
| **Task** | A unit of user intent given to AERQEN, e.g. "Create a monthly Excel report from these files." |
| **Workflow** | A sequence of one or more steps needed to complete a task. |
| **Module** | A small, self-contained unit of software with a clear responsibility and interface. |

---

## Architecture Terms

| Term | Meaning |
|---|---|
| **Brain** | Converts user intent into structured task information. It must not directly control hardware, files, or network. |
| **Planner** | Turns a task into explicit, inspectable steps and dependencies. |
| **Executor** | Runs approved tool actions and returns structured results. It reports success/failure; it never assumes success. |
| **Tool** | A controlled capability AERQEN can use (filesystem, browser, document, computer control, etc.). |
| **Tool Registry** | The controlled list of available tools describing each tool's inputs, capabilities, risk, and outputs. |
| **Observation** | Capturing relevant application/computer state after an action. |
| **Verifier** | Checks whether an action actually achieved its intended result. |
| **Recovery** | Handling recoverable failures with bounded retries, then stopping safely. It must never loop indefinitely. |
| **Memory** | Storing only useful, permitted information: user preferences, project context, task history. |
| **Task Manager** | Tracks the state and lifecycle of tasks through the pipeline. |

---

## Security Terms

| Term | Meaning |
|---|---|
| **Policy** | A rule that decides whether an action is allowed. |
| **Permission Level / Risk Level** | Classification of an action: `LOW RISK`, `MEDIUM RISK`, or `HIGH RISK`. |
| **Action decision** | The outcome of a policy check: `ALLOW`, `CONFIRM`, or `BLOCK`. |
| **Approval** | Explicit human consent required before high-impact actions execute. |
| **Audit Log** | A record of decisions, approvals, actions, failures, and outcomes that never exposes secrets. |
| **Secret** | Something that must stay private: API keys, passwords, tokens, cookies, private keys. |
| **Credential** | Information used to prove identity (e.g. a password) or to authenticate. |
| **CAPTCHA / Access Control** | Web or system mechanisms that must never be bypassed by AERQEN. |
| **Incident** | A discovered security problem or serious unexpected behavior. |

---

## Process Terms

| Term | Meaning |
|---|---|
| **Phase** | A stage of development from the roadmap (Phase 0 … Phase 10). |
| **Phase gate / Exit criteria** | The documented condition that must be true before a phase is considered complete. |
| **Acceptance criteria** | Explicit, verifiable conditions a feature must satisfy to be accepted. |
| **Milestone** | A point in time when some tested, documented result is available. |
| **Regression** | A previously working feature that stops working after a change. |
| **Regression test** | Re-running old tests after a change to confirm nothing broke. |
| **MVP / Minimum Viable Core Loop** | The smallest runnable version of the task → plan → execute → verify → report cycle for the first milestone. |

---

## Evidence Terms

These four words are used deliberately. Do not use them loosely.

| Term | Meaning | Example claim |
|---|---|---|
| **Measured** | Actually executed and observed, with the result recorded. | "The integration test ran and this output was recorded." |
| **Reported** | Observed by the project owner but not independently reproduced. | "The owner saw X but I could not reproduce it." |
| **Reasoned** | Supported by documented technical reasoning, but not yet observed. | "Based on the architecture, module A handles this." |
| **Unverified** | Intended or believed, with no test evidence yet. | "We expect this to work once implemented." |

The checklist question for any claim is:

> **Is this Measured, Reported, Reasoned, or Unverified?**

---

## Tag / ID Terms

| Term | Meaning |
|---|---|
| **`CRIT-*`** | Critical work that blocks the first usable AERQEN milestone. |
| **`FEAT-*`** | A new capability built and tested independently. |
| **`BUG-*`** | A real failure in an implemented feature, with reproduction evidence. |
| **`pending` / `building` / `testing` / `superseded` / `done` / `blocked`** | The lifecycle states used in `todo-list.md`. |

---

## Relationship to other documents

- Vocabulary rules: `todo-list.md` and `done-list.md`
- Architecture module names: `ARCHITECTURE.md`
- Security terms: `SECURITY.md`
- Development process: `DEVELOPMENT_AND_TESTING.md`

If you must introduce a new term, add it to this glossary in the same review that introduces it.