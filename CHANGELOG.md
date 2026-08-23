# Changelog

**Document:** `CHANGELOG.md`  
**Status:** Active — records only what has actually been established

All notable changes to AERQEN will be documented here.

The project is currently in an early architecture and specification stage. This changelog therefore records decisions, documentation, experiments, implementation milestones, and verified results — not imagined functionality.

The format is inspired by Keep a Changelog. Semantic versioning will be introduced when actual releasable software versions exist.

---

## [Unreleased]

### `0.0.0-spec` — AERQEN project foundation

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

**Phase:** Phase 0 — Specification and Feasibility.

**Next milestone:** Technical feasibility review and first executable core-agent prototype.

---

## Changelog rules

1. Record what actually happened.
2. Do not rewrite history to make progress look cleaner.
3. Keep rejected approaches when they teach an engineering lesson.
4. Distinguish code/build success from real-world behavior.
5. Record important limitations.
6. If a previous claim is found to be wrong, correct it explicitly rather than silently editing history.
