# AI Computer Employee — System Architecture

## 1. Architecture Style
Use a modular agent architecture with strict boundaries between:
- User Interface
- Agent/Brain
- Planner
- Tool Registry
- Execution Layer
- Computer Control
- Observation/Vision
- Verification
- Memory
- Security
- Logging
- Testing

No module should secretly perform responsibilities belonging to another module.

## 2. High-Level Flow

User
→ UI
→ Task Intake
→ Brain
→ Planner
→ Policy/Security Check
→ Tool Selection
→ Executor
→ Computer/Tool
→ Observation
→ Verifier
→ Recovery if needed
→ Result
→ User

## 3. Core Components

### Brain
Converts user intent into structured task information. It should not directly control the mouse, keyboard, filesystem, or external services.

### Planner
Turns a task into explicit steps and dependencies.

### Policy/Security Layer
Determines whether an action is allowed, requires confirmation, or must be blocked.

### Tool Registry
Provides a controlled list of available tools and their capabilities.

### Executor
Runs approved actions. It must report success/failure rather than assume success.

### Computer Control
Handles keyboard, mouse, windows, applications, and other computer interactions.

### Observation
Captures relevant application/screen state.

### Verifier
Checks whether the intended state/result was actually achieved.

### Recovery
Handles recoverable failures with bounded retries. It must not loop indefinitely.

### Memory
Stores only useful, permitted information such as preferences, project context, and task history.

### Audit/Logging
Records important actions, decisions, failures, approvals, and outcomes without exposing secrets.

## 4. Design Rules
1. Prefer small modules over giant files.
2. Use explicit interfaces between modules.
3. Keep provider-specific AI code isolated.
4. Keep OS-specific automation isolated.
5. Never let an LLM directly execute arbitrary system commands without policy controls.
6. Every important external action must be observable and verifiable.
7. All automation should have a stop/emergency mechanism.
8. New capabilities must be added as tools or modules, not by modifying unrelated core logic.

## 5. Failure Model
Every action should have:
- Input validation
- Permission check
- Execution
- Observation
- Verification
- Error classification
- Recovery or safe stop

## 6. Human-in-the-Loop
The user remains the final authority for high-impact actions. The architecture must support approval before:
- Deletion
- Irreversible changes
- External communication
- Purchases
- Credential/account changes
- Software installation
- Sensitive data transfer
