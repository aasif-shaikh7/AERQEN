# AI Computer Employee — One-Person Development & Testing Process

## 1. Development Model
There is one human developer and AI-assisted engineering.

Human:
- Defines goals
- Provides decisions
- Runs tests
- Reports actual results
- Approves changes

AI:
- Explains
- Designs
- Generates code
- Reviews
- Suggests tests
- Helps debug

## 2. Golden Rule
Never move to the next phase because the code "looks correct."

Move forward only after testing the current phase.

## 3. Development Loop

```text
Requirement
→ Design
→ Small implementation
→ Run
→ Observe
→ Test
→ Fix
→ Regression test
→ Document
→ Accept
→ Next task
```

## 4. Test Levels

### Unit Tests
Test individual functions/classes.

### Integration Tests
Test communication between modules.

### System Tests
Test a complete user workflow.

### Security Tests
Test blocked/unsafe behavior.

### Regression Tests
Re-run old tests after changes.

## 5. Manual Testing
Because the developer is non-programming-focused, every phase must include simple manual test instructions:
- What to run
- What to click/type
- Expected result
- What counts as failure
- What screenshot/log to send to the AI

## 6. Bug Reporting Format

```text
Phase:
Feature:
What I did:
Expected:
Actual:
Error message:
Screenshot:
Environment:
What changed before the error:
```

Never summarize an error if the original error message is available. Send the original text/screenshot.

## 7. AI Debugging Rule
When an error is reported, AI must:
1. Identify likely cause.
2. Explain it simply.
3. Propose the smallest safe fix.
4. State which files change.
5. Provide the updated code/change.
6. Provide exact test steps.
7. Identify possible regression risks.

## 8. Acceptance Criteria
Every feature must have explicit acceptance criteria before implementation.

## 9. Versioning
Use small, traceable commits such as:
- `phase-1-core`
- `phase-1-fix-task-validation`
- `phase-2-tool-registry`

## 10. No Fake Testing
Neither human nor AI may claim:
- "tested"
- "verified"
- "works"
unless the test was actually performed.

## 11. Recovery
If a change breaks a previously working feature:
- Stop adding new functionality.
- Reproduce.
- Identify regression.
- Restore or fix.
- Re-run previous tests.
- Only then continue.
