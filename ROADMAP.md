# AI Computer Employee — Roadmap

## Phase 0 — Specification
Goal: freeze product requirements and architecture.
- PRD
- Architecture
- Security policy
- Folder structure
- Development/testing process

Exit: documentation reviewed and internally consistent.

## Phase 1 — Core Agent
Goal: create a minimal task pipeline.
- Application entry point
- Configuration
- Task model
- Brain interface
- Planner
- Executor interface
- Verifier
- Logging
- Basic tests

Exit: a simple task can pass through the complete pipeline and failures are reported correctly.

## Phase 2 — Safe Tool System
Goal: controlled tools.
- Tool registry
- Tool schemas
- Permission policy
- Approval system
- Audit logging

Exit: tools cannot execute outside their defined contract.

## Phase 3 — Computer Observation and Control
Goal: basic Windows interaction.
- Screen capture
- Keyboard
- Mouse
- Window/application control
- State observation
- Verification
- Emergency stop

Exit: controlled test tasks work repeatedly in a safe test environment.

## Phase 4 — Files and Documents
- File operations
- PDF
- Word
- Excel
- PowerPoint
- Import/export
- Validation

## Phase 5 — Browser Agent
- Browser navigation
- Page understanding
- Form interaction
- Search
- Download handling
- Verification
- Strong safety policies

## Phase 6 — Coding Agent
- Project inspection
- Code generation
- Test execution
- Error diagnosis
- Patch generation
- Regression testing

## Phase 7 — Memory
- User preferences
- Project memory
- Task history
- Retention controls
- Memory safety

## Phase 8 — Specialist Integrations
Examples:
- Revit
- AutoCAD
- Engineering workflows
- Other domain tools

Specialist integrations must remain optional modules.

## Phase 9 — Reliability
- Better recovery
- Failure classification
- Observability
- Performance
- Security hardening
- Regression suite

## Phase 10 — Advanced Autonomy
Only after the earlier phases are stable:
- Long-running workflows
- Scheduled tasks
- Multi-agent collaboration
- Advanced planning
- More autonomous execution

## Release Rule
No phase is considered complete because the code exists. A phase is complete only when its acceptance tests pass.
