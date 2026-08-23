# AI Computer Employee — Product Requirements Document (PRD)

## 1. Product Vision
Build a general-purpose AI Computer Employee for Windows that can understand natural-language instructions, plan multi-step tasks, use approved computer tools, verify results, recover from failures, and report what it did.

The product is NOT limited to Revit. It should eventually support common digital work such as files, browser tasks, Office documents, spreadsheets, PDFs, coding, research, repetitive workflows, and specialist applications.

## 2. Primary User
The product is designed for a single non-programmer developer/operator who will use AI coding assistance to design, implement, debug, document, and test the software.

## 3. Core Principle
The system must be built incrementally. Never create a huge untested codebase. Every phase must produce a runnable, testable milestone.

## 4. Core Capabilities
- Natural-language task input
- Task understanding and decomposition
- Tool selection
- Controlled computer interaction
- Screen/state observation
- Action verification
- Retry and recovery
- File and document operations
- Browser automation
- Office automation
- Coding assistance and code execution in a controlled environment
- Persistent task/project memory
- Permissions and approval gates
- Audit logs
- Human-readable status and errors

## 5. Non-Goals for V1
- Fully autonomous unrestricted computer control
- Autonomous financial purchases
- Autonomous destructive file operations
- Circumventing authentication, CAPTCHA, access controls, or security systems
- Pretending an action succeeded when it was not verified

## 6. User Experience
The user should be able to say:
"Create a monthly Excel report from these files."

The system should:
1. Understand the request.
2. Explain or internally construct a plan.
3. Identify required tools.
4. Request approval when required.
5. Execute.
6. Verify each important step.
7. Recover from recoverable errors.
8. Present the result and a concise action summary.

## 7. Success Criteria
A phase is successful only when:
- The intended functionality works on the target environment.
- Failure cases are tested.
- Logs are understandable.
- No known critical security issue is introduced.
- The feature is documented.
- The previous phase remains functional.

## 8. Quality Requirements
- Modular
- Testable
- Observable
- Secure by default
- Recoverable
- Maintainable by one developer with AI assistance
- Clear separation between reasoning, planning, tools, execution, and verification
